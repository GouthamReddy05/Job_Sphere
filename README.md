# Job_Sphere

An advanced AI-powered platform to analyze resumes against job descriptions, identify missing skills, generate interview questions, and suggest project ideas. The system also fetches live job postings based on the user's role and location.

This repository contains the frontend (React + TypeScript) and backend (FastAPI + LangChain) code, along with integration for embeddings, NLP models, and job search APIs.

## 🎯 Project Overview

Job seekers often struggle to understand how well their resumes align with job requirements. Recruiters, on the other hand, receive hundreds of applications and need quick filtering.

This project bridges the gap by:

- Analyzing resumes against job descriptions.
- Calculating an ATS (Applicant Tracking System) Score.
- Suggesting missing skills to improve resumes.
- Generating project ideas tailored to the job role.
- Creating interview questions (technical + general).
- Fetching live job postings with links based on the role and location.

## 💾 Data & Models

The project uses a combination of NLP models and APIs:

- **Resume Parsing**: pdfminer, PyPDF2, python-docx, pdfplumber.
- **Scoring & Embeddings**: gensim, nltk, GloVe model (to calculate similarity score).
- **Search Integration**: Google Search API (google-search-results).
- **RAG + Reasoning**: LangChain, LangChain-Community, Ollama.
- **Database**: MongoDB (for user authentication and data storage).

## ⚙️ Project Workflow

### 1. Frontend (React + TypeScript)

- Signup/Login page with animations.
- Resume upload (supports .pdf and .docx).
- Form to collect job role, location, experience, job description.
- Autocomplete for Indian cities.
- Feature navigation for ATS Score, Skills, Projects, Interview Questions, and Job Links.

### 2. Backend (FastAPI)

- Processes uploaded resumes with async operations.
- Extracts text content from PDF and DOCX files.
- Computes ATS Score using job description + GloVe embeddings.
- Identifies missing skills with NLP.
- Generates project ideas & interview questions using LangChain + Ollama.
- Fetches live jobs using Google Search API.
- Handles user authentication with JWT tokens and MongoDB.
- CORS-enabled for secure cross-origin requests.

## 📊 Features & Outputs

| Feature | Description | Example Output |
|---------|-------------|-----------------|
| ATS Score | Resume vs Job Description score | Your ATS Score: 78/100 |
| Missing Skills | List of skills not found in resume | Cloud Computing, ReactJS, AWS |
| Project Ideas | AI-generated project suggestions | Build a chatbot for customer support |
| Interview Questions | Technical + HR questions | "Explain polymorphism in OOPs", "Tell me about yourself" |
| Live Jobs | Real-time job links from Google | https://www.naukri.com/... |

## 🛠️ Technologies Used

### Frontend

- React + TypeScript
- Tailwind CSS
- Framer Motion (for animations)

### Backend

- **Python** (FastAPI, FastAPI-CORS, python-dotenv)
- **LangChain** & LangChain-Community
- **Ollama** (for LLM-powered generation)
- **MongoDB** (for database and user management)
- **PDF & DOCX parsers**: pdfminer, pdfplumber, PyPDF2, python-docx
- **Authentication**: JWT tokens with secure password hashing

### NLP & Scoring

- NLTK, Gensim
- Pre-trained GloVe embeddings

### Search API

- Google Search Results API (SerpAPI)

## 🚀 How to Run This Project

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Job_Sphere.git
cd Job_Sphere

2.  Setup Backend (FastAPI)

python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt

Run the FastAPI server:

cd frontend/resume-analyzer-app
npm install
npm run start

Access at: http://localhost:3000

📌 Example Flow
Sign up or Login.
Fill job details (role, location, experience, description).
Upload your resume (PDF/DOCX).
Navigate through features:
View ATS Score.
Discover Missing Skills.
Get Project Ideas.
Practice Interview Questions.


Explore Live Job Links.
🔐 Environment Variables
Create a .env file in the root directory with the following:

MONGODB_URI=your_mongodb_connection_string
SERP_API_KEY=your_serpapi_key
OLLAMA_BASE_URL=http://localhost:11434

📋 API Endpoints
POST /api/auth/signup - User registration
POST /api/auth/login - User login
POST /api/auth/logout - User logout
GET /api/auth/me - Get current user
POST /api/process-resume - Process and validate resume
POST /api/analyze/ats-score - Analyze ATS score
POST /api/analyze/missing-skills - Get missing skills
POST /api/analyze/project-ideas - Generate project ideas
POST /api/analyze/interview-prep - Generate interview questions
POST /api/analyze/job-matches - Fetch live job postings

🤝 Contributing
Contributions are welcome! Please fork this repository and submit a pull request.
>>>>>>> eba5603 (Initial commit)
