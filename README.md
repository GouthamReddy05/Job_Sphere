# Job_Sphere

An AI-assisted platform that analyzes resumes against job descriptions, identifies missing skills, generates interview questions, and suggests project ideas. It also fetches live job postings based on role and location.

This repository contains a React + TypeScript frontend and a FastAPI backend, plus integrations for embeddings, NLP, and job search APIs.

## 🎯 Project Overview

Job_Sphere helps job seekers and recruiters by:

- Comparing resumes to job descriptions and computing an ATS (Applicant Tracking System) score.
- Reporting missing skills and recommended improvements.
- Generating tailored project ideas and interview questions.
- Fetching live job postings based on role and location.

## 💾 Data & Models

Key components used:

- Resume parsing: `pdfminer.six`, `pdfplumber`, `PyPDF2`, `python-docx`.
- Scoring & embeddings: `gensim`, `nltk`, pre-trained GloVe embeddings (or other vectors).
- Retrieval & reasoning: `langchain`, `langchain-community`, and an LLM (e.g., Ollama or other provider).
- Search integration: SerpAPI (Google Search Results) for job links.
- Database: MongoDB for user and application data.

## 🛠️ Tech Stack

- Frontend: React + TypeScript, Tailwind CSS, Framer Motion
- Backend: Python, FastAPI, python-dotenv
- NLP: NLTK, Gensim, GloVe embeddings
- Database: MongoDB

## 🚀 Quick Start (Development)

1. Clone the repository

```bash
git clone https://github.com/your-username/Job_Sphere.git
cd Job_Sphere
```

2. Backend (FastAPI)

```bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create a .env file in the project root (see examples below)

# Run the FastAPI server (default host: 127.0.0.1, port: 8000)
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

3. Frontend (development)

```bash
cd frontend/resume-analyzer-app
npm install
npm start

# Frontend dev server runs at http://localhost:3000 by default
```

Notes:
- Run backend and frontend in separate terminals. To run both together you can use `concurrently` (example below).

Example (run both):

```bash
# from project root
npx concurrently "uvicorn main:app --reload --port 8000" "cd frontend/resume-analyzer-app && npm start"
```

## 🔐 Environment Variables

Create a `.env` file in the project root with the following keys (replace placeholders):

- MONGODB_URI=mongodb+srv://<user>:<pass>@cluster0.mongodb.net/your_db
- SERP_API_KEY=your_serpapi_key
- GEMINI_API_KEY=your_llm_api_key_or_provider_key
- JOBBLE_API_KEY=your_jobble_api_key (optional)

Add any other provider-specific keys your deployment requires (Ollama, other LLM providers, etc.).

## 📋 API Endpoints (examples)

- POST /api/auth/signup — User registration
- POST /api/auth/login — User login
- POST /api/auth/logout — User logout
- POST /api/process-resume — Upload & process resume
- POST /api/analyze/ats-score — Analyze ATS score
- POST /api/analyze/missing-skills — Get missing skills
- POST /api/analyze/project-ideas — Generate project ideas
- POST /api/analyze/interview-prep — Generate interview questions
- POST /api/analyze/job-matches — Fetch live job postings

## 📌 Example user flow

1. Sign up / Log in
2. Provide job details (role, location, experience, job description)
3. Upload resume (PDF/DOCX)
4. View ATS score, missing skills, project ideas, interview questions, and job matches

## Contributing

Contributions welcome — please fork, create a feature branch, and submit a pull request. Include tests or manual verification steps for significant changes.

## License

Add a license file if you intend to open-source this project.
