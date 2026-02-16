from fastapi import FastAPI, HTTPException, Response, Depends, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import re
import json
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import hashlib
import os

# Import database and auth (Assuming these files exist and are correct)
from database import db
from auth import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES, normalize_password

# Import Features
from features.missing_skills import send_text_to_llm, retrieve_skills, generate_missing_skills, extract_text_from_file, extract_json
from features.Job_match_analysis import calculate_ats_score
from features.project_ideas import generate_project_ideas
from features.interview_prep import generate_interview_questions
from features.live_jobs import run_job_agent

import PyPDF2
import docx
from fastapi.exceptions import RequestValidationError

app = FastAPI()


origins = [
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:5001",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5001",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_collection = db["users"]

# --- Pydantic Models ---

class UserSignup(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ATSAnalysisRequest(BaseModel):
    job_role: str
    job_description: str
    resume_text: str

class MissingSkillsRequest(BaseModel):
    job_role: str
    resume_text: str

class ProjectIdeasRequest(BaseModel):
    job_role: str
    job_description: str

class InterviewPrepRequest(BaseModel):
    job_role: str
    resume_text: Optional[str] = None

class JobMatchRequest(BaseModel):
    job_role: str
    location: str


def check_file(text: str) -> bool:
    """Checks if the text contains at least 3 common resume sections."""

    keywords = [
        "education",
        "experience",
        "skills",
        "projects",
        "certifications",
        "summary",
        "contact",
        "university",
        "college",
        "degree"
    ]

    text_lower = text.lower()

    found_keywords = 0
    for keyword in keywords:
        if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
            found_keywords += 1

    return found_keywords >= 3

# async def extract_text_from_upload_file(file: UploadFile):
#     """Extracts text from a PDF or DOCX file object."""
#     filename = file.filename
#     text = ""
#     try:
#         content = await file.read()
#         file_stream = io.BytesIO(content)

#         if filename.endswith('.pdf'):
#             pdf_reader = PyPDF2.PdfReader(file_stream)
#             for page in pdf_reader.pages:
#                 text += page.extract_text()
#         elif filename.endswith('.docx'):
#             document = docx.Document(file_stream)
#             for para in document.paragraphs:
#                 text += para.text + '\n'
#         else:
#             return None, "Unsupported file type. Please upload a PDF or DOCX."
#     except Exception as e:
#         return None, f"Error processing file: {str(e)}"
    
#     return text, None


def normalize_password(password: str) -> str:
    """
    Converts any-length password into a fixed-length secure hash
    before bcrypt.
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# --- Auth Endpoints ---

@app.post("/api/auth/signup")
async def signup(user: UserSignup):
    try:
        existing_user = await user_collection.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        hashed_password = normalize_password(user.password)

        new_user = {"email": user.email, "password": hashed_password}
        result = await user_collection.insert_one(new_user)
        
        return {"message": "User created successfully", "user_id": str(result.inserted_id)}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/api/auth/login")
async def login(response: Response, user: UserLogin):
    start_user = await user_collection.find_one({"email": user.email})
    hashed_password = normalize_password(user.password)

    if not start_user or hashed_password != start_user["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"user_id": str(start_user["_id"])})
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False
    )
    return {"message": "Login successful"}

@app.post("/api/auth/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logout successful"}

@app.get("/api/auth/me")
async def get_me(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}



@app.post('/api/process-resume')
def process_resume(
    resume: UploadFile = File(...),
    jobRole: str = Form(...),
    jobDescription: str = Form(default=""),
    location: str = Form(...),
    experience: str = Form(...)
):
    try:
        if not resume.filename:
             raise HTTPException(status_code=400, detail="No selected file")

        resume_text = extract_text_from_file(resume)
        
    except Exception as e:
        print(f"ERROR in process_resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    if not check_file(resume_text):
        error_message = 'The file you gave does not seem to be a valid resume. Please upload a proper resume file.'
        raise HTTPException(status_code=400, detail=error_message)

    return {
        'message': 'Resume processed successfully',
        'resume_text': resume_text,
        'job_role': jobRole,
        'job_description': jobDescription,
        'location': location,
        'experience': experience
    }

@app.post('/api/analyze/ats-score')
async def analyze_ats_score(request: ATSAnalysisRequest):
    ats_score = calculate_ats_score(request.resume_text, request.job_description)
    
    mock_result = { 
        'title': 'Job Match Analysis', 
        'score': ats_score, 
        'details': [ 'Strong keyword optimization', 'Excellent formatting', 'Clear section headers' ] 
    }
    return mock_result

from fastapi import HTTPException
import json

@app.post('/api/analyze/missing-skills')
async def analyze_missing_skills(request: MissingSkillsRequest):
    try:
        structured_text = send_text_to_llm(request.resume_text)

        skills = retrieve_skills(structured_text)
        clean_skills = extract_json(skills)
        print(f"Extracted Skills: {skills}")

        try:
            skill_list = json.loads(clean_skills)
        except json.JSONDecodeError:
            skill_list = []

        missing_skills = generate_missing_skills(request.job_role, skill_list)
        print(f"LLM Missing Skills Response: {missing_skills}")

        try:
            structured_response = extract_json(missing_skills)
            structured_response = json.loads(structured_response)
        except json.JSONDecodeError:
            raise ValueError("LLM returned invalid JSON for missing skills")

        flat_list = []
        for category_skills in structured_response.values():
            if isinstance(category_skills, list):
                flat_list.extend(category_skills)

        return {
            "title": "Missing Skills Analysis",
            "skills": flat_list
        }

    except Exception as e:
        print("SERVER ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# @app.post('/api/analyze/missing-skills')
# async def analyze_missing_skills(request: MissingSkillsRequest):
#     structured_text = send_text_to_llm(request.resume_text)
#     skills = retrieve_skills(structured_text)
#     skill_list = json.loads(skills) if skills else []
#     missing_skills = generate_missing_skills(request.job_role, skill_list)

#     flat_list = []
#     try:
#         structured_response = json.loads(missing_skills) 
#         for category_skills in structured_response.values():
#             if isinstance(category_skills, list):
#                 flat_list.extend(category_skills)
#     except (json.JSONDecodeError, TypeError) as e:
#         print(f"Error processing AI response: {e}")
#         pass
    
#     mock_result = { 
#         'title': 'Missing Skills Analysis', 
#         'skills': flat_list 
#     }
#     return mock_result

@app.post('/api/analyze/project-ideas')
async def analyze_project_ideas(request: ProjectIdeasRequest):
    # print("\n--- 1. PROJECT IDEAS ROUTE TRIGGERED ---")
    project_list = []
    
    try:
        project_list = generate_project_ideas(request.job_role, request.job_description)
    except Exception as e:
        print(f"!!!!!! AN ERROR OCCURRED IN THE ROUTE: {e} !!!!!!")
        project_list = [] 

    result = {
        'title': 'Project Ideas for Your Profile',
        'projects': project_list
    }
    return result



@app.post('/api/analyze/interview-prep')
async def analyze_interview_prep(request: InterviewPrepRequest):

    structured_text = send_text_to_llm(request.resume_text)
    skills = retrieve_skills(structured_text)

    ques = generate_interview_questions(request.job_role, skills)

    json_start_index = ques.find('{')
    json_end_index = ques.rfind('}')
        
    if json_start_index == -1 or json_end_index == -1:
        raise HTTPException(status_code=500, detail='Could not parse LLM response')

    json_string = ques[json_start_index : json_end_index + 1]
    
    try:
        parsed_data = json.loads(json_string)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail='Invalid JSON from LLM')
    
    mock_result = { 
        'title': 'Interview Preparation', 
        'questions': parsed_data.get('questions', [])
    }
    return mock_result


@app.post('/api/analyze/job-matches')
async def analyze_job_matches(request: JobMatchRequest):
    try:
        query = f"{request.job_role}, {request.location}"

        job_list = run_job_agent(query)

        if not isinstance(job_list, list):
            job_list = []

        return {
            'title': f'Live Job Matches in {request.location}',
            'jobs': job_list
        }

    except Exception as e:
        print(f"Job Match Error: {e}")
        raise HTTPException(
            status_code=500,
            detail='Error finding job matches'
        )


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
build_path = os.path.join(BASE_DIR, "frontend", "resume-analyzer-app", "build")
if os.path.isdir(build_path):
    app.mount("/", StaticFiles(directory=build_path, html=True), name="static")


@app.get("/", include_in_schema=False)
def serve_react():
    return FileResponse(os.path.join(build_path, "index.html"))