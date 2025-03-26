from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import streamlit as st
import tempfile
import os

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
        
    def upload_text_content(self, file_name, content, folder_id):
        """
        Carica un contenuto testuale come file su Google Drive nella cartella specificata
        """
        temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8")
        try:
            temp_path = temp_file.name
            temp_file.write(content)
            temp_file.close() 
            
            file_id = self.upload_file(file_name, temp_path, folder_id)
            return file_id
        finally:
            # provo a cancellare il file temporaneo
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except (PermissionError, OSError) as e:
                print(f"Warning: Could not delete temporary file {temp_path}: {str(e)}")
                pass