from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import streamlit as st

def authenticate_drive():
    """
    Autentica l'applicazione con Google Drive
    """
    creds = Credentials.from_service_account_info(st.secrets["gdrive_service_account"])
    service = build("drive", "v3", credentials=creds)
    return service

def upload_to_drive(service, file_name, file_path, folder_id):
    """
    Carica un file su Google Drive nella cartella specificata
    """
    file_metadata = {
        "name": file_name,
        "parents": [folder_id]
    }
    
    media = MediaFileUpload(
        file_path
    )
        
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
        
    return file.get("id")