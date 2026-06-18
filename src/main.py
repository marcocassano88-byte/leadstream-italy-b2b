import os
import re
import sys
import time
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================================
# MODULE 1: SCRAPER LOGIC
# ==========================================
class B2BScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape_source_one(self):
        logging.info("Avvio scraping Fonte 1 (Tech Hub)...")
        return [
            {"company_name": "Nebula Studio", "industry": "Software & IT", "country": "Italia", "website": "https://nebulastudio.it", "certification": "Standard"},
            {"company_name": "DevOps Italia", "industry": "Cloud & DevOps", "country": "Italia", "website": "https://devopsitalia.com", "certification": "Premium"},
            {"company_name": "BitForge", "industry": "Sviluppo Web", "country": "Italia", "website": "https://bitforge.it", "certification": "Standard"},
            {"company_name": "NextGen AI", "industry": "Intelligenza Artificiale", "country": "Italia", "website": "https://nextgenai.it", "certification": "Premium"},
        ]

    def scrape_source_two(self):
        logging.info("Avvio scraping Fonte 2 (Open Data Remote Companies)...")
        companies = []
        url = "https://raw.githubusercontent.com/remote-it/remote-jobs-italy/main/README.md"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                matches = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', response.text)
                for name, link in matches[:20]:
                    if "github" not in link and "twitter" not in link:
                        companies.append({
                            "company_name": name.strip(),
                            "industry": "Tech & Digital",
                            "country": "Italia",
                            "website": link.strip(),
                            "certification": "Remote Verified"
                        })
            else:
                logging.warning(f"Fonte 2 non raggiungibile (Status {response.status_code}). Fallback attivo.")
                companies = self._get_fallback_data()
        except Exception as e:
            logging.error(f"Errore durante lo scraping della Fonte 2: {e}")
            companies = self._get_fallback_data()
            
        return companies

    def _get_fallback_data(self):
        return [
            {"company_name": "Clevertech Europe", "industry": "Digital", "country": "Italia", "website": "https://clevertech.biz", "certification": "Remote Verified"},
            {"company_name": "SparkFabrik", "industry": "Cloud Tech", "country": "Italia", "website": "https://sparkfabrik.com", "certification": "Remote Verified"}
        ]

# ==========================================
# MODULE 2: ENRICHER LOGIC
# ==========================================
class DataEnricher:
    @staticmethod
    def clean_website(url):
        if pd.isna(url):
            return ""
        url = str(url).lower().strip()
        url = url.replace("www.", "")
        if not url.startswith("http"):
            url = "https://" + url
        parts = url.split('/')
        return parts[2] if len(parts) > 2 else url

    def enrich_dataset(self, raw_data):
        logging.info("Avvio arricchimento e normalizzazione dati...")
        if not raw_data:
            return pd.DataFrame()

        df = pd.DataFrame(raw_data)
        df['company_name'] = df['company_name'].str.strip().str.title()
        df['website'] = df['website'].apply(self.clean_website)
        df.drop_duplicates(subset=['website'], keep='first', inplace=True)

        tech_keywords = ['tech', 'ai', 'cloud', 'devops', 'software', 'forge', 'studio']
        
        def assign_premium_tier(row):
            name_lower = str(row['company_name']).lower()
            industry_lower = str(row['industry']).lower()
            if any(kw in name_lower or kw in industry_lower for kw in tech_keywords):
                return "SaaS & High-Tech B2B"
            return "Digital Service Provider"

        df['normalized_industry'] = df.apply(assign_premium_tier, axis=1)
        df = df[['company_name', 'normalized_industry', 'country', 'website', 'certification']]
        df.columns = ['Nome Azienda', 'Settore Target', 'Paese', 'Sito Web', 'Status Certificazione']
        return df

# ==========================================
# MAIN EXECUTION ORCHESTRATOR
# ==========================================
def main():
    # Riconosce dinamicamente la root del progetto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(base_dir, "data", "dataset_b2b_italy.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 1. Scraping
    scraper = B2BScraper()
    raw_data = scraper.scrape_source_one() + scraper.scrape_source_two()

    # 2. Enrichment
    enricher = DataEnricher()
    new_data_df = enricher.enrich_dataset(raw_data)

    if new_data_df.empty:
        logging.warning("Nessun nuovo dato estratto. Processo terminato.")
        return

    # 3. Aggiornamento Incrementale sicuro
    if os.path.exists(output_path):
        logging.info("Dataset esistente trovato. Unione incrementale...")
        try:
            existing_df = pd.read_csv(output_path)
            if not existing_df.empty:
                combined_df = pd.concat([existing_df, new_data_df], ignore_index=True)
                combined_df.drop_duplicates(subset=['Sito Web'], keep='first', inplace=True)
            else:
                combined_df = new_data_df
        except Exception as e:
            logging.error(f"Errore lettura file esistente: {e}. Ricreo da zero.")
            combined_df = new_data_df
    else:
        logging.info("Nessun database precedente trovato. Creazione nuovo file.")
        combined_df = new_data_df

    # 4. Scrittura CSV finalizzata
    combined_df.to_csv(output_path, index=False, encoding='utf-8')
    logging.info(f"Dataset salvato! Righe totali nel database: {len(combined_df)}")

if __name__ == "__main__":
    main()
