import datetime
import streamlit as st
import requests
from utils.validators import clean_text

class N8NHandler:
    def __init__(self):
        self.webhook_url = st.secrets["n8n_webhook_url"]

    def get_drive_url(self, file_id):
        """
        genera l'url di google drive per il file
        """
        return f"https://drive.google.com/file/d/{file_id}/view"

    def send_data(self, form_data, file_ids, summary_data):
        """
        Invia i dati del form a n8n
        """
        # pulizia dei dati del form da eventuali caratteri problematici
        cleaned_form_data = {k: clean_text(v) for k, v in form_data.items()}
        cleaned_summary_data = {k: clean_text(v) for k, v in summary_data.items()}
        
        payload = {
            "CATEGORIA": cleaned_summary_data["categoria"].upper(),
            "RAGIONE_SOCIALE": cleaned_form_data["ragione_sociale"],
            "TIPOLOGIA": cleaned_form_data["tipologia"],
            "TITOLO_PROGETTO": cleaned_form_data["titolo_progetto"],
            "NOME_REFERENTE": cleaned_form_data["nome_referente"],
            "COGNOME_REFERENTE": cleaned_form_data["cognome_referente"],
            "RUOLO": cleaned_form_data["ruolo"],
            "MAIL": cleaned_form_data["mail"],
            "TELEFONO": cleaned_form_data["telefono"],
            "AREA_TERAPEUTICA": cleaned_form_data["area_terapeutica"],
            "INFO_GIURIA": cleaned_summary_data["info_giuria"],
            "SINTESI_EBOOK": cleaned_summary_data["sintesi_ebook"],
            "OBIETTIVI": cleaned_summary_data["obiettivi"],
            "RISULTATI": cleaned_summary_data["risultati"],
            "PPT_URL": self.get_drive_url(file_ids["presentation"]),
            "DATA_SOTTOMISSIONE": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "CONSENSO_PRIVACY": 1 if cleaned_form_data["privacy_consent"] else 0,
            "CONSENSO_GIURIA": 1 if cleaned_form_data["jury_consent"] else 0,
            "CONSENSO_MARKETING": 1 if cleaned_form_data["marketing_consent"] else 0,
            "CONSENSO_AI": 1 if cleaned_form_data["ai_consent"] else 0
        }
            
        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 200:
                return True
            else:
                st.error(f"errore nell'invio dei dati: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            st.error(f"errore nella connessione al webhook: {str(e)}")
            return False 