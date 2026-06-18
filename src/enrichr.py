import pandas as pd
import logging

class DataEnricher:
    @staticmethod
    def clean_website(url):
        if pd.isna(url):
            return ""
        url = str(url).lower().strip()
        url = url.replace("www.", "")
        if not url.startswith("http"):
            url = "https://" + url
        return url.split('/')[2] if len(url.split('/')) > 2 else url

    def enrich_dataset(self, raw_data):
        logging.info("Avvio arricchimento e normalizzazione dati...")
        if not raw_data:
            return pd.DataFrame()

        df = pd.DataFrame(raw_data)

        # 1. Pulizia stringhe e rimozione duplicati latenti
        df['company_name'] = df['company_name'].str.strip().str.title()
        df['website'] = df['website'].apply(self.clean_website)
        df.drop_duplicates(subset=['website'], keep='first', inplace=True)

        # 2. Logica di Keyword Matching per la categorizzazione Premium (AI Logic deterministica)
        tech_keywords = ['tech', 'ai', 'cloud', 'devops', 'software', 'forge', 'studio']
        
        def assign_premium_tier(row):
            name_lower = row['company_name'].lower()
            industry_lower = row['industry'].lower()
            
            if any(kw in name_lower or kw in industry_lower for kw in tech_keywords):
                return "SaaS & High-Tech B2B"
            return "Digital Service Provider"

        df['normalized_industry'] = df.apply(assign_premium_tier, axis=1)
        
        # Seleziona e ordina le colonne per l'output pronto alla vendita
        df = df[['company_name', 'normalized_industry', 'country', 'website', 'certification']]
        df.columns = ['Nome Azienda', 'Settore Target', 'Paese', 'Sito Web', 'Status Certificazione']
        
        return df
