import os 
import streamlit as st
from upload_handler import authenticate_drive, upload_to_drive
import tempfile

if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None
if "file_upload_ids" not in st.session_state:
    st.session_state["file_upload_ids"] = []

FOLDER_ID = st.secrets["drive_folder_id"]

st.set_page_config(
    page_title="Iscrizione PEA",
    page_icon="📊",
)

st.image("images/logo_pea.jpg", width=200)
st.title("Carica la tua presentazione")

with st.form("upload_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Nome")
    with col2:
        surname = st.text_input("Cognome")
    
    uploaded_file = st.file_uploader(
        "Carica la tua presentazione", 
        type=["ppt", "pptx"],
        help="Carica un file PowerPoint"
    )
    
    submit_button = st.form_submit_button("Carica")

    if submit_button and uploaded_file is not None:
        if name and surname:
            with st.spinner("Caricamento in corso..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
                        temp_file.write(uploaded_file.getbuffer())
                        temp_file_path = temp_file.name

                    file_name = f"{surname}_{name}_{uploaded_file.name}"
                    
                    service = authenticate_drive()
                    file_id = upload_to_drive(service, file_name, temp_file_path, FOLDER_ID)
                    
                    os.unlink(temp_file_path)
                    
                    st.success(f"✅ Presentazione caricata con successo!")
                    st.session_state["file_upload_ids"] = file_id
                    
                except Exception as e:
                    st.error(f"Si è verificato un errore durante il caricamento: {str(e)}")
        else:
            st.error("Per favore, inserisci sia nome che cognome.")
