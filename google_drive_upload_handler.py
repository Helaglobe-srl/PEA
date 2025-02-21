from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import streamlit as st

class GoogleDriveUploadHandler:
    def __init__(self):
        self.service = self.authenticate_drive()
        
    def authenticate_drive(self):
        """
        Autentica l'applicazione con Google Drive
        """
        creds = Credentials.from_service_account_info(st.secrets["gdrive_service_account"])
        service = build("drive", "v3", credentials=creds)
        return service

    def upload_file(self, file_name, file_path, folder_id):
        """
        Carica un file su Google Drive nella cartella specificata
        """
        file_metadata = {
            "name": file_name,
            "parents": [folder_id]
        }
        
        media = MediaFileUpload(file_path)
            
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()
            
        return file.get("id")