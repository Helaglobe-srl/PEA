import streamlit as st
import requests

def clean_text(text):
    """
    Pulisce il testo da caratteri che potrebbero causare problemi nel JSON
    """
    if isinstance(text, str):
        text = text.replace('\\', '')
        text = text.replace('"', "'")
        text = text.replace('\n', ' ').replace('\r', '')
        return text
    return text

def get_drive_url(file_id):
    """
    Genera l'URL di Google Drive per il file
    """
    return f"https://drive.google.com/file/d/{file_id}/view"

def send_data_to_n8n(form_data, file_ids, summary_data):
    """
    Invia i dati del form a n8n
    """
    N8N_WEBHOOK_URL = st.secrets["n8n_webhook_url"]
    
    payload = {
        "CATEGORIA": summary_data["categoria"].upper(),
        "CANDIDATO": form_data["candidato"],
        "ENTE": form_data["ente"],
        "TITOLO_PROGETTO": form_data["titolo_progetto"],
        "NOME_REFERENTE": form_data["nome_referente"],
        "COGNOME_REFERENTE": form_data["cognome_referente"],
        "RUOLO": form_data["ruolo"],
        "MAIL": form_data["mail"],
        "TELEFONO": form_data["telefono"],
        "AREA_TERAPEUTICA": form_data["area_terapeutica"],
        "INFO_GIURIA": clean_text(summary_data["info_giuria"]),
        "SINTESI_EBOOK": clean_text(summary_data["sintesi_ebook"]),
        "OBIETTIVI": clean_text(summary_data["obiettivi"]),
        "RISULTATI": clean_text(summary_data["risultati"]),
        "PPT_URL": get_drive_url(file_ids["ppt"]),
        #"MARCHIO_URL": get_drive_url(file_ids["marchio"]),
        "CONSENSO_PRIVACY": 1 if form_data["privacy_consent"] else 0,
        "CONSENSO_GIURIA": 1 if form_data["jury_consent"] else 0,
        "CONSENSO_MARKETING": 1 if form_data["marketing_consent"] else 0
    }
        
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            return True
        else:
            st.error(f"Errore nell'invio dei dati: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"Errore nella connessione al webhook: {str(e)}")
        return False 