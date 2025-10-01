import ollama
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

hf_api_key = os.getenv('huggingface_api_key')

client = InferenceClient("meta-llama/Llama-3-70B-Instruct", token=hf_api_key)




def generate_interview_questions(role, skills):
    """Generates interview questions and returns a clean list of strings."""
    skills_str = ", ".join(skills)
    prompt = f"""
    You are an expert AI interview question generator. For the job role "{role}" with skills "{skills_str}", generate 20 relevant interview questions in four categories: DSA & Core CS, Technical Skills, Role-Specific, and HR.

    **CRITICAL OUTPUT FORMAT:**
    You MUST return a single JSON object with one key "questions", containing a flat array of all 20 question strings.

    Example: {{ "questions": ["Question 1?", "Question 2?"] }}
    """
    messages = [{"role": "user", "content": prompt}]
    
    # try:
    #     response = client.chat_completion(
    #         messages=messages, model="meta-llama/Llama-3-70B-Instruct", response_format={"type": "json_object"}
    #     )
    #     response_content = response.choices[0].message.content
    #     data = json.loads(response_content)
        
    #     return data.get("questions", [])
    # except Exception as e:
    #     print(f"⚠️ LLM Error (interview_questions): {e}")
    #     return ["Could not generate interview questions at this time."]

    try:
        response = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        return f"{response['message']['content']}"


    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"


# print(generate_interview_questions("Data Scientist", "Python, Machine Learning, Data Analysis"))
