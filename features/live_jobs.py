import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_API_KEY = os.getenv("serpapi_api_key")
JOOBLE_API_KEY = os.getenv("jobble_api_key")

if not SERPAPI_API_KEY:
    raise ValueError("Missing SERPAPI_API_KEY in environment")

if not JOOBLE_API_KEY:
    raise ValueError("Missing JOOBLE_API_KEY in environment")


def fetch_jobs_from_google(role_location: str) -> list:
    """Fetch live job listings from Google Jobs via SerpApi."""
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

    response = requests.get("https://serpapi.com/search", params=params)

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
        for job in jobs[:5]
    ]


def fetch_jobs_from_jooble(role_location: str) -> list:
    """Search for job vacancies on Jooble."""
    if "," in role_location:
        role, location = [x.strip() for x in role_location.split(",", 1)]
    else:
        role = role_location.strip()
        location = "India"

    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    headers = {"Content-Type": "application/json"}
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
    """Remove duplicate jobs based on title, company, and location."""
    seen = set()
    unique = []

    for job in jobs:
        key = (job.get("title"), job.get("company"), job.get("location"))
        if key not in seen:
            seen.add(key)
            unique.append(job)

    return unique


def fetch_jobs_smart(role_location: str) -> list:
    """Fetch jobs from both sources and remove duplicates."""
    combined_jobs = []

    print("🔎 Fetching from Jooble...")
    combined_jobs.extend(fetch_jobs_from_jooble(role_location))

    print("🔎 Fetching from Google Jobs...")
    combined_jobs.extend(fetch_jobs_from_google(role_location))

    return dedupe_jobs(combined_jobs)


def run_job_agent(query: str) -> list:
    """
    FastAPI-safe wrapper.
    Always returns list[dict].
    """
    try:
        return fetch_jobs_smart(query)
    except Exception as e:
        print(f"❌ Job fetch failed: {e}")
        return []


if __name__ == "__main__":
    query = "Software Developer, India"
    jobs = run_job_agent(query)

    import json
    print(json.dumps(jobs, indent=2))
