import re
import nltk
from nltk.corpus import stopwords
import numpy as np
from scipy.spatial.distance import cosine
from gensim.models import KeyedVectors
import pickle


with open("glove_model.pkl", "rb") as f:
    glove_model = pickle.load(f)

# nltk.download('stopwords')



stop_words = set(stopwords.words('english'))

def pre_process_corrected(text):

  text = text.lower()
  text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
  words = text.split()
  words = [word for word in words if word not in stop_words]
  
  return words


def get_document_vector(processed_tokens, model):

  vectors = [model[token] for token in processed_tokens if token in model]
  
  if not vectors:
      return np.zeros(model.vector_size)
  return np.mean(vectors, axis=0)



def calculate_ats_score(resume_text, job_description_text):
    
    preprocessed_resume_text = pre_process_corrected(resume_text)

    preprocessed_description_text = pre_process_corrected(job_description_text)

    resume_vector = get_document_vector(preprocessed_resume_text, glove_model)

    job_description_vector = get_document_vector(preprocessed_description_text, glove_model)

    similarity_score = 1 - cosine(resume_vector, job_description_vector)


    ats_score = round(similarity_score * 100, 2)

    return ats_score

# resume_text = """
# GOUTHAM REDDY
# +91 9398625385
# anugu.gouthamreddy2005@gmail.com
# Summary
# Third-year Computer Science undergraduate at Sreenidhi Institute of Science and Technology with a strong foundation in Data Structures,
# Algorithms, and a deep interest in AI/ML. Solved 600+ DSA problems across coding platforms and currently exploring Deep Learning and
# Artificial Intelligence. Passionate about learning, building, and contributing to impactful tech solutions.
# Education
# Sreenidhi Institute of Science and Technology, Hyderabad
# B.Tech in Computer Science and Engineering, CGPA: 8.9/10
# Chaitanya Junior College, Hyderabad
# Intermediate (MPC), Score: 98.8%.
# Experience
# AI Developer
# Contributed to VISWAM.AI’s Fine-Tuning Module by curating and uploading 100+ multimodal Telugu cultural data samples (folk tales,
# songs, traditions, etc.) across 6+ categories, enhancing regional language AI model performance.
# Smart Interviews – Data Structures & Algorithms Training Program
# Covered 10+ core DSA topics with 50+ hours of structured instruction.
# Enhanced problem-solving speed and accuracy through real-world coding interview questions and hands-on practice.
# Project
# Crop Disease Classifier and Treatment Guider
# Impact: Achieved high accuracy in diagnosing 12 crop diseases using computer vision and provided detailed treatment guidance, helping
# farmers with actionable disease management strategies.
# Tech Stack: Python, TensorFlow/Keras, OpenCV, scikit-learn, Flask, pandas, Matplotlib, RAG with FAISS and Sentence Transformers.
# Key Point: Built an end-to-end system that not only classifies crop leaf diseases from images but also generates treatment and precautionary
# measures through an integrated knowledge base.
# VaishnavAI
# Spiritual Q&A chatbot specialized in Ramayana and Bhagavatam using LLMs and vector search.
# Impact: Improved accuracy and relevance in spiritual query responses using context-aware AI.
# Tech Stack: Python, FAISS, SentenceTransformers, Gemini API
# Key Point: Stored shlokas in FAISS index and used top-k retrieval + LLM (Gemini API) for accurate, culturally grounded answers.
# Technical Skills
# Programming Languages: C, C++, Python
# Web Technologies: HTML, CSS, JavaScript
# Libraries & Frameworks: Flask, scikit-learn, Tensorflow, NumPy, Pandas, Matplotlib
# Machine Learning: Supervised Learning, Convolutional Neural Networks (CNN)
# Deep Learning: RNN, LSTM, GRU, Bidirectional LSTM
# Natural Language Processing: Bagofwords, TFIDF, Word2Vec, Encoders, Decoders, Transformers
# Core CS Concepts: Data Structures & Algorithms (DSA), Object-Oriented Programming (OOPS), DBMS
# Tools: Git, GitHub, VS Code, Jupyter notebook, Google Colab
# Certifications
# Introduction to Data Science Virtual Internship certificate from Cisco Networking Academy
# Earned participation certificate in coding competitions at VNR VJIET and Geethanjali College of Engineering
# """

# job_description_text = """
# Job Title: Machine Learning Engineer (Intern). Seeking a candidate with a strong background in DSA and Python to
# design, train, and deploy computer vision models using TensorFlow and OpenCV. Responsibilities include building ML
# pipelines and working with libraries like scikit-learn, Pandas, and NumPy. Must be familiar with Git.
# """

# print(calculate_ats_score(resume_text, job_description_text))