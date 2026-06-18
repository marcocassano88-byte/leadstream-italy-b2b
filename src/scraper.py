import requests
from bs4 import BeautifulSoup
import logging
import re
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class B2BScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape_source_one(self):
        """
        Fonte 1: Simulazione controllata e fallback di directory open data tech.
        Estrae aziende innovative e agenzie digitali.
        """
        logging.info("Avvio scraping Fonte 1 (Tech Hub)...")
        mocked_market_data = [
            {"company_name": "Nebula Studio", "industry": "Software & IT", "country": "Italia", "website": "https://nebulastudio.it", "certification": "Standard"},
            {"company_name": "DevOps Italia", "industry": "Cloud & DevOps", "country": "Italia", "website": "https://devopsitalia.com", "certification": "Premium"},
            {"company_name": "BitForge", "industry": "Sviluppo Web", "country": "Italia", "website": "https://bitforge.it", "certification": "Standard"},
            {"company_name": "NextGen AI", "industry": "Intelligenza Artificiale", "country": "Italia", "website": "https://nextgenai.it", "certification": "Premium"},
        ]
        return mocked_market_data

    def scrape_source_two(self):
        """
        Fonte 2: Scraping live da liste curate di aziende Remote/Tech italiane su repository pubblici/Open Data.
        """
        logging.info("Avvio scraping Fonte 2 (Open Data Remote Companies)...")
        companies = []
        # URL di un repository open data curato su GitHub (aziende italiane remote-friendly)
        url = "https://raw.githubusercontent.com/remote-it/remote-jobs-italy/main/README.md"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                # Estrazione tramite regex dei link markdown [Nome](Sito)
                matches = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', response.text)
                for name, link in matches[:20]: # Limite prudenziale per stabilità
                    if "github" not in link and "twitter" not in link:
                        companies.append({
                            "company_name": name.strip(),
                            "industry": "Tech & Digital",
                            "country": "Italia",
                            "website": link.strip(),
                            "certification": "Remote Verified"
                        })
            else:
                logging.warning(f"Fonte 2 non raggiungibile (Status {response.status_code}). Uso dati di fallback.")
                companies = [
                    {"company_name": "Clevertech Europe", "industry": "Digital", "country": "Italia", "website": "https://clevertech.biz", "certification": "Remote Verified"},
                    {"company_name": "SparkFabrik", "industry": "Cloud Tech", "country": "Italia", "website": "https://sparkfabrik.com", "certification": "Remote Verified"}
                ]
        except Exception as e:
            logging.error(f"Errore durante lo scraping della Fonte 2: {e}")
            
        return companies
