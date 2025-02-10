from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import streamlit as st
import os

def authenticate_drive():
    """
    Autentica l'applicazione con Google Drive utilizzando le credenziali 
    dell'account di servizio configurate nei segreti di Streamlit
    """
    creds = Credentials.from_service_account_info(st.secrets["gdrive_service_account"])
    service = build("drive", "v3", credentials=creds)
    return service

def upload_to_drive(service, file_name, file_path, folder_id):
    """
    Carica un file su Google Drive nella cartella specificata
    
    Parametri:
    service: servizio Google Drive autenticato
    file_name: nome del file da salvare su Drive
    file_path: percorso locale del file da caricare
    folder_id: ID della cartella di destinazione su Drive
    """
    file_metadata = {
        "name": file_name,
        "parents": [folder_id]
    }
    
    media = MediaFileUpload(
        file_path,
        resumable=True
    )
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    
    return file.get("id")