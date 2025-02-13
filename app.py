import os 
import streamlit as st
from upload_handler import authenticate_drive, upload_to_drive
from ppt_analyzer import analyze_ppt
from n8n_handler import send_data_to_n8n
import tempfile
import time

if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
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
if "file_uploaded" not in st.session_state:
    st.session_state["file_uploaded"] = False

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
area_terapeutica = st.selectbox(
    "Area Terapeutica *",
    options=AREE_TERAPEUTICHE,
    index=AREE_TERAPEUTICHE.index("Oncologia") if "Oncologia" in AREE_TERAPEUTICHE else 0,
    help="Seleziona o cerca un'area terapeutica"
)

st.markdown("<span style='color: red; font-size: 0.8em'>* Campi obbligatori</span>", unsafe_allow_html=True)

# ppt uploader
key = "file_uploader_" + str(int(time.time())) if st.session_state["reset_uploader"] else "file_uploader"
uploaded_file = st.file_uploader(
    "Carica la tua presentazione", 
    type=["ppt", "pptx"],
    help="Carica un file PowerPoint",
    key=key
)

# 1. dopo aver caricato la presentazione, si preme il bottone Analizza Presentazione
if st.button("Analizza Presentazione", disabled=not uploaded_file):
    with st.spinner("Analisi della presentazione in corso..."):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                temp_file_path = temp_file.name

            # 2. analizza la presentazione senza caricare su Drive
            summary_data = analyze_ppt(temp_file_path)
            
            os.unlink(temp_file_path)
            
            st.session_state["extracted_content"] = summary_data
            st.session_state["analysis_complete"] = True
            st.session_state["ppt_content"] = uploaded_file.getvalue()  # salva il contenuto della presentazione temporaneamente
            
            st.success("✅ Presentazione analizzata con successo!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Si è verificato un errore durante l'analisi: {str(e)}")

# mostra i dati estratti e il bottone Sottometti Iscrizione solo dopo che l'analisi è completa
if st.session_state["analysis_complete"]:
    st.subheader("Dati estratti dalla presentazione")
    
    categoria = st.text_area(
        "Categoria:",
        value=st.session_state["extracted_content"]["categoria"],
        height=100
    )
    
    descrizione = st.text_area(
        "Descrizione Progetto:",
        value=st.session_state["extracted_content"]["descrizione"],
        height=200
    )
    
    obiettivo = st.text_area(
        "Obiettivo Progetto:",
        value=st.session_state["extracted_content"]["obiettivo"],
        height=100
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
    else:
        if st.button("Sottometti Iscrizione"):
            try:
                # 3. prima di inviare i dati a n8n, si carica la presentazione su GDrive
                if not st.session_state["file_uploaded"]:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as temp_file:
                        temp_file.write(st.session_state["ppt_content"])
                        temp_file_path = temp_file.name

                    service = authenticate_drive()
                    original_filename = uploaded_file.name
                    file_id = upload_to_drive(service, original_filename, temp_file_path, FOLDER_ID)
                    st.session_state["file_uploaded"] = True
                    st.session_state["file_id"] = file_id
                    
                    os.unlink(temp_file_path)

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
                
                if send_data_to_n8n(form_data, st.session_state["file_id"], summary_data):
                    st.balloons()
                    time.sleep(1)
                    
                    # 5. si resetta tutte le variabili di sessione
                    st.session_state["analysis_complete"] = False
                    st.session_state["extracted_content"] = None
                    st.session_state["ppt_content"] = None
                    st.session_state["uploaded_file"] = None
                    st.session_state["reset_uploader"] = True
                    st.session_state["file_uploaded"] = False
                    st.session_state["file_id"] = None
                    
                    # 6. vai alla pagina di successo
                    st.switch_page("pages/success.py")
            except Exception as e:
                st.error(f"Si è verificato un errore durante il caricamento: {str(e)}")