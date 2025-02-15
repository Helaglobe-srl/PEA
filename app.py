import os 
import streamlit as st
from upload_handler import authenticate_drive, upload_to_drive
from ppt_analyzer import analyze_ppt
from n8n_handler import send_data_to_n8n
import tempfile
import time
from email_handler import send_confirmation_email
from utils.validators import validate_phone_number, validate_email

if "file_upload_ids" not in st.session_state:
    st.session_state["file_upload_ids"] = None
if "extracted_content" not in st.session_state:
    st.session_state["extracted_content"] = None
if "analysis_complete" not in st.session_state:
    st.session_state["analysis_complete"] = False
if "form_data" not in st.session_state:
    st.session_state["form_data"] = None
if "reset_uploader" not in st.session_state:
    st.session_state["reset_uploader"] = False
if "files_uploaded_to_drive" not in st.session_state:
    st.session_state["files_uploaded_to_drive"] = False
if "ppt_file_content" not in st.session_state:
    st.session_state["ppt_file_content"] = None
if "marchio_content" not in st.session_state:
    st.session_state["marchio_content"] = None
if "marchio_type" not in st.session_state:
    st.session_state["marchio_type"] = None

FOLDER_ID = st.secrets["drive_folder_id"]

st.set_page_config(
    page_title="Iscrizione PEA",
    page_icon="📊",
)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("images/logo_pea.jpg", width=200)


st.markdown("""
    <h1 style='text-align: center; margin-bottom: 0;'>Form di Iscrizione</h1>
    <h2 style='text-align: center; margin-top: 0; margin-bottom: 0;'>Patient Engagement Award</h2>
    <h3 style='text-align: center; color: #666666; margin-top: 0; margin-bottom: 40px;'>3rd Edition</h3>
    """, unsafe_allow_html=True)

# Aree Terapeutiche
AREE_TERAPEUTICHE = [
    "Allergologia e Immunologia",
    "Cardiologia",
    "Dermatologia",
    "Diabetologia",
    "Ematologia",
    "Endocrinologia",
    "Gastroenterologia",
    "Geriatria",
    "Ginecologia",
    "Malattie Infettive",
    "Malattie Rare",
    "Medicina Interna",
    "Nefrologia",
    "Neurologia",
    "Oncologia",
    "Ortopedia",
    "Pediatria",
    "Pneumologia",
    "Psichiatria",
    "Reumatologia",
    "Urologia"
]

# campi obbligatori
candidato = st.text_input("Candidato *")
titolo_progetto = st.text_input("Titolo Progetto *")
col1, col2 = st.columns(2)
with col1:
    nome_referente = st.text_input("Nome Referente *")
with col2:
    cognome_referente = st.text_input("Cognome Referente *")
ruolo = st.text_input("Ruolo *")
mail = st.text_input("Mail *")
telefono = st.text_input("Telefono *")
area_terapeutica = st.selectbox(
    "Area Terapeutica *",
    options=AREE_TERAPEUTICHE,
    index=AREE_TERAPEUTICHE.index("Oncologia") if "Oncologia" in AREE_TERAPEUTICHE else 0,
    help="Seleziona o cerca un'area terapeutica"
)

# messaggi di validazione telefono e email
if mail and not validate_email(mail):
    st.error("Per favore inserisci un indirizzo email valido (esempio: nome@dominio.com)")
if telefono and not validate_phone_number(telefono):
    st.error("Per favore inserisci un numero di telefono valido (esempio: 3401234567 o +39 340 1234567)")

# sezione di caricamento files
st.subheader("Caricamento File")

# - Logo
marchio_file = st.file_uploader(
    "marchio aziendale in formato vettoriale o in alta risoluzione *", 
    type=["png", "jpg", "jpeg"],
    help="Carica il marchio aziendale",
    key="marchio_uploader"
)

# - Immagine di progetto
image_file = st.file_uploader(
    "Immagine rappresentativa del progetto (1920x1080 px) *", 
    type=["png", "jpg", "jpeg"],
    help="Carica un'immagine in formato 1920x1080 pixel",
    key="image_uploader"
)

# - PPT 
key = "file_uploader_" + str(int(time.time())) if st.session_state["reset_uploader"] else "file_uploader"
ppt_file = st.file_uploader(
    "Presentazione del progetto *", 
    type=["ppt", "pptx"],
    help="Carica un file PowerPoint",
    key=key
)

st.markdown("<span style='color: red; font-size: 0.8em'>* Campi obbligatori</span>", unsafe_allow_html=True)

# controllo che tutti i file siano stati caricati
if not all([marchio_file, image_file, ppt_file]):
    st.warning("Carica tutti i file richiesti prima di procedere.")

# salva i file caricati in sessione
if marchio_file:
    st.session_state["marchio_content"] = marchio_file.getvalue()
    st.session_state["marchio_type"] = marchio_file.name.split('.')[-1]
if image_file:
    st.session_state["image_content"] = image_file.getvalue()
    st.session_state["image_type"] = image_file.name.split('.')[-1]

# 1. analisi della presentazione
if st.button("Carica Files", disabled=not all([marchio_file, image_file, ppt_file])):
    with st.spinner("Analisi della presentazione in corso..."):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ppt_file.name.split('.')[-1]}") as temp_file:
                temp_file.write(ppt_file.getbuffer())
                temp_file_path = temp_file.name

            summary_data = analyze_ppt(temp_file_path)
            os.unlink(temp_file_path)
            
            st.session_state["extracted_content"] = summary_data
            st.session_state["analysis_complete"] = True
            st.session_state["ppt_file_content"] = ppt_file.getvalue()
            
            st.success("✅ Presentazione analizzata con successo!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Si è verificato un errore durante l'analisi: {str(e)}")

