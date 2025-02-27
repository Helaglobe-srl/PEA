import base64
import os 
import streamlit as st
import tempfile
import time
from utils.validators import validate_phone_number, validate_email
from utils.constants import AREE_TERAPEUTICHE, TIPOLOGIE, CATEGORIE
from google_drive_upload_handler import GoogleDriveUploadHandler
from email_handler import EmailHandler
from n8n_handler import N8NHandler
from presentation_analyzer import PresentationAnalyzer

FOLDER_ID = st.secrets["drive_folder_id"]

drive_handler = GoogleDriveUploadHandler()
email_handler = EmailHandler()
n8n_handler = N8NHandler()
presentation_analyzer = PresentationAnalyzer()

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
if "presentation_content" not in st.session_state:
    st.session_state["presentation_content"] = None
if "marchio_content" not in st.session_state:
    st.session_state["marchio_content"] = None
if "marchio_type" not in st.session_state:
    st.session_state["marchio_type"] = None

st.set_page_config(
    page_title="Iscrizione PEA 2025",
    page_icon="images/LOGO_PEA_ICO.ico",
)

col1, col2, col3 = st.columns([1,1,1])
with col2:
    st.image("images/LOGO_PEA.webp", width=200, use_container_width=True)

st.markdown("""
    <h1 style='text-align: center; margin-bottom: 0;'>Form di Iscrizione</h1>
    <h2 style='text-align: center; margin-top: 0; margin-bottom: 0;'>Patient Engagement Award</h2>
    <h3 style='text-align: center; color: #666666; margin-top: 0; margin-bottom: 40px;'>3rd Edition</h3>
    """, unsafe_allow_html=True)

st.markdown("<span style='color: red; font-size: 0.8em'>* Campi obbligatori</span>", unsafe_allow_html=True)

# campi obbligatori
ragione_sociale = st.text_input("Ragione Sociale *")
tipologia = st.selectbox(
    "Tipologia Candidato *",
    options=TIPOLOGIE,
    index=TIPOLOGIE.index("Azienda Farmaceutica"), 
    help="Seleziona la tipologia"
)
# mostro campo di testo extra per tipologia personalizzato se selezionato "Altro"
if tipologia == "Altro":
    tipologia_custom = st.text_input(
        "Specifica la Tipologia *",
        help="Inserisci la tipologia non presente nella lista"
    )
    # se l'utente ha inserito una tipologia personalizzata, usa quella invece di "Altro"
    if tipologia_custom:
        tipologia = tipologia_custom
    else:
        st.error("Per favore specifica la Tipologia")
        tipologia = ""  # imposto a stringa vuota per far fallire la validazione dei campi obbligatori in fondo alla pagina

# titolo progetto
titolo_progetto = st.text_input("Titolo Progetto *")

# Area Terapeutica multi-selezione
area_terapeutica_selection = st.multiselect(
    "Area Terapeutica Progetto *",
    options=AREE_TERAPEUTICHE,
    #default=["Oncologia"] if "Oncologia" in AREE_TERAPEUTICHE else None,
    placeholder="Seleziona una o più aree terapeutiche",
    help="Seleziona una o più aree terapeutiche"
)

# salvo la selezione originale per il controllo di "Altro"
has_altro = "Altro" in area_terapeutica_selection
area_terapeutica = area_terapeutica_selection.copy()

# mostra campo di testo extra per area terapeutica personalizzata se "Altro" è tra le selezioni
if "Altro" in area_terapeutica:
    area_terapeutica_custom = st.text_input(
        "Specifica l'Area Terapeutica *",
        help="Inserisci l'area terapeutica non presente nella lista"
    )
    # se l'utente seleziona un'area personalizzata (Altro), sostituisci "Altro" con quella
    if area_terapeutica_custom:
        area_terapeutica = [at for at in area_terapeutica if at != "Altro"] + [area_terapeutica_custom]
    else:
        st.error("Per favore specifica l'Area Terapeutica personalizzata")
        area_terapeutica = [at for at in area_terapeutica if at != "Altro"]  # rimuovo "Altro" se non è specificata l'area custom

