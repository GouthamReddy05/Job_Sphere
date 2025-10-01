import io
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import PyPDF2
import docx
import re
import os
from features.missing_skills import extract_text_from_file, send_text_to_llm, retrieve_skills, generate_missing_skills
from features.Job_match_analysis import calculate_ats_score
from features.project_ideas import generate_project_ideas
from features.interview_prep import generate_interview_questions
from features.live_jobs.jobble_agent import run_job_agent
import json

app = Flask(__name__, static_folder="frontend/resume-analyzer-app/build", static_url_path="/")
CORS(app)

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, "index.html")

# --- Helper Function to Validate Resume Content ---
def check_file(text):
    """Checks if the text contains at least 5 common resume keywords."""
    keywords = ["education", "experience", "skills", "projects", "certifications", "summary", "contact", "technical skills", "university", "college", "degree"]
    keyword_set = set(keywords)
    
    found_keywords = set()
    for word in text.lower().split():
        if word in keyword_set:
            found_keywords.add(word)
            
    if len(found_keywords) >= 5:
        return True
    return False

# --- Helper Function to Extract Text ---
# def extract_text_from_file(file):
#     """Extracts text from a PDF or DOCX file object."""
#     filename = file.filename
#     text = ""
#     try:
#         if filename.endswith('.pdf'):
#             pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
#             for page in pdf_reader.pages:
#                 text += page.extract_text()
#         elif filename.endswith('.docx'):
#             document = docx.Document(io.BytesIO(file.read()))
#             for para in document.paragraphs:
#                 text += para.text + '\n'
#         else:
#             return None, "Unsupported file type. Please upload a PDF or DOCX."
#     except Exception as e:
#         return None, f"Error processing file: {str(e)}"
    
#     return text, None

# --- API Endpoints ---

@app.route('/api/process-resume', methods=['POST'])
def process_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file found'}), 400

    file = request.files['resume']
    job_role = request.form.get('jobRole', '')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        resume_text = extract_text_from_file(file)
        # if error:
        #     return jsonify({'error': error}), 500

        if not check_file(resume_text):
            error_message = 'The file you gave does not seem to be a valid resume. Please upload a proper resume file.'
            return jsonify({'error': error_message}), 400

        # print("Extracted Resume Text:", resume_text[:500])

        return jsonify({
            'message': 'Resume processed successfully',
            'resume_text': resume_text,
            'job_role': job_role
        })



@app.route('/api/analyze/ats-score', methods=['POST'])
def analyze_ats_score():
    data = request.get_json()
    job_role = data.get('job_role')
    job_description = data.get('job_description') 
    
    resume_text = data.get('resume_text', '')

    ats_score = calculate_ats_score(resume_text, job_description)
    
    mock_result = { 
        'title': 'Job Match Analysis', 
        'score': ats_score, 
        'details': [ 'Strong keyword optimization', 'Excellent formatting', 'Clear section headers' ] 
    }
    return jsonify(mock_result)



@app.route('/api/analyze/missing-skills', methods=['POST'])
def analyze_missing_skills():
    data = request.get_json()
    job_role = data.get('job_role')
    resume_text = data.get('resume_text', '')

    structured_text = send_text_to_llm(resume_text)
    skills = retrieve_skills(structured_text)
    missing_skills = generate_missing_skills(job_role, skills)

    # if missing_skills is None:
    #     missing_skills = []
    flat_list = []

    try:
        structured_response = json.loads(missing_skills) 
        
        for category_skills in structured_response.values():
            if isinstance(category_skills, list):
                flat_list.extend(category_skills)

    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error processing AI response: {e}")
        pass
    mock_result = { 
        'title': 'Missing Skills Analysis', 
        'skills': flat_list 
    }
    return jsonify(mock_result)


# @app.route('/api/analyze/project-ideas', methods=['POST'])
# def analyze_project_ideas():
#     data = request.get_json()
#     job_role = data.get('job_role')
#     job_description = data.get('job_description') 

#     project_ideas = generate_project_ideas(job_role, job_description)

#     project_ideas = parse_project_ideas(project_ideas)

#     mock_result = { 
#         'title': 'Project Ideas for Your Profile', 
#         'projects': project_ideas
#     }

#     return jsonify(mock_result)

@app.route('/api/analyze/project-ideas', methods=['POST'])
def analyze_project_ideas():
    print("\n--- 1. PROJECT IDEAS ROUTE TRIGGERED ---")
    project_list = []
    
    try:
        data = request.get_json()
        job_role = data.get('job_role')
        job_description = data.get('job_description')

        
        project_list = generate_project_ideas(job_role, job_description)

    except Exception as e:
        print(f"!!!!!! AN ERROR OCCURRED IN THE ROUTE: {e} !!!!!!")
        project_list = [] 

    # Prepare the final JSON to be sent to the frontend
    result = {
        'title': 'Project Ideas for Your Profile',
        'projects': project_list
    }
    
    return jsonify(result)

@app.route('/api/analyze/interview-prep', methods=['POST'])
def analyze_interview_prep():

    data = request.get_json()
    job_role = data.get('job_role')
    resume_text = data.get('resume_text')
    # structured_text = send_text_to_llm(resume_text)
    # skills = retrieve_skills(structured_text)
    skills = "Python, Machine Learning, Data Analysis"

    ques = generate_interview_questions(job_role, skills)

    json_start_index = ques.find('{')
    json_end_index = ques.rfind('}')
        
    if json_start_index == -1 and json_end_index == -1:
        return jsonify({'error': 'Could not parse LLM response'}), 500

        # 2. Extract the JSON part of the string
    json_string = ques[json_start_index : json_end_index + 1]
    # print("Questions : ", json_string)

        
        # 3. Convert the JSON string into a Python dictionary
    parsed_data = json.loads(json_string)
    
    # print("Generated questions:", ques)

    mock_result = { 
        'title': 'Interview Preparation', 
        'questions': parsed_data.get('questions', [])
    }
    return jsonify(mock_result)



@app.route('/api/analyze/job-matches', methods=['POST'])
def analyze_job_matches():
    try:
        data = request.get_json()
        job_role = data.get('job_role')
        location = data.get('location')
        location = "india"
        
        query = f"{job_role}, {location}"

        # url_pattern = re.compile(r"https?://[^\s]+")
        # job_links = url_pattern.findall(agent_output_string)
        job_list = run_job_agent(query)

        
        result = { 
            'title': f'Live Job Matches in {location}', 
            'jobs': job_list
        }
        return jsonify(result)

    except Exception as e:
        print(f"!!!!!! AN ERROR OCCURRED IN THE ROUTE: {e} !!!!!!")
        return jsonify({
            'title': 'Error Finding Jobs',
            'jobs': []
        }), 500


if __name__ == '__main__':
    # Check if the build folder exists and has content
    if os.path.exists(app.static_folder) and os.path.isdir(app.static_folder) and len(os.listdir(app.static_folder)) > 0:
        print(f"Serving static files from: {app.static_folder}")
    else:
        print(f"Warning: Static folder '{app.static_folder}' not found or is empty.")
        print("Please run 'npm run build' in your React app directory.")
    
    app.run(debug=True, port=5000)