# 2. mostra i dati estratti e il bottone Sottometti Iscrizione solo dopo che l'analisi è completa
if st.session_state["analysis_complete"]:
    st.subheader("Dati estratti dalla presentazione")
    
    st.info("""
        I campi seguenti sono stati estratti automaticamente dalla presentazione, puoi modificarli se necessario. 
        Una volta verificato che i dati siano corretti, premi il pulsante 'Sottometti Iscrizione' per completare la procedura.
    """)
    
    categoria = st.text_area(
        "Categoria:",
        value=st.session_state["extracted_content"]["categoria"],
        height=100
    )
    
    descrizione = st.text_area(
        "Descrizione Progetto:",
        value=st.session_state["extracted_content"]["descrizione"],
        height=300
    )
    
    obiettivo = st.text_area(
        "Obiettivo Progetto:",
        value=st.session_state["extracted_content"]["obiettivo"],
        height=300
    )
    
    # controlla se tutti i campi obbligatori sono compilati
    required_fields = {
        "Candidato": candidato,
        "Titolo Progetto": titolo_progetto,
        "Nome Referente": nome_referente,
        "Cognome Referente": cognome_referente,
        "Ruolo": ruolo,
        "Mail": mail,
        "Telefono": telefono,
        "Area Terapeutica": area_terapeutica
    }
    
    empty_fields = [field for field, value in required_fields.items() if not value.strip()]
    if empty_fields:
        st.error(f"Per favore compila i seguenti campi obbligatori: {', '.join(empty_fields)}")
    elif not validate_email(mail):
        st.error("Per favore correggi l'indirizzo email prima di procedere")
    elif not validate_phone_number(telefono):
        st.error("Per favore correggi il numero di telefono prima di procedere")
    else:
        if st.button("Sottometti Iscrizione"):
            with st.spinner("Iscrizione in corso..."):
                try:
                    # 3. prima di inviare i dati a n8n, si carica la presentazione su GDrive
                    if not st.session_state["files_uploaded_to_drive"]:
                        current_date = time.strftime("%Y%m%d")
                        clean_name = lambda s: s.lower().replace(" ", "_")
                        base_filename = f"{current_date}_{clean_name(candidato)}_{clean_name(titolo_progetto)}"
                        
                        try:
                            service = authenticate_drive()
                            file_uploads = [
                                ("ppt", "_presentazione", st.session_state["ppt_file_content"]),
                                ("marchio", "_marchio", st.session_state["marchio_content"]),
                                ("image", "_immagine", st.session_state["image_content"])
                            ]

                            file_ids = {}
                            for file_key, suffix, content in file_uploads:
                                if content is None:
                                    st.error(f"Per favore carica il file {file_key} prima di procedere")
                                    continue
                                
                                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                                    temp_file.write(content)
                                    temp_path = temp_file.name
                                
                                # aggiungo un suffisso univoco al nome del file (_presentazione, _marchio, _immagine)
                                if file_key == "ppt":
                                    filename = f"{base_filename}{suffix}.pptx"
                                elif file_key == "marchio":
                                    filename = f"{base_filename}{suffix}.{st.session_state['marchio_type']}"
                                else:  
                                    filename = f"{base_filename}{suffix}.{st.session_state['image_type']}"
                                
                                try:
                                    file_ids[file_key] = upload_to_drive(service, filename, temp_path, FOLDER_ID)
                                    os.unlink(temp_path)
                                except Exception as e:
                                    st.error(f"Error uploading {file_key}: {str(e)}")

                            st.session_state["files_uploaded_to_drive"] = True
                            st.session_state["file_upload_ids"] = file_ids
                            
                        except Exception as e:
                            st.error(f"Si è verificato un errore durante il caricamento dei file: {str(e)}")
                            st.stop()

                    # 4. infine si invia i dati a n8n che li salva come nuovo record nel google sheet iscrizioni
                    form_data = {
                        "candidato": candidato,
                        "titolo_progetto": titolo_progetto,
                        "nome_referente": nome_referente,
                        "cognome_referente": cognome_referente,
                        "ruolo": ruolo,
                        "mail": mail,
                        "telefono": telefono,
                        "area_terapeutica": area_terapeutica
                    }
                    
                    summary_data = {
                        "categoria": categoria,
                        "descrizione": descrizione,
                        "obiettivo": obiettivo
                    }
                    
                    if send_data_to_n8n(form_data, st.session_state["file_upload_ids"], summary_data):
                                                
                        # invio email di conferma
                        if send_confirmation_email(form_data["mail"], form_data):
                            st.balloons()
                            # resetta tutte le variabili di sessione
                            st.session_state["analysis_complete"] = False
                            st.session_state["extracted_content"] = None
                            st.session_state["ppt_file_content"] = None
                            st.session_state["reset_uploader"] = True
                            st.session_state["files_uploaded_to_drive"] = False
                            st.session_state["file_upload_ids"] = None
                            
                            # vai alla pagina di conferma iscrizione
                            st.success("✅ Iscrizione completata con successo!")
                            time.sleep(1)
                            st.switch_page("pages/success.py")
                        else:
                            st.warning("Iscrizione completata ma si è verificato un errore nell'invio dell'email di conferma.")
                except Exception as e:
                    st.error(f"Si è verificato un errore durante l'iscrizione: {str(e)} \n Contattare l'Amministratore {st.secrets['email']['sender']}")