import requests
import hashlib
import streamlit as st

class MailchimpHandler:
    def __init__(self):
        self.api_key = st.secrets["mailchimp"]["api_key"]
        self.list_id = st.secrets["mailchimp"]["list_id"]
        self.data_center = st.secrets["mailchimp"]["data_center"]
        self.tag_name = "PEA 2025"

    def add_subscriber(self, email, first_name, last_name, ruolo, azienda, telefono, tipologia):
        """
        Add a new subscriber to Mailchimp list or update existing one with PEA 2025 tag
        """
        try:
            # calcolo l'hash MD5 della email in minuscolo (richiesto da Mailchimp)
            subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()

            # prima controllo se il membro esiste, in tal caso gli assegno il tag PEA 2025
            tags_url = f'https://{self.data_center}.api.mailchimp.com/3.0/lists/{self.list_id}/members/{subscriber_hash}/tags'
            tags_data = {
                "tags": [{
                    "name": self.tag_name,
                    "status": "active"
                }]
            }

            tags_response = requests.post(
                tags_url, 
                auth=('anystring', self.api_key), 
                json=tags_data
            )

            if tags_response.status_code == 204:
                return True, "Existing subscriber updated with PEA 2025 tag"

            # se non esiste, crea un nuovo membro con il tag
            url = f'https://{self.data_center}.api.mailchimp.com/3.0/lists/{self.list_id}/members'
            
            member_data = {
                "email_address": email,
                "status": "subscribed",
                "merge_fields": {
                    "EMAIL": email,
                    "MMERGE1": first_name,      
                    "MMERGE2": last_name,      
                    "MMERGE3": ruolo,          
                    "MMERGE4": tipologia,  
                    "MMERGE5": azienda,
                    "MMERGE16": telefono,
                },
                "tags": [self.tag_name]
            }

            response = requests.post(
                url, 
                auth=('anystring', self.api_key), 
                json=member_data
            )

            if response.status_code in [200, 201]: # 200: membro già esistente, 201: membro nuovo => in ogni caso successo
                return True, "New subscriber added successfully"
            else:
                return False, f"Failed to add subscriber. Status: {response.status_code}, Response: {response.json()}"

        except Exception as e:
            return False, f"Error adding subscriber to Mailchimp: {str(e)}" 