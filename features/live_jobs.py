import os
import requests
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_ollama import OllamaLLM
from langchain.agents import create_agent


load_dotenv()

SERPAPI_API_KEY = os.getenv("serpapi_api_key")
JOOBLE_API_KEY = os.getenv("jobble_api_key")

if not SERPAPI_API_KEY:
    raise ValueError("Missing serpapi_api_key in .env")

if not JOOBLE_API_KEY:
    raise ValueError("Missing jobble_api_key in .env")


@tool
def fetch_jobs_from_google(role_location: str) -> list:
    """Fetch live job listings from Google Jobs via SerpApi using a 'role, location' string."""
    if "," in role_location:
        role, location = [x.strip() for x in role_location.split(",", 1)]
    else:
        role = role_location.strip()
        location = ""

    query = f"{role} jobs {location}" if location else f"{role} jobs"

    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "api_key": SERPAPI_API_KEY
    }

    response = requests.get(
        "https://serpapi.com/search?engine=google_jobs",
        params=params
    )

    if response.status_code != 200:
        return []

    jobs = response.json().get("jobs_results", [])

    return [
        {
            "title": job.get("title", "N/A"),
            "company": job.get("company_name", "N/A"),
            "location": job.get("location", "N/A"),
            "link": job.get("apply_options", [{}])[0].get("link", "#")
        }
        for job in jobs
    ]


@tool
def fetch_jobs_from_jooble(role_location: str | list) -> list:
    """Search for job vacancies on Jooble. Defaults to India if no location is provided."""
    if isinstance(role_location, list):
        role_location = ", ".join(role_location)

    if "," in role_location:
        role, location = [x.strip() for x in role_location.split(",", 1)]
    else:
        role = role_location.strip()
        location = "India"

    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    headers = {"Content-type": "application/json"}
    payload = {"keywords": role, "location": location, "page": 1}

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        jobs = response.json().get("jobs", [])

        return [
            {
                "title": job.get("title", "N/A"),
                "company": job.get("company", "N/A"),
                "location": job.get("location", "N/A"),
                "link": job.get("link", "#")
            }
            for job in jobs[:5]
        ]

    except Exception as e:
        print(f"❌ Jooble error: {e}")
        return []



def dedupe_jobs(jobs: list) -> list:
    seen = set()
    unique = []

    for job in jobs:
        key = (job.get("title"), job.get("company"), job.get("location"))
        if key not in seen:
            seen.add(key)
            unique.append(job)

    return unique


@tool
def fetch_jobs_smart(role_location: str) -> list:

    """Combined tool that searches both Google and Jooble, then removes duplicates."""

    combined_jobs = []

    print("🔎 Fetching from Jooble...")
    combined_jobs.extend(fetch_jobs_from_jooble.invoke(role_location))

    print("🔎 Fetching from Google Jobs...")
    combined_jobs.extend(fetch_jobs_from_google.invoke(role_location))

    return dedupe_jobs(combined_jobs)



llm = OllamaLLM(
    model="llama3",
    temperature=0
)

tools = [fetch_jobs_smart]


agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a professional job search assistant. Provide details in JSON format."
)

def run_job_agent(query: str) -> list:
    """
    Safe wrapper for FastAPI.
    Always returns list[dict].
    """
    try:
        result = agent.invoke({"input": query})

        if isinstance(result, dict):
            output = result.get("output", [])
            if isinstance(output, list):
                return output

    except Exception as e:
        print(f"Agent invoke failed, falling back to direct tool call: {e}")

    try:
        jobs = fetch_jobs_smart.invoke(query)
        if isinstance(jobs, list):
            return jobs
    except Exception as e:
        print(f"Fallback fetch_jobs_smart failed: {e}")

    return []



if __name__ == "__main__":
    query = "Software Developer, India"
    print("\n🤖 Agent Running...\n")
    jobs = run_job_agent(query)
    import json
    print(json.dumps(jobs, indent=2))
