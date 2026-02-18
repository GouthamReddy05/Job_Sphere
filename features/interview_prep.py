import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage


load_dotenv()


# hf_api_key = os.getenv('huggingface_api_key')

# client = InferenceClient("meta-llama/Llama-3-70B-Instruct", token=hf_api_key)

os.environ["GEMINI_API_KEY"] = os.getenv("gemini_api_key")

model = init_chat_model("google_genai:gemini-2.5-flash")



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
        response = model.invoke([
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=prompt)
        ])

        return response.content

    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"