# converto la lista in stringa
area_terapeutica_string = ", ".join(area_terapeutica) if area_terapeutica else ""

# mostro errore se nessuna area terapeutica è selezionata (e "Altro" non è stato selezionato)
if not area_terapeutica and not has_altro:
    st.error("Per favore seleziona almeno un'Area Terapeutica")

# nome e cognome referente
col1, col2 = st.columns(2)
with col1:
    nome_referente = st.text_input("Nome Referente *")
with col2:
    cognome_referente = st.text_input("Cognome Referente *")
ruolo = st.text_input("Ruolo *")

# mail e conferma mail
col1, col2 = st.columns(2)
with col1:
    mail = st.text_input("Mail *").lower()
with col2:
    mail_confirm = st.text_input("Conferma Mail *").lower()

# validazione mail e conferma mail
if mail and mail_confirm:
    if mail != mail_confirm:
        st.error("Gli indirizzi email non corrispondono")
    elif not validate_email(mail):
        st.error("Per favore inserisci un indirizzo email valido (esempio: nome@dominio.com)")

telefono = st.text_input("Telefono *")

# messaggi di validazione telefono e email
if telefono and not validate_phone_number(telefono):
    st.error("Per favore inserisci un numero di telefono valido (esempio: 3401234567 o +39 340 1234567)")

# GIF robot 
with open("images/hela.gif", "rb") as f:
    data = f.read()
    encoded = base64.b64encode(data).decode()
st.markdown(f"""
<div style="display: flex; justify-content: center;">
    <img src="data:image/gif;base64,{encoded}" style="width: 400px; height: auto; margin: 20px 0;">
</div>
""", unsafe_allow_html=True)

# sezione di caricamento files
st.subheader("Caricamento File")

# - Logo
marchio_file = st.file_uploader(
    "Logo aziendale in alta risoluzione o vettoriale *", 
    type=["png", "jpg", "jpeg", "pdf", "svg"],
    help="Carica il logo aziendale in alta risoluzione o vettoriale, formati accettati: png, jpg, jpeg, pdf, svg",
    key="marchio_uploader"
)

# - Immagine di progetto
image_file = st.file_uploader(
    "Immagine rappresentativa del progetto (1920x1080 px) *", 
    type=["png", "jpg", "jpeg"],
    help="Carica un'immagine in formato 1920x1080 pixel",
    key="image_uploader"
)

# - Presentazione
key = "file_uploader_" + str(int(time.time())) if st.session_state["reset_uploader"] else "file_uploader"
presentation_file = st.file_uploader(
    "Presentazione del progetto *", 
    type=["ppt", "pptx", "pdf"],
    help="Carica un file PowerPoint o PDF",
    key=key
)

# controllo che tutti i file siano stati caricati
if not all([marchio_file, image_file, presentation_file]):
    st.warning("Carica tutti i file richiesti prima di procedere.")

# salva i file caricati in sessione
if marchio_file:
    st.session_state["marchio_content"] = marchio_file.getvalue()
    st.session_state["marchio_type"] = marchio_file.name.split('.')[-1]
if image_file:
    st.session_state["image_content"] = image_file.getvalue()
    st.session_state["image_type"] = image_file.name.split('.')[-1]


# 1. analisi della presentazione
if st.button("Carica Files", disabled=not all([marchio_file, image_file, presentation_file])):
    with st.spinner("Analisi della presentazione in corso..."):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{presentation_file.name.split('.')[-1]}") as temp_file:
                temp_file.write(presentation_file.getbuffer())
                temp_file_path = temp_file.name

            summary_data = presentation_analyzer.analyze(temp_file_path)
            os.unlink(temp_file_path)
            
            st.session_state["extracted_content"] = summary_data
            st.session_state["analysis_complete"] = True
            st.session_state["presentation_content"] = presentation_file.getvalue()
            
            st.success("✅ Presentazione analizzata con successo!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Si è verificato un errore durante l'analisi: {str(e)}")

