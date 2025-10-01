# from langchain.agents import initialize_agent
# from langchain.agents.agent_types import AgentType
# from langchain.tools import tool
# from langchain_community.llms import Ollama
# import requests
# from dotenv import load_dotenv
# import os
# import re



# load_dotenv()

# JOOBLE_API_KEY = os.getenv("jobble_api_key")

# @tool
# def fetch_jobs_from_jooble(role_location: str) -> str:
#     """
#     Fetch job listings from Jooble API based on role and location.
#     Returns a formatted string with job titles, companies, locations, and links.
#     """
#     if "," in role_location:
#         role, location = [x.strip() for x in role_location.split(",", 1)]
#     else:
#         role = role_location.strip()
#         location = ""
    
#     url = f"https://jooble.org/api/{JOOBLE_API_KEY}"

#     headers = {"Content-type": "application/json"}
#     payload = {"keywords": role, "location": location, "page": 1, "jobs_per_page": 5}
    
#     response = requests.post(url, json=payload, headers=headers)
#     if response.status_code != 200:
#         return f"❌ Error: {response.status_code} {response.reason}"
    
#     jobs = response.json().get("jobs", [])
#     if not jobs:
#         return "No jobs found."
    
#     result_text = ""
#     for job in jobs:
#         title = job.get("title", "N/A")
#         company = job.get("company", "N/A")
#         loc = job.get("location", "N/A")
#         link = job.get("link", "#")
#         result_text += f"🔹 {title} – {company}\n📍 {loc}\n🔗 {link}\n\n"
    
#     return result_text.strip()


# # Initialize LLM
# llm = Ollama(model="llama3")

# tools = [fetch_jobs_from_jooble]

# agent = initialize_agent(
#     tools,
#     llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
#     max_iterations=3,
#     handle_parsing_errors=True
# )

# # Run agent
# role_location = "Software Developer, India"
# response = agent.invoke(role_location)


# # Extract and print only the job links from the output
# if isinstance(response, dict) and 'output' in response:
#     output_text = response['output']
# else:
#     output_text = str(response)
# links = re.findall(r'https?://[^\s]+', output_text)
# print("\nJob Links:")
# for link in links:
#     print(link)

# In files/live_jobs/jobble_agent.py

from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from langchain_community.llms import Ollama
import requests
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()
JOOBLE_API_KEY = os.getenv("jobble_api_key")

# In files/live_jobs/jobble_agent.py

# In files/live_jobs/jobble_agent.py

@tool
# ✅ Correct Signature: Accepts string OR list, ALWAYS returns a list
def fetch_jobs_from_jooble(role_location: str | list) -> list:
    """
    Fetches job listings from the Jooble API and returns a LIST of job objects.
    Defaults to India if no location is provided.
    """
    if isinstance(role_location, list):
        role_location = ", ".join(role_location)
    
    if "," in role_location:
        role, location = [x.strip() for x in role_location.split(",", 1)]
    else:
        role = role_location.strip()
        location = ""

    if not location or location.lower() == 'none':
        location = "India"
    
    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    headers = {"Content-type": "application/json"}
    payload = {"keywords": role, "location": location, "page": 1}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        jobs_data = response.json().get("jobs", [])
        if not jobs_data:
            return []

        results_list = []
        for job in jobs_data[:5]:
            job_details = {
                "title": job.get("title", "N/A"),
                "company": job.get("company", "N/A"),
                "location": job.get("location", "N/A"),
                "link": job.get("link", "#")
            }
            results_list.append(job_details)
        
        return results_list

    except Exception as e:
        print(f"❌ An error occurred in the tool: {e}")
        return [] # ✅ ALWAYS return a list, even on error
    

def run_job_agent(query: str) -> list:
    """
    This function now acts as a direct, simple wrapper for our tool.
    It calls the fetch_jobs_from_jooble function and returns its result.
    """
    print(f"--- Calling the job tool directly with query: {query} ---")
    
    job_list = fetch_jobs_from_jooble.invoke(query)
    
    return job_list

if __name__ == '__main__':
    print("--- Testing jobble_agent.py directly ---")
    test_query = "Software Developer, India"
    
    # agent_result is now a list of dictionaries
    agent_result = run_job_agent(test_query)
    
    print("\n--- Agent's Final Answer (structured list) ---")
    import json
    print(json.dumps(agent_result, indent=2))

    # ✅ FIX: Loop through the list to get the links
    print("\n--- Extracted Job Links ---")
    if isinstance(agent_result, list):
        for job in agent_result:
            # Access the 'link' key from each dictionary
            print(job.get('link', 'No link found'))