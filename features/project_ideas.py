import json
import os
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage




os.environ["GEMINI_API_KEY"] = os.getenv("gemini_api_key")

model = init_chat_model("google_genai:gemini-2.5-flash")


def generate_project_ideas(role, job_description):
    # """Generates structured project ideas and returns a list of dicts."""
    prompt = f"""
    Act as an expert AI career mentor. Based on the job role "{role}" and the following job description:

    {job_description}

    Generate exactly 5 practical project ideas that align with the role.  

    ✅ Output strictly as a **single valid JSON array** of 5 objects.  
    Each object must contain the following keys:  
    - "title": Short and clear project title  
    - "objective": One-sentence description of the project's purpose  
    - "tools": Tools, libraries, or frameworks to be used  
    - "skills": Skills the user will learn or demonstrate  

    Example format:
    [
      {{
        "title": "Project Title",
        "objective": "Project objective here",
        "tools": "List of tools/frameworks",
        "skills": "List of skills gained"
      }}
    ]
    """

    try:
        response = model.invoke([
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=prompt)
        ])

        raw_output_from_llm = response.content

        
        json_start_index = raw_output_from_llm.find('[')
        
        json_end_index = raw_output_from_llm.rfind(']')
        
        if json_start_index == -1 or json_end_index == -1:
            print("Error: Valid JSON array not found in the LLM response.")
            return [] 

        json_string = raw_output_from_llm[json_start_index : json_end_index + 1]
        
        parsed_projects = json.loads(json_string)

        # return f"{response['message']['content']}"
        return parsed_projects


    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"

# project_ideas = generate_project_ideas("Data Scientist", "Experience with Python, Machine Learning, Data Analysis, and statistical modeling.")

# print(project_ideas)
