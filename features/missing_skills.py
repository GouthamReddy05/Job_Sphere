import io
# import pdfplumber
from PyPDF2 import PdfReader
# from pdfminer.high_level import extract_text
import docx
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
import ollama

load_dotenv()

hf_api_key = os.getenv('huggingface_api_key')
if hf_api_key:
    client = InferenceClient(token=hf_api_key)
else:
    client = InferenceClient() 


import io

# def extract_text_from_file(file_source):
#     """
#     Reads a document from either a file path or a file-like object.

#     Args:
#         file_source: A file path (str) or a file-like object.

#     Returns:
#         The extracted text as a string.
#     """
#     text = ""
#     filename = ""

#     if hasattr(file_source, 'read'):

#         filename = file_source.filename
        
#         content_stream = io.BytesIO(file_source.read())
        
#         file_source.seek(0)

#     elif isinstance(file_source, str):

#         if not os.path.exists(file_source):
#             raise FileNotFoundError(f"No such file: '{file_source}'")
#         filename = file_source
#         content_stream = file_source 

#     else:
#         raise TypeError("Input must be a file path (string) or a file-like object.")

#     if filename.lower().endswith('.pdf'):
#         with pdfplumber.open(content_stream) as pdf:
#             for page in pdf.pages:
#                 page_text = page.extract_text()
#                 if page_text:
#                     text += page_text + "\n"
    
#     elif filename.lower().endswith('.docx'):
#         document = docx.Document(content_stream)
#         for para in document.paragraphs:
#             text += para.text + "\n"
    
#     else:
#         raise ValueError("Unsupported file type. Please provide a PDF or DOCX file.")

#     return text



def extract_text_from_file(file_source):
    """
    Reads a document from either a file path or a file-like object.

    Args:
        file_source: A file path (str) or a file-like object.

    Returns:
        The extracted text as a string.
    """
    text = ""
    filename = ""

    if hasattr(file_source, 'read'):
        # It's a file-like object (e.g., uploaded file in Flask)
        filename = getattr(file_source, 'filename', 'uploaded_file')
        content_stream = io.BytesIO(file_source.read())
        file_source.seek(0)

    elif isinstance(file_source, str):
        # It's a file path
        if not os.path.exists(file_source):
            raise FileNotFoundError(f"No such file: '{file_source}'")
        filename = file_source
        content_stream = file_source  # Keep path for PyPDF2/docx

    else:
        raise TypeError("Input must be a file path (string) or a file-like object.")

    # --- Handle PDF ---
    if filename.lower().endswith('.pdf'):
        if isinstance(content_stream, str):  # file path
            reader = PdfReader(content_stream)
        else:  # file-like
            reader = PdfReader(content_stream)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # --- Handle DOCX ---
    elif filename.lower().endswith('.docx'):
        if isinstance(content_stream, str):  # file path
            document = docx.Document(content_stream)
        else:  # file-like
            document = docx.Document(content_stream)
        for para in document.paragraphs:
            text += para.text + "\n"

    else:
        raise ValueError("Unsupported file type. Please provide a PDF or DOCX file.")

    return text




# print(extract_ordered_text_pdf("Resume.pdf"))

def send_text_to_llm(text):
    
    prompt = f"""
    You are an AI that organizes resume text into structured sections.

    Task:
    - Organize the resume text into these exact sections:
      - Name and Contact Information
      - Introduction/Summary
      - Experience
      - Projects
      - Education
      - Skills
      - Certifications
    - If a section uses a different title (e.g., "Profile", "Career Overview"), map it to the most relevant one.
    - If any section is missing, still include it with an empty string ("").

    Input Resume Text:
    {text}

    Output:
    Return ONLY valid JSON in this format:
    {{
      "Name and Contact Information": "",
      "Introduction/Summary": "",
      "Experience": "",
      "Projects": "",
      "Education": "",
      "Skills": "",
      "Certifications": ""
    }}
    """


    # try:
    #     response = client.chat_completion(model="meta-llama/Llama-3.3-70B-Instruct", messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": prompt}
    #     ])

    #     return f"{response.choices[0].message.content}"


    # except Exception as e:
    #     return f"⚠️ Error generating response: {str(e)}"

    try:
        response = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        return f"{response['message']['content']}"


    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"
    

def retrieve_skills(text):
    prompt = f"""
    You are an AI career assistant.
    Task: you are given a resume text. Extract and list all the skills mentioned in the resume in a correct order.
    Input: {text}
    Output: A list of skills in JSON format and do not seperate combine all types of skills into list with numbering without double quotes.
    """
    # try:
    #     response = client.chat_completion(model="meta-llama/Llama-3.3-70B-Instruct", messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": prompt}
    #     ])

    #     return f"{response.choices[0].message.content}"
    
    # except Exception as e:
    #     return f"⚠️ Error generating response: {str(e)}"

    try:
        response = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        return f"{response['message']['content']}"


    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"
    
    

def generate_missing_skills(role, candidate_skills):
    prompt = f"""
You are an AI career coach specializing in **skill gap analysis**. Your task is to analyze the gap between a target job role and a candidate's existing skills.

### Instructions
1. Use a fixed and standard list of essential skills required for the target job role. Do not invent or add irrelevant skills.
2. Compare these required skills with the candidate's provided skills.
3. List only the missing crucial skills that the candidate does not already have.
4. Categorize the missing skills into exactly these three categories (do not add or remove categories):
   - Core Technical Skills
   - Programming Languages/Frameworks
   - Tools & Platforms
5. If no skills are missing in a category, return an empty list `[]`.
6. Output must be only a single valid JSON object. Do not include explanations, markdown, or extra text.
7. Do not generate unnecessary skills — only include those truly required for the role.

## Input Data
- **Target Job Role:** "{role}"
- **Candidate's Existing Skills:** {candidate_skills}

## Example of a Perfect Output
{{
  "Core Technical Skills": ["Data Structures", "System Design"],
  "Programming Languages/Frameworks": ["Go", "React Native"],
  "Tools & Platforms": ["Kubernetes", "Docker", "AWS"]
}}
"""


    # try:
    #     response = client.chat_completion(model="meta-llama/Llama-3.3-70B-Instruct", messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": prompt}
    #     ])

    #     return f"{response.choices[0].message.content}"


    # except Exception as e:
    #     return f"⚠️ Error generating response: {str(e)}"

    try:
        response = ollama.chat(model="llama3", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])

        return f"{response['message']['content']}"


    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"



# text = extract_text_from_file("Resume.pdf")
# print(text)

# structured_text = send_text_to_llm(text)
# print(structured_text)

# skills = retrieve_skills(structured_text)
# print(skills)

# missing_skills = generate_missing_skills("Machine Learning engineer", skills)
# print(missing_skills)
