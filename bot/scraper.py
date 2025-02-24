from bs4 import BeautifulSoup
import requests
from mtranslate import translate
import json
import time
import traceback
import os

class MedicalScraper:
    def __init__(self):
        print("Initializing scraper...")
        
        # Creăm directorul data dacă nu există
        if not os.path.exists('data'):
            os.makedirs('data')
            print("Created data directory")
        
        # Configurare pentru site-ul tău
        self.base_url = "https://your-site.com"  # Înlocuiește cu URL-ul tău
        
        # Liste de URL-uri pentru boli comune pe categorii
        self.condition_urls = [
            "https://medlineplus.gov/commoncold.html",
            "https://medlineplus.gov/flu.html",
            "https://medlineplus.gov/headache.html",
            "https://medlineplus.gov/backpain.html",
            "https://medlineplus.gov/fever.html",
            "https://medlineplus.gov/soreThroat.html",
            "https://medlineplus.gov/cough.html",
            "https://medlineplus.gov/asthma.html",
            "https://medlineplus.gov/highbloodpressure.html",
            "https://medlineplus.gov/diabetes.html",
            "https://medlineplus.gov/arthritis.html",
            "https://medlineplus.gov/allergies.html",
            "https://medlineplus.gov/sinusitis.html",
            "https://medlineplus.gov/bronchitis.html",
            "https://medlineplus.gov/pneumonia.html",
            "https://medlineplus.gov/stomachache.html",
            "https://medlineplus.gov/diarrhea.html",
            "https://medlineplus.gov/migraine.html",
            "https://medlineplus.gov/conjunctivitis.html",
            "https://medlineplus.gov/earinfections.html"
        ]

        self.condition_urls.extend([
            "https://medlineplus.gov/depression.html",
            "https://medlineplus.gov/anxiety.html",
            "https://medlineplus.gov/heartburn.html",
            "https://medlineplus.gov/tonsillitis.html",
            "https://medlineplus.gov/chickenpox.html",
            "https://medlineplus.gov/measles.html",
            "https://medlineplus.gov/mumps.html",
            "https://medlineplus.gov/gastritis.html",
            "https://medlineplus.gov/ulcers.html",
            "https://medlineplus.gov/foodpoisoning.html"
        ])

        # Actualizăm categoriile pentru boli mai generale
        self.disease_categories = {
            'infectious': ['virus', 'bacteria', 'infection', 'flu', 'pneumonia'],
            'cardiovascular': ['heart', 'blood pressure', 'cardiac', 'stroke', 'circulation'],
            'respiratory': ['lung', 'breathing', 'asthma', 'bronchitis', 'cough'],
            'digestive': ['stomach', 'intestine', 'liver', 'digestion', 'gastric'],
            'neurological': ['brain', 'headache', 'migraine', 'nerve', 'seizure'],
            'musculoskeletal': ['muscle', 'bone', 'joint', 'back pain', 'arthritis'],
            'skin': ['rash', 'acne', 'dermatitis', 'eczema', 'skin infection'],
            'endocrine': ['diabetes', 'thyroid', 'hormone', 'metabolism'],
            'ent': ['ear', 'nose', 'throat', 'sinus', 'tonsils'],
            'general': ['fever', 'pain', 'fatigue', 'inflammation']
        }

        # Filtre pentru a exclude anumite tipuri de articole
        self.exclude_keywords = [
            'abuse', 'violence', 'addiction', 'social', 'economic', 
            'insurance', 'policy', 'statistics', 'research'
        ]
        
        # Actualizăm markerii de severitate
        self.severity_markers = {
            'urgent': ['emergency', 'severe', 'critical', 'immediate medical attention', 'call doctor'],
            'moderate': ['should see doctor', 'concerning', 'worsening', 'persistent'],
            'mild': ['mild', 'common', 'usually resolves', 'self-care', 'home treatment']
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
            'Accept-Language': 'ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        print("Headers configured.")

    def translate_text(self, text):
        try:
            translated = translate(text, 'ro')
            return translated
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return text

    def classify_disease(self, text):
        """Clasifică boala în funcție de descriere și simptome"""
        text = text.lower()
        categories = []
        
        for category, keywords in self.disease_categories.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        return categories if categories else ['unclassified']

    def determine_severity(self, text):
        """Determină severitatea bolii în funcție de descriere și simptome"""
        text = text.lower()
        
        if any(marker in text for marker in self.severity_markers['urgent']):
            return 'urgent'
        elif any(marker in text for marker in self.severity_markers['moderate']):
            return 'moderate'
        elif any(marker in text for marker in self.severity_markers['mild']):
            return 'mild'
        return 'unknown'

    def extract_symptoms_detailed(self, element):
        """Extrage simptome cu detalii suplimentare"""
        if not element:
            return []
            
        symptoms = []
        list_items = element.select('li') or element.select('p')
        
        for item in list_items:
            text = item.text.strip()
            if text:
                # Analizăm fiecare simptom
                symptom = {
                    'description': self.translate_text(text),
                    'severity': self.determine_severity(text),
                    'body_parts': self.extract_body_parts(text),
                    'duration': self.extract_duration(text),
                    'associated_symptoms': self.extract_associated_symptoms(text)
                }
                symptoms.append(symptom)
                
        return symptoms

    def extract_body_parts(self, text):
        """Extrage părțile corpului menționate în text"""
        body_parts = ['head', 'chest', 'stomach', 'back', 'arms', 'legs', 
                     'skin', 'throat', 'eyes', 'ears', 'mouth', 'heart', 'lungs']
        found = []
        text = text.lower()
        
        for part in body_parts:
            if part in text:
                found.append(self.translate_text(part))
                
        return found

    def extract_duration(self, text):
        """Extrage informații despre durata simptomelor"""
        duration_markers = ['acute', 'chronic', 'days', 'weeks', 'months', 'years', 
                          'temporary', 'permanent', 'recurring']
        text = text.lower()
        
        for marker in duration_markers:
            if marker in text:
                return self.translate_text(marker)
        return 'unspecified'

    def extract_associated_symptoms(self, text):
        """Extrage simptome asociate"""
        text = text.lower()
        associated = []
        
        # Căutăm fraze care indică simptome asociate
        markers = ['along with', 'accompanied by', 'associated with', 'and also']
        for marker in markers:
            if marker in text:
                parts = text.split(marker)
                if len(parts) > 1:
                    associated.append(self.translate_text(parts[1].strip()))
                    
        return associated

    def should_process_article(self, title, description):
        """Verifică dacă articolul este relevant pentru colecția noastră"""
        text = (title + " " + description).lower()
        
        # Excludem articolele care conțin cuvinte cheie nedorite
        if any(keyword in text for keyword in self.exclude_keywords):
            return False
            
        # Verificăm dacă articolul este despre o boală sau condiție medicală
        medical_keywords = [
            'disease', 'condition', 'disorder', 'syndrome', 'infection',
            'pain', 'symptoms', 'treatment', 'illness', 'health problem'
        ]
        
        return any(keyword in text for keyword in medical_keywords)

    def scrape_conditions(self):
        try:
            print("\nStarting scraping process...")
            all_medical_data = []
            
            print(f"Processing {len(self.condition_urls)} common conditions")
            
            for url in self.condition_urls:
                try:
                    print(f"\nAccessing: {url}")
                    
                    response = requests.get(url, headers=self.headers, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extragem informațiile direct din pagina bolii
                        title = (soup.select_one("h1.with-also") or 
                                soup.select_one("h1.page-title") or
                                soup.select_one("h1"))
                                
                        summary = (soup.select_one("#topic-summary") or 
                                  soup.select_one(".page-summary") or
                                  soup.select_one(".intro"))
                                  
                        symptoms = (soup.select_one("#symptoms") or 
                                  soup.select_one(".symptoms"))
                                  
                        causes = (soup.select_one("#causes") or 
                                soup.select_one(".causes"))
                                
                        treatment = (soup.select_one("#treatment") or 
                                   soup.select_one(".treatment"))
                        
                        if title:
                            data = {
                                "boala": self.translate_text(title.text.strip()),
                                "descriere": self.translate_text(summary.text.strip()) if summary else "",
                                "simptome": self.extract_symptoms_detailed(symptoms) if symptoms else [],
                                "cauze": self.extract_list(causes) if causes else [],
                                "tratament": self.extract_list(treatment) if treatment else [],
                                "url": url
                            }
                            
                            all_medical_data.append(data)
                            print(f"Processed: {data['boala']}")
                            print(f"Found: {len(data['simptome'])} symptoms, "
                                  f"{len(data['cauze'])} causes, "
                                  f"{len(data['tratament'])} treatments")
                    else:
                        print(f"Error accessing {url}: {response.status_code}")
                        
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error processing URL: {str(e)}")
                    continue
            
            # Salvăm datele
            if all_medical_data:
                with open('data/medical_data_medline.json', 'w', encoding='utf-8') as f:
                    json.dump(all_medical_data, f, ensure_ascii=False, indent=4)
                print(f"\nSaved {len(all_medical_data)} conditions to medical_data_medline.json")
            
            return all_medical_data
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            traceback.print_exc()
            return []

    def extract_list(self, element):
        """Extrage și traduce o listă de elemente din HTML"""
        if not element:
            return []
            
        items = []
        list_items = element.select('li') or element.select('p')
        
        for item in list_items:
            text = item.text.strip()
            if text:
                translated = self.translate_text(text)
                items.append(translated)
                
        return items

    def load_existing_data(self):
        """Încarcă datele existente din toate fișierele JSON"""
        all_data = []
        json_files = [
            'data/medical_data.json',
            'data/medical_data_medline.json',
            'data/medical_data_sfatul.json'
        ]
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.extend(data)
                    print(f"Loaded {len(data)} conditions from {file_path}")
            except FileNotFoundError:
                print(f"No existing data in {file_path}")
                
        return all_data

    def save_combined_data(self, new_data):
        """Combină și salvează toate datele"""
        # Încarcă datele existente
        existing_data = self.load_existing_data()
        
        # Adaugă datele noi
        combined_data = existing_data + new_data
        
        # Elimină duplicatele bazate pe URL
        unique_data = {item['url']: item for item in combined_data}.values()
        
        # Salvează datele combinate
        with open('data/medical_knowledge_base.json', 'w', encoding='utf-8') as f:
            json.dump(list(unique_data), f, ensure_ascii=False, indent=4)
            
        print(f"\nSaved {len(unique_data)} total conditions to knowledge base")
        return list(unique_data)

    def explore_site_structure(self):
        """Explorează structura site-ului și găsește elementele relevante"""
        try:
            print(f"\nExploring site structure: {self.base_url}")
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Găsește toate link-urile
                links = soup.find_all('a')
                print(f"Found {len(links)} links")
                
                # Găsește toate elementele cu class sau id
                elements = soup.find_all(class_=True) + soup.find_all(id=True)
                print("\nFound elements with classes/ids:")
                for elem in elements[:10]:  # Primele 10 pentru exemplu
                    print(f"Tag: {elem.name}, Class: {elem.get('class')}, ID: {elem.get('id')}")
                
                # Salvează HTML-ul pentru analiză
                with open('site_structure.html', 'w', encoding='utf-8') as f:
                    f.write(soup.prettify())
                    
                return True
                
        except Exception as e:
            print(f"Error exploring site: {str(e)}")
            return False

class MedicalKnowledgeBase:
    def __init__(self):
        print("Initializing Medical Knowledge Base...")
        
        # Creăm directorul data dacă nu există
        if not os.path.exists('data'):
            os.makedirs('data')
            print("Created data directory")
        
        # Încărcăm datele existente
        self.load_knowledge_base()
        
        # Categorii de boli pentru clasificare
        self.disease_categories = {
            'infectious': ['virus', 'bacteria', 'infectie', 'gripa', 'pneumonie'],
            'cardiovascular': ['inima', 'tensiune', 'cardiac', 'stroke', 'circulatie'],
            'respiratory': ['plamani', 'respiratie', 'astm', 'bronsita', 'tuse'],
            'digestive': ['stomac', 'intestin', 'ficat', 'digestie', 'gastric'],
            'neurological': ['creier', 'durere de cap', 'migrena', 'nerv', 'convulsii'],
            'musculoskeletal': ['muschi', 'oase', 'articulatii', 'durere de spate', 'artrita'],
            'skin': ['eruptie', 'acnee', 'dermatita', 'eczema', 'infectie piele'],
            'endocrine': ['diabet', 'tiroida', 'hormoni', 'metabolism'],
            'ent': ['ureche', 'nas', 'gat', 'sinusuri', 'amigdale'],
            'general': ['febra', 'durere', 'oboseala', 'inflamatie']
        }

    def load_knowledge_base(self):
        """Încarcă toate datele medicale existente"""
        self.medical_data = []
        json_files = [
            'data/medical_data.json',
            'data/medical_data_medline.json',
            'data/medical_data_sfatul.json',
            'data/medical_knowledge_base.json'
        ]
        
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.medical_data.extend(data)
                    print(f"Loaded {len(data)} conditions from {file_path}")
            except FileNotFoundError:
                print(f"No existing data in {file_path}")
                
        print(f"Total conditions in knowledge base: {len(self.medical_data)}")

    def search_conditions(self, query):
        """Caută în baza de cunoștințe după un termen"""
        query = query.lower()
        results = []
        
        for condition in self.medical_data:
            score = 0
            
            # Caută în titlu
            if query in condition['boala'].lower():
                score += 3
            
            # Caută în simptome
            for symptom in condition.get('simptome', []):
                if isinstance(symptom, dict):  # Pentru simptome detaliate
                    if query in symptom['description'].lower():
                        score += 2
                elif isinstance(symptom, str):  # Pentru simptome simple
                    if query in symptom.lower():
                        score += 2
            
            # Caută în cauze
            for cause in condition.get('cauze', []):
                if query in cause.lower():
                    score += 1
            
            if score > 0:
                results.append({
                    'condition': condition,
                    'relevance': score
                })
        
        # Sortează rezultatele după relevanță
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results

    def get_condition_details(self, condition_name):
        """Returnează detalii complete despre o boală"""
        condition_name = condition_name.lower()
        for condition in self.medical_data:
            if condition['boala'].lower() == condition_name:
                return condition
        return None

if __name__ == "__main__":
    try:
        print("=== Starting Medical Knowledge Base ===")
        kb = MedicalKnowledgeBase()
        
        while True:
            print("\n1. Caută o boală sau simptom")
            print("2. Vezi toate bolile")
            print("3. Ieșire")
            
            choice = input("\nAlegeți opțiunea (1-3): ")
            
            if choice == "1":
                query = input("\nIntroduceți termenul de căutare: ")
                results = kb.search_conditions(query)
                
                if results:
                    print(f"\nAm găsit {len(results)} rezultate:")
                    for i, result in enumerate(results[:5], 1):
                        condition = result['condition']
                        print(f"\n{i}. {condition['boala']}")
                        if 'simptome' in condition:
                            print("Simptome principale:", end=" ")
                            if isinstance(condition['simptome'], list):
                                if condition['simptome']:
                                    if isinstance(condition['simptome'][0], dict):
                                        print(", ".join([s['description'] for s in condition['simptome'][:3]]))
                                    else:
                                        print(", ".join(condition['simptome'][:3]))
                        print(f"Relevanță: {result['relevance']}")
                else:
                    print("\nNu am găsit rezultate pentru căutarea dvs.")
                    
            elif choice == "2":
                print("\nToate bolile din baza de cunoștințe:")
                for i, condition in enumerate(kb.medical_data, 1):
                    print(f"{i}. {condition['boala']}")
                    
            elif choice == "3":
                print("\nLa revedere!")
                break
                
    except Exception as e:
        print("\nCRITICAL ERROR:")
        print(str(e))
    finally:
        input("\nApăsați Enter pentru a ieși...") 