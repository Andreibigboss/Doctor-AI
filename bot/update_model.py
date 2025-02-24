from scraper import MedicalScraper
import os
import json
import traceback  # Adăugăm pentru a vedea stack trace-ul complet

def update_model():
    print("\n=== Starting update process ===")
    
    try:
        # Verificăm dacă există directorul pentru model
        if not os.path.exists('model'):
            print("Creating model directory...")
            os.makedirs('model')
        
        # Verificăm dacă există directorul pentru date
        if not os.path.exists('data'):
            print("Creating data directory...")
            os.makedirs('data')
        
        # Inițializăm scraper-ul și obținem date noi
        print("\n=== Initializing scraper ===")
        scraper = MedicalScraper()
        print("\n=== Starting scraping and translation process ===")
        try:
            data = scraper.scrape_and_translate()
            print(f"\nScraped {len(data)} articles successfully")
        except Exception as e:
            print(f"\nError during scraping: {str(e)}")
            print("\nFull error trace:")
            print(traceback.format_exc())
            return
        
        print("\n=== Starting model training ===")
        try:
            import train
            print("\nModel training completed successfully")
        except Exception as e:
            print(f"\nError during training: {str(e)}")
            print("\nFull error trace:")
            print(traceback.format_exc())
            return
        
        print("\n=== Update process finished successfully! ===")
        
        # Așteaptă input de la utilizator înainte de a închide
        input("\nPress Enter to close...")

    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        print("\nFull error trace:")
        print(traceback.format_exc())
        input("\nPress Enter to close...")

if __name__ == "__main__":
    update_model() 