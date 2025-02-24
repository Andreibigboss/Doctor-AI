import pickle
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import defaultdict
import json

class MedicalBot:
    def __init__(self):
        # Încărcăm modelul și datele salvate
        try:
            with open('model/vectorizer.pkl', 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            with open('model/questions.pkl', 'rb') as f:
                self.X = pickle.load(f)
            
            with open('model/answers.pkl', 'rb') as f:
                self.answers = pickle.load(f)

            # Încărcăm baza de date medicală
            with open('data/medical_data.json', 'r', encoding='utf-8') as f:
                self.medical_data = json.load(f)
            
            print("Model and medical data loaded successfully")
        except Exception as e:
            print(f"Error loading model or data: {str(e)}")
            raise

    def identify_symptoms_from_text(self, text):
        """Identifică simptome din text folosind analiza lingvistică"""
        text = text.lower().strip()
        print(f"Analizez textul: '{text}'")  # Debug
        
        # Expresii comune pentru dureri
        expresii_durere = [
            "mă doare", "ma doare",
            "am durere", "am dureri",
            "simt durere", "simt dureri"
        ]
        
        # Părți ale corpului și simptome comune
        parti_corp = {
            "burta": ["burta", "burtă", "stomac", "abdomen", "abdominal"],
            "cap": ["cap", "capul", "tâmplă", "tampla", "frunte"],
            "gat": ["gat", "gât", "gatul", "gâtul"],
            "piept": ["piept", "pieptul", "torace"]
        }
        
        simptome_identificate = []
        
        # 1. Verificăm expresiile de durere
        for expresie in expresii_durere:
            if expresie in text:
                # Căutăm partea corpului după expresia de durere
                rest_text = text[text.find(expresie) + len(expresie):].strip()
                print(f"Text după expresia de durere: '{rest_text}'")  # Debug
                
                for parte, variante in parti_corp.items():
                    if any(varianta in rest_text or varianta in text for varianta in variante):
                        simptome_identificate.append({
                            "nume": f"durere de {parte}",
                            "sursa": "expresie_directă",
                            "context": text
                        })
                        print(f"Găsit simptom: durere de {parte}")  # Debug
        
        # 2. Verificăm și în baza de date
        for condition in self.medical_data:
            if 'simptome' in condition:
                for symptom in condition['simptome']:
                    symptom_text = symptom if isinstance(symptom, str) else symptom.get('description', '')
                    if symptom_text.lower() in text:
                        simptome_identificate.append({
                            "nume": symptom_text,
                            "sursa": "baza_de_date",
                            "context": text
                        })
                        print(f"Găsit simptom din baza de date: {symptom_text}")  # Debug
        
        # Eliminăm duplicate și returnăm rezultatele
        rezultate = list({v['nume']:v for v in simptome_identificate}.values())
        print(f"Simptome identificate final: {[r['nume'] for r in rezultate]}")  # Debug
        return rezultate

    def find_relevant_answers(self, symptoms, user_input):
        # Vectorizăm întrebarea utilizatorului
        user_vector = self.vectorizer.transform([user_input])
        
        # Calculăm similaritatea cu toate întrebările din training
        similarities = cosine_similarity(user_vector, self.X)[0]
        
        # Găsim cele mai relevante răspunsuri
        relevant_indices = np.where(similarities > 0.2)[0]
        
        if len(relevant_indices) == 0:
            return None

        # Colectăm informații relevante
        collected_info = defaultdict(set)
        for idx in relevant_indices:
            answer = self.answers[idx]
            # Împărțim răspunsul în secțiuni
            if "Cauze:" in answer:
                collected_info["cauze"].add(answer.split("Cauze:")[1].split(".")[0])
            if "Consultați medicul" in answer:
                collected_info["urgență"].add(answer.split("Consultați medicul")[1].split(".")[0])
            if "Pentru" in answer:
                collected_info["tratament"].add(answer.split("Pentru")[1].split(".")[0])

        return collected_info

    def get_symptom_info(self, symptom_name):
        """Caută informații despre un simptom în baza de date"""
        for condition in self.medical_data:
            if 'simptome' in condition:
                # Verifică în lista de simptome
                for s in condition['simptome']:
                    if isinstance(s, str) and symptom_name.lower() in s.lower():
                        return {
                            'recomandari': condition['tratament']['recomandari'] if isinstance(condition['tratament'], dict) else condition['tratament'],
                            'boli_asociate': [condition['boala']]
                        }
        return None

    def format_list(self, items):
        """Formatează o listă de simptome sau tratamente"""
        if not items:
            return ""
        if isinstance(items[0], dict):
            return ", ".join([item['description'] for item in items])
        return ", ".join(items)

    def format_treatment(self, treatment):
        """Formatează informațiile despre tratament"""
        if isinstance(treatment, dict):
            if 'recomandari' in treatment:
                return ", ".join(treatment['recomandari'])
            return str(treatment)
        elif isinstance(treatment, list):
            return ", ".join(treatment)
        return str(treatment)

    def get_response(self, user_input):
        try:
            # Identificăm simptomele
            symptoms = self.identify_symptoms_from_text(user_input)
            
            # Învață din conversație
            learning_response = self.learn_from_conversation(user_input, [s['nume'] for s in symptoms])
            if learning_response:
                return learning_response
                
            # Învață din descrieri detaliate
            detailed_learning = self.learn_from_detailed_description(user_input)
            if detailed_learning:
                return detailed_learning
            
            # Încercăm să învățăm din conversație
            learning_response = self.learn_from_conversation(user_input, [s['nume'] for s in symptoms])
            if learning_response:
                return learning_response + "\n\nPot să vă ajut cu altceva?"
            
            # Căutăm în baza de cunoștințe
            knowledge_results = self.search_medical_data(user_input)
            
            response = ""
            
            if symptoms:
                response += "Am identificat următoarele simptome:\n\n"
                for symptom in symptoms:
                    # Căutăm informații despre simptom în baza de date
                    symptom_info = self.get_symptom_info(symptom['nume'])
                    response += f"• {symptom['nume'].title()}:\n"
                    if symptom_info:
                        if 'recomandari' in symptom_info:
                            response += f"  Recomandări: {self.format_list(symptom_info['recomandari'])}\n"
                        if 'boli_asociate' in symptom_info:
                            response += f"  Poate fi asociat cu: {', '.join(symptom_info['boli_asociate'])}\n"
                    response += "\n"
            
            # Adăugăm informații din baza de cunoștințe
            if knowledge_results:
                response += "\nInformații relevante din baza noastră medicală:\n\n"
                for result in knowledge_results[:2]:
                    condition = result['condition']
                    response += f"• {condition['boala']}:\n"
                    if 'simptome' in condition:
                        response += "  Simptome asociate: " + self.format_list(condition['simptome'][:3]) + "\n"
                    if 'tratament' in condition:
                        response += "  Tratament recomandat: " + self.format_treatment(condition['tratament']) + "\n"
                    response += "\n"
            
            if not symptoms and not knowledge_results:
                return "Îmi pare rău, nu am înțeles exact problema. Puteți să descrieți mai detaliat ce simptome aveți?"
            
            response += "\nNotă: Aceste informații sunt generale. Pentru un diagnostic corect, vă recomand să consultați un medic."
            
            return response
            
        except Exception as e:
            print(f"Error in get_response: {str(e)}")
            return "Îmi pare rău, a apărut o eroare. Vă rog să reformulați întrebarea."

    def search_medical_data(self, query):
        """Caută în baza de cunoștințe medicale"""
        query = query.lower()
        results = []
        
        try:
            for condition in self.medical_data:
                score = 0
                
                # Caută în titlu
                if query in condition['boala'].lower():
                    score += 3
                
                # Caută în simptome
                if 'simptome' in condition:
                    for symptom in condition['simptome']:
                        if isinstance(symptom, dict):
                            if query in symptom['description'].lower():
                                score += 2
                        elif isinstance(symptom, str):
                            if query in symptom.lower():
                                score += 2
                
                # Caută în cauze
                if 'cauze' in condition:
                    for cause in condition['cauze']:
                        if query in cause.lower():
                            score += 1
                
                if score > 0:
                    results.append({
                        'condition': condition,
                        'relevance': score
                    })
            
            # Sortează după relevanță
            results.sort(key=lambda x: x['relevance'], reverse=True)
            return results
            
        except Exception as e:
            print(f"Error in search_medical_data: {str(e)}")
            return []

    def find_possible_conditions(self, symptoms):
        # Găsește bolile posibile bazate pe simptome
        possible_conditions = []
        
        for condition in self.medical_data:
            matching_symptoms = set(symptoms) & set(condition['simptome'])
            if matching_symptoms:
                possible_conditions.append({
                    'boala': condition['boala'],
                    'matching_symptoms': len(matching_symptoms),
                    'total_symptoms': len(condition['simptome']),
                    'score': len(matching_symptoms) / len(condition['simptome']),
                    'tratament': condition['tratament'],
                    'cauze': condition['cauze']
                })
        
        # Sortează după scorul de potrivire
        possible_conditions.sort(key=lambda x: x['score'], reverse=True)
        return possible_conditions

    def learn_from_conversation(self, user_input, symptoms_mentioned):
        """Învață din conversațiile cu utilizatorii"""
        try:
            # Verifică dacă avem o boală nouă menționată
            if "am fost diagnosticat cu" in user_input.lower() or "medicul mi-a spus că am" in user_input.lower():
                # Extrage boala nouă
                text_parts = user_input.lower().split("cu" if "cu" in user_input.lower() else "am")
                potential_disease = text_parts[1].strip()
                
                # Verifică dacă boala există deja
                if not any(condition['boala'].lower() == potential_disease for condition in self.medical_data):
                    # Creează o nouă intrare
                    new_condition = {
                        "boala": potential_disease,
                        "simptome": symptoms_mentioned,
                        "sursa": "conversație_utilizator",
                        "confirmare_necesară": True  # Marcăm pentru verificare
                    }
                    
                    # Adaugă în baza de date temporară
                    with open('data/learned_conditions.json', 'a', encoding='utf-8') as f:
                        json.dump(new_condition, f, ensure_ascii=False)
                        f.write('\n')
                    
                    print(f"Am învățat despre o nouă condiție: {potential_disease}")
                    return f"Mulțumesc pentru informație. Am notat despre {potential_disease} și simptomele asociate."
            
            return None
            
        except Exception as e:
            print(f"Error learning from conversation: {str(e)}")
            return None

    def learn_from_detailed_description(self, user_input):
        """Învață din descrieri detaliate ale bolilor"""
        try:
            # Identifică pattern-uri de descriere detaliată
            patterns = [
                "simptomele sunt", "simptomele includ",
                "se manifestă prin", "cauzele sunt",
                "se tratează cu", "tratamentul include"
            ]
            
            text_lower = user_input.lower()
            new_info = {}
            
            # Extrage informații structurate
            for pattern in patterns:
                if pattern in text_lower:
                    section = text_lower.split(pattern)[1].split(".")[0]
                    if "simptom" in pattern:
                        new_info["simptome"] = [s.strip() for s in section.split(",")]
                    elif "cauz" in pattern:
                        new_info["cauze"] = [c.strip() for c in section.split(",")]
                    elif "trat" in pattern:
                        new_info["tratament"] = [t.strip() for t in section.split(",")]
            
            if new_info:
                # Salvează informațiile noi
                with open('data/new_medical_info.json', 'a', encoding='utf-8') as f:
                    json.dump(new_info, f, ensure_ascii=False)
                    f.write('\n')
                return "Am învățat informații noi despre această condiție medicală. Mulțumesc!"
                
            return None
            
        except Exception as e:
            print(f"Error learning from description: {str(e)}")
            return None

    def learn_from_feedback(self, user_input, previous_response, was_helpful):
        """Învață din feedback-ul utilizatorilor"""
        try:
            if not was_helpful:
                # Salvează cazurile unde răspunsul nu a fost util
                feedback_data = {
                    "intrebare": user_input,
                    "raspuns": previous_response,
                    "util": False,
                    "necesita_imbunatatire": True
                }
                
                with open('data/feedback_to_improve.json', 'a', encoding='utf-8') as f:
                    json.dump(feedback_data, f, ensure_ascii=False)
                    f.write('\n')
                
                return "Îmi pare rău că răspunsul nu a fost util. Am notat acest caz pentru îmbunătățire."
                
            return None
            
        except Exception as e:
            print(f"Error processing feedback: {str(e)}")
            return None 