# 2. mostra i dati estratti e il bottone Sottometti Iscrizione solo dopo che l'analisi è completa
if st.session_state["analysis_complete"]:
    st.subheader("Dati estratti dalla presentazione")
    
    st.info("""
        Abbiamo analizzato i contenuti che hai condiviso con noi e, sulla base degli obiettivi e dei risultati che ci hai indicato, crediamo che il tuo progetto possa essere descritto come leggerai qui di seguito.
        
        Ogni campo riprende i contenuti riportati nella presentazione, ma puoi modificare se necessario e, una volta che avrai verificato che tutto sia corretto, premi il pulsante 'Sottometti Iscrizione' per completare la procedura.
        
        Grazie! 
    """)
    
    # categoria
    suggested_category = st.session_state["extracted_content"]["categoria"]
    default_index = 0
    for i, cat in enumerate(CATEGORIE):
        if cat.upper() == suggested_category.upper():
            default_index = i
            break
            
    categoria = st.selectbox(
        "Categoria:",
        options=CATEGORIE,
        index=default_index,
        help="Seleziona la categoria del progetto"
    )
    
    # salvo info_giuria per salvarla nel google sheet ma non viene mostrata nella pagina
    info_giuria = st.session_state["extracted_content"]["info_giuria"]
    
    sintesi_ebook = st.text_area(
        "Sintesi informazioni per l'Ebook (max 5 frasi):",
        value=st.session_state["extracted_content"]["sintesi_ebook"],
        height=200,
        help="Questa sintesi verrà utilizzata per l'Ebook. Max 5 frasi."
    )
    
    obiettivi = st.text_area(
        "Obiettivi:",
        value=st.session_state["extracted_content"]["obiettivi"],
        height=200,
        help="Lista degli obiettivi principali del progetto"
    )
    
    risultati = st.text_area(
        "Risultati:",
        value=st.session_state["extracted_content"]["risultati"],
        height=200,
        help="Lista dei risultati principali raggiunti"
    )
    
    # Checkbox per i consensi
    st.subheader("Privacy e Consensi")
    
    ai_consent = st.checkbox(
        "Acconsento all'utilizzo di tecnologie di Intelligenza Artificiale per l'analisi della presentazione, " +
        "esclusivamente allo scopo di velocizzare il processo di iscrizione. I contenuti non verranno in alcun modo " +
        "utilizzati per l'addestramento di modelli e saranno trattati nel rispetto del GDPR 2016/679 e della " +
        "normativa vigente in materia di protezione dei dati personali *"
    )
    
    privacy_consent = st.checkbox(
        "Acconsento al " + 
        "[trattamento dei dati personali](https://www.helaglobe.com/privacy-policy)" +
        " ai sensi degli articoli 13-14 del GDPR 2016/679 *"
    )
    
    jury_consent = st.checkbox(
        "Autorizzo HELAGLOBE S.R.L. a condividere con la giuria la documentazione presentata *"
    )
    
    marketing_consent = st.checkbox(
        "Acconsento a ricevere novità e informazioni sui progetti di Helaglobe"
    )
    
    # controlla se tutti i campi obbligatori sono compilati
    required_fields = {
        "Ragione Sociale": ragione_sociale,
        "Tipologia": tipologia,
        "Titolo Progetto": titolo_progetto,
        "Nome Referente": nome_referente,
        "Cognome Referente": cognome_referente,
        "Ruolo": ruolo,
        "Mail": mail,
        "Telefono": telefono,
        "Area Terapeutica": area_terapeutica_string
    }
    
    empty_fields = [field for field, value in required_fields.items() if not value.strip()]
    if empty_fields:
        st.error(f"Per favore compila i seguenti campi obbligatori: {', '.join(empty_fields)}")
    elif not validate_email(mail):
        st.error("Per favore correggi l'indirizzo email prima di procedere")
    elif mail != mail_confirm:
        st.error("Gli indirizzi email non corrispondono")
    elif not validate_phone_number(telefono):
        st.error("Per favore correggi il numero di telefono prima di procedere")
    elif not privacy_consent or not jury_consent or not ai_consent:
        st.error("Per favore accetta i consensi obbligatori per procedere (Privacy, Autorizzazione giuria e Analisi AI)")
    else:
        if st.button("Sottometti Iscrizione"):
            with st.spinner("Iscrizione in corso..."):
                try:
                    # 3. prima di inviare i dati a n8n, si carica la presentazione su GDrive
                    if not st.session_state["files_uploaded_to_drive"]:
                        clean_name = lambda s: s.lower().replace(" ", "_")
                        base_filename = f"{clean_name(ragione_sociale)}_{clean_name(titolo_progetto)}"
                        
                        try:
                            file_uploads = [
                                ("presentation", "_presentazione", st.session_state["presentation_content"]),
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
                                
                                # in base al tipo di file, aggiungo un suffisso univoco al nome del file (_presentazione, _marchio, _immagine)
                                if file_key == "presentation":
                                    original_ext = presentation_file.name.split('.')[-1].lower()
                                    filename = f"{base_filename}{suffix}.{original_ext}"
                                elif file_key == "marchio":
                                    filename = f"{base_filename}{suffix}.{st.session_state['marchio_type']}"
                                else:  
                                    filename = f"{base_filename}{suffix}.{st.session_state['image_type']}"
                                
                                try:
                                    file_ids[file_key] = drive_handler.upload_file(filename, temp_path, FOLDER_ID)
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
                        "ragione_sociale": ragione_sociale,
                        "tipologia": tipologia,
                        "titolo_progetto": titolo_progetto,
                        "nome_referente": nome_referente,
                        "cognome_referente": cognome_referente,
                        "ruolo": ruolo,
                        "mail": mail,
                        "telefono": telefono,
                        "area_terapeutica": area_terapeutica_string,
                        "privacy_consent": privacy_consent,
                        "jury_consent": jury_consent,
                        "marketing_consent": marketing_consent,
                        "ai_consent": ai_consent
                    }
                    
                    summary_data = {
                        "categoria": categoria,
                        "info_giuria": info_giuria,
                        "sintesi_ebook": sintesi_ebook,
                        "obiettivi": obiettivi,
                        "risultati": risultati
                    }
                    
                    # invio dati a n8n
                    if n8n_handler.send_data(form_data, st.session_state["file_upload_ids"], summary_data):
                        
                        # invio email di conferma
                        email_result = email_handler.send_confirmation_email(
                            form_data["mail"], 
                            form_data, 
                            st.session_state["file_upload_ids"]
                        )
                        if email_result is True:
                            st.balloons()
                            # resetta tutte le variabili di sessione
                            st.session_state["analysis_complete"] = False
                            st.session_state["extracted_content"] = None
                            st.session_state["presentation_content"] = None
                            st.session_state["reset_uploader"] = True
                            st.session_state["files_uploaded_to_drive"] = False
                            st.session_state["file_upload_ids"] = None
                            
                            # vai alla pagina di conferma iscrizione
                            st.success("✅ Iscrizione completata con successo!")
                            time.sleep(1)
                            st.switch_page("pages/success.py")
                        else:
                            # mostra un messaggio di warning con l'errore specifico sul mancato recapito mail
                            st.warning(f"""
                                La tua iscrizione è stata registrata correttamente, ma non è stato possibile inviare l'email di conferma.
                                
                                Motivo: {email_result}
                                
                                Per favore contatta il supporto all'indirizzo {st.secrets['email']['sender']} per ricevere assistenza.
                            """)
                except Exception as e:
                    st.error(f"Si è verificato un errore durante l'iscrizione: {str(e)} \n Contattare l'Amministratore {st.secrets['email']['sender']}")