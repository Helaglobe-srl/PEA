import streamlit as st
import json
import datetime
import re
from google_drive_upload_handler import GoogleDriveUploadHandler

st.set_page_config(page_title="Iscrizione Completata", page_icon="✅")

col1, col2, col3 = st.columns([1,1,1])
with col2:
    st.image("images/LOGO_PEA.webp", use_container_width=True)
st.title("✅ Iscrizione completata con successo!")

# messaggio di conferma dell'iscrizione
st.info("""
    Grazie per aver candidato il tuo progetto!  

    Riceverai un'e-mail di conferma, con il riepilogo dei dati inseriti.  

    Controlla la tua casella di posta per tutti i dettagli. Se non ricevi l'email, ti preghiamo di controllare anche la cartella dello spam. 

    Per eventuali necessità scrivi a peaward@helaglobe.com o chiama al numero 055.4939527.  

    Grazie, 

    Il team Helaglobe 
""")

# Sezione feedback
st.markdown("## Il tuo feedback è importante per noi!")

with st.form("feedback_form"):
    # 1. Slider per gradimento
    gradimento = st.slider(
        "Quanto ti è piaciuto il processo di candidatura?", 
        min_value=1, 
        max_value=5, 
        value=5
    )
    
    # 2. Opzione si/no
    adozione = st.radio(
        "Adotteresti questo sistema per i tuoi form?",
        options=["Sì", "No"]
    )
    
    # 3. Campo libero per suggerimenti
    suggerimenti = st.text_area("Hai suggerimenti?")
    
    submit_button = st.form_submit_button("Invia feedback")
    
    if submit_button:
        try:
            # ottengo i dati del candidato dalla session state settati nella pagina di candidatura
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            form_data = st.session_state.get("form_data", {})
            if form_data is None:
                form_data = {}
            
            # struttura del file txt di feedback
            feedback_content = {
                "timestamp": timestamp,
                "feedback": {
                    "gradimento": gradimento,
                    "adozione": adozione,
                    "suggerimenti": suggerimenti
                },
                "dati_candidato": {
                    "nome": form_data.get("nome_referente", "utente_anonimo"),
                    "cognome": form_data.get("cognome_referente", "anonimo"),
                    "azienda": form_data.get("ragione_sociale", "n/a"),
                    "email": form_data.get("mail", "n/a")
                }
            }
            
            # converto in JSON
            feedback_json = json.dumps(feedback_content, indent=4, ensure_ascii=False)
            
            # nome dell'azienda per il nome del file
            azienda = feedback_content["dati_candidato"]["azienda"]
            azienda_clean = re.sub(r'[^\w]', '_', azienda).lower()
            if not azienda_clean:
                azienda_clean = "azienda_anonima"
            file_name = f"feedback_{azienda_clean}.txt"
            
            # carico su Google Drive il file di feedback
            drive_handler = GoogleDriveUploadHandler()
            folder_id = st.secrets.get("drive_feedback_folder_id")            
            file_id = drive_handler.upload_text_content(file_name, feedback_json, folder_id)
            
            st.success("Grazie per il tuo feedback!")
            
        except Exception as e:
            st.error(f"Si è verificato un errore durante l'invio del feedback: {str(e)}")
            st.exception(e)

# bottone Torna alla Home
col1, col2, col3 = st.columns([1,1,1])
with col2:
    if st.button("Candida un altro progetto"):
        # resetta tutte le variabili di sessione
        for key in list(st.session_state.keys()): 
            del st.session_state[key]
        st.switch_page("app.py") 