import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import pickle
from scraper import MedicalScraper

# Încărcăm datele existente
with open('data/medical_data.json', 'r', encoding='utf-8') as f:
    existing_data = json.load(f)

# Pregătim datele pentru antrenament
questions = []
answers = []

for item in existing_data:
    questions.extend(item['questions'])
    answers.extend([item['answer']] * len(item['questions']))

# Verificăm dacă avem suficiente date
if len(questions) < 2:
    raise ValueError("Insufficient training data. Need at least 2 question-answer pairs.")

# Creăm și antrenăm vectorizatorul cu parametri ajustați
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 3),
    min_df=1,  # Reducem pragul pentru documente cu puține date
    stop_words=['ce', 'este', 'sunt', 'care', 'cum', 'pentru']
)

X = vectorizer.fit_transform(questions)

# Salvăm modelul și vectorizatorul
with open('model/vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

with open('model/questions.pkl', 'wb') as f:
    pickle.dump(X, f)

with open('model/answers.pkl', 'wb') as f:
    pickle.dump(answers, f)

print(f"Model antrenat cu {len(questions)} întrebări și {len(set(answers))} răspunsuri unice") 