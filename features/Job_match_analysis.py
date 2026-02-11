import re
import nltk
from nltk.corpus import stopwords
import numpy as np
from scipy.spatial.distance import cosine
# from gensim.models import KeyedVectors
import pickle


try:
    with open("glove_model.pkl", "rb") as f:
        glove_model = pickle.load(f)
except FileNotFoundError:
    print("Warning: 'glove_model.pkl' not found. Using simple keyword matching instead.")
    glove_model = None

try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
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

    if glove_model:
        resume_vector = get_document_vector(preprocessed_resume_text, glove_model)
        job_description_vector = get_document_vector(preprocessed_description_text, glove_model)
        similarity_score = 1 - cosine(resume_vector, job_description_vector)
        ats_score = round(similarity_score * 100, 2)
    else:
        # Fallback: Jaccard Similarity
        resume_set = set(preprocessed_resume_text)
        description_set = set(preprocessed_description_text)
        if not description_set:
            return 0.0
        intersection = resume_set.intersection(description_set)
        union = resume_set.union(description_set)
        similarity_score = len(intersection) / len(union)
        ats_score = round(similarity_score * 100, 2)

    return ats_score
