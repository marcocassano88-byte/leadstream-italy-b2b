import os
import sys
import logging
import pandas as pd

# Fix definitivo per i percorsi: aggiunge la cartella principale del progetto al path di Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import B2BScraper
from src.enricher import DataEnricher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    output_path = "data/dataset_b2b_italy.csv"
    os.makedirs("data", exist_ok=True)

    # 1. Esecuzione Scraper
    scraper = B2BScraper()
    data_source_1 = scraper.scrape_source_one()
    data_source_2 = scraper.scrape_source_two()
    
    combined_raw_data = data_source_1 + data_source_2

    # 2. Esecuzione Enrichment
    enricher = DataEnricher()
    new_data_df = enricher.enrich_dataset(combined_raw_data)

    if new_data_df.empty:
        logging.warning("Nessun nuovo dato estratto. Processo terminato.")
        return

    # 3. Aggiornamento Incrementale (No Sovrascrittura Distruttiva)
    if os.path.exists(output_path):
        logging.info("Dataset esistente trovato. Unione in corso...")
        try:
            existing_df = pd.read_csv(output_path)
            if not existing_df.empty:
                combined_df = pd.concat([existing_df, new_data_df], ignore_index=True)
                combined_df.drop_duplicates(subset=['Sito Web'], keep='first', inplace=True)
            else:
                combined_df = new_data_df
        except Exception as e:
            logging.error(f"Errore durante la lettura del dataset esistente: {e}. Creo un nuovo file.")
            combined_df = new_data_df
    else:
        logging.info("Nessun dataset precedente trovato. Creazione nuovo file.")
        combined_df = new_data_df

    # 4. Salvataggio Finale Production-Ready
    combined_df.to_csv(output_path, index=False, encoding='utf-8')
    logging.info(f"Dataset aggiornato con successo! Righe totali: {len(combined_df)}")

if __name__ == "__main__":
    main()
