import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

class MedicalDataCollector:
    def __init__(self):
        self.medical_sources = [
            {
                "name": "WHO",
                "url": "https://www.who.int/health-topics",
                "type": "official"
            },
            {
                "name": "MedlinePlus",
                "url": "https://medlineplus.gov/healthtopics.html",
                "type": "medical_library"
            },
            {
                "name": "NIH",
                "url": "https://www.nih.gov/health-information",
                "type": "research"
            }
        ]
        
        # Creăm directorul pentru date dacă nu există
        if not os.path.exists('data'):
            os.makedirs('data')

    def collect_new_data(self):
        """Colectează date noi din sursele medicale"""
        new_data = []
        summary = []
        
        for source in self.medical_sources:
            try:
                print("\n" + "="*50)
                print(f"Sursa: {source['name']}")
                print("="*50)
                print(f"Accesez URL: {source['url']}")
                
                # Colectează date de la sursă
                response = requests.get(source['url'], timeout=10)
                print(f"Status code: {response.status_code}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    print("Pagina accesată cu succes, caut informații...")
                    
                    # Extrage informații despre boli
                    diseases = self.extract_diseases(soup, source['name'])
                    print(f"Am găsit {len(diseases)} boli")
                    
                    if diseases:
                        # Adaugă sursa și timestamp
                        for disease in diseases:
                            disease.update({
                                "sursa": source['name'],
                                "data_colectare": datetime.now().isoformat(),
                                "verificat": False
                            })
                        
                        new_data.extend(diseases)
                        status = f"Succes - {len(diseases)} boli găsite"
                    else:
                        status = "Nu s-au găsit boli noi"
                else:
                    status = f"Eroare - Status code: {response.status_code}"
                    
            except Exception as e:
                status = f"Eroare - {str(e)}"
                print(f"Detalii eroare: {e.__class__.__name__}")
            
            summary.append(f"{source['name']}: {status}")
                
        # Afișează rezumatul
        print("\n" + "="*50)
        print("REZUMAT COLECTARE DATE:")
        print("="*50)
        for line in summary:
            print(line)
        print(f"\nTotal boli noi găsite: {len(new_data)}")
        print("="*50)
        print("\nApasă ENTER pentru a continua...")
        input()
        
        return new_data

    def update_knowledge_base(self):
        """Actualizează baza de cunoștințe cu date noi"""
        try:
            # Colectează date noi
            new_data = self.collect_new_data()
            
            if not new_data:
                print("Nu s-au găsit date noi")
                return
                
            # Încarcă baza de date existentă
            existing_data = []
            try:
                with open('data/medical_data.json', 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except FileNotFoundError:
                print("Se creează o nouă bază de date")
            
            # Combină datele noi cu cele existente, evitând duplicatele
            updated_data = self.merge_data(existing_data, new_data)
            
            # Salvează datele actualizate
            with open('data/medical_data.json', 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, ensure_ascii=False, indent=4)
                
            print(f"Baza de date actualizată cu {len(new_data)} intrări noi")
            
        except Exception as e:
            print(f"Eroare la actualizarea bazei de date: {str(e)}")

    def merge_data(self, existing_data, new_data):
        """Combină datele noi cu cele existente, evitând duplicatele"""
        merged = {item['boala']: item for item in existing_data}
        
        for item in new_data:
            if item['boala'] not in merged:
                merged[item['boala']] = item
            else:
                # Actualizează informațiile existente cu date noi
                existing = merged[item['boala']]
                existing['simptome'] = list(set(existing['simptome'] + item['simptome']))
                if 'cauze' in item:
                    existing['cauze'] = list(set(existing.get('cauze', []) + item['cauze']))
                if 'tratament' in item:
                    existing['tratament'] = list(set(existing.get('tratament', []) + item['tratament']))
                
        return list(merged.values())

    def extract_diseases(self, soup, source_type):
        """Extrage informații despre boli din HTML în funcție de sursa"""
        diseases = []
        
        # Cuvinte cheie pentru a filtra ce nu sunt boli
        exclude_keywords = [
            'health', 'intervention', 'population', 'demographic', 'behaviour',
            'policy', 'system', 'program', 'statistics', 'research'
        ]
        
        try:
            if source_type == "WHO":
                disease_elements = soup.find_all('a', {'data-entity-type': 'node'})
                print(f"WHO: Am găsit {len(disease_elements)} elemente")
                
                for element in disease_elements:
                    name = element.text.strip()
                    # Verificăm dacă este boală
                    if name and not any(keyword in name.lower() for keyword in exclude_keywords):
                        disease = {
                            "boala": name,
                            "simptome": [],
                            "cauze": [],
                            "tratament": [],
                            "url": f"https://www.who.int{element.get('href', '')}"
                        }
                        diseases.append(disease)
                        
            elif source_type == "MedlinePlus":
                # Actualizat pentru MedlinePlus
                disease_elements = soup.select('.section-body ul li a')
                print(f"MedlinePlus: Am găsit {len(disease_elements)} elemente")
                
                for element in disease_elements:
                    name = element.text.strip()
                    if name:
                        disease = {
                            "boala": name,
                            "simptome": [],
                            "cauze": [],
                            "tratament": [],
                            "url": f"https://medlineplus.gov{element.get('href', '')}"
                        }
                        diseases.append(disease)
                        
            elif source_type == "NIH":
                # Actualizat pentru NIH
                disease_elements = soup.select('.health-topics a')
                print(f"NIH: Am găsit {len(disease_elements)} elemente")
                
                for element in disease_elements:
                    name = element.text.strip()
                    if name:
                        disease = {
                            "boala": name,
                            "simptome": [],
                            "cauze": [],
                            "tratament": [],
                            "url": element.get('href', '')
                        }
                        diseases.append(disease)
            
            # Filtrăm lista finală
            diseases = [d for d in diseases if len(d['boala']) > 3]  # Eliminăm intrări prea scurte
            
            if diseases:
                print("\nPrimele 5 boli găsite:")
                for d in diseases[:5]:
                    print(f"- {d['boala']}")
                
        except Exception as e:
            print(f"Eroare la extragerea bolilor: {str(e)}")
            print(f"Tip eroare: {type(e).__name__}")
            
        return diseases

    def clean_knowledge_base(self):
        """Curăță baza de date de intrări care nu sunt boli"""
        try:
            # Încarcă datele existente
            with open('data/medical_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Cuvinte cheie pentru identificarea non-bolilor
            exclude_keywords = [
                'health', 'intervention', 'population', 'demographic', 'behaviour',
                'policy', 'system', 'program', 'statistics', 'research',
                'ageism', 'abuse', 'addiction', 'human', 'other'
            ]

            # Filtrăm datele
            cleaned_data = []
            removed_count = 0
            
            for item in data:
                if not any(keyword in item['boala'].lower() for keyword in exclude_keywords):
                    cleaned_data.append(item)
                else:
                    removed_count += 1
                    print(f"Șterg intrarea: {item['boala']}")

            # Salvăm datele curățate
            with open('data/medical_data.json', 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, ensure_ascii=False, indent=4)

            print(f"\nCurățare completă: am șters {removed_count} intrări care nu erau boli")
            print(f"Au rămas {len(cleaned_data)} boli în baza de date")

        except Exception as e:
            print(f"Eroare la curățarea bazei de date: {str(e)}")

if __name__ == "__main__":
    collector = MedicalDataCollector()
    collector.clean_knowledge_base()  # Curăță baza de date întâi
    collector.update_knowledge_base()  # Apoi adaugă date noi 