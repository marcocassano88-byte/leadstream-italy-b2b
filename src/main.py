import os
import sys
import logging
import pandas as pd

# CORREZIONE PERCORSI CRITICA: Deve essere in cima a tutto prima degli altri import
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.scraper import B2BScraper
from src.enricher import DataEnricher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Definiamo il percorso assoluto del file CSV basato sulla cartella principale del progetto
    output_path = os.path.join(BASE_DIR, "data", "dataset_b2b_italy.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

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

    # 3. Aggiornamento Incrementale
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
