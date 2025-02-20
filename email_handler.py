import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
from datetime import datetime

class EmailHandler:
    def __init__(self):
        """
        Inizializza l'handler email con le configurazioni da secrets
        """
        self.sender_email = st.secrets["email"]["sender"]
        self.password = st.secrets["email"]["password"]
        self.smtp_server = "smtp.gmail.com"  
        self.smtp_port = 587  # porta TLS Gmail

    def configure_smtp(self):
        """
        Configura la connessione SMTP con Gmail
        """
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # TLS
            server.login(self.sender_email, self.password)
            return server
        except Exception as e:
            st.error(f"Errore nella configurazione SMTP: {str(e)}")
            return None

    def send_confirmation_email(self, recipient_email, form_data, file_ids):
        """
        Invia una email di conferma dopo la registrazione
        """
        server = None
        try:
            server = self.configure_smtp()
            if not server:
                return "Errore di configurazione del server email"

            # preparo i link ai file caricati in Google Drive
            marchio_link = f"https://drive.google.com/file/d/{file_ids.get('marchio')}/view" if file_ids.get('marchio') else "#"
            image_link = f"https://drive.google.com/file/d/{file_ids.get('image')}/view" if file_ids.get('image') else "#"
            ppt_link = f"https://drive.google.com/file/d/{file_ids.get('ppt')}/view" if file_ids.get('ppt') else "#"

            msg = MIMEMultipart()
            msg['From'] = f"Patient Engagement Award – Helaglobe"
            msg['To'] = recipient_email
            msg['Subject'] = "Conferma registrazione al Patient Engagament Award 2025"

            # Corpo email
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <p>Gentile {form_data['nome_referente']} {form_data['cognome_referente']},</p>
                
                <p>la candidatura del progetto <strong>{form_data['titolo_progetto']}</strong> è stata registrata correttamente.</p>
                
                <p>Riepiloghiamo di seguito i dati da te inseriti:</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <ul style="list-style-type: none; padding-left: 0;">
                        <li><strong>Candidato:</strong> {form_data['candidato']}</li>
                        <li><strong>Tipologia:</strong> {form_data['tipologia']}</li>
                        <li><strong>Titolo Progetto:</strong> {form_data['titolo_progetto']}</li>
                        <li><strong>Area Terapeutica:</strong> {form_data['area_terapeutica']}</li>
                        <li><strong>Nome Referente:</strong> {form_data['nome_referente']}</li>
                        <li><strong>Cognome Referente:</strong> {form_data['cognome_referente']}</li>
                        <li><strong>Ruolo:</strong> {form_data['ruolo']}</li>
                        <li><strong>Email:</strong> {form_data['mail']}</li>
                        <li><strong>Telefono:</strong> {form_data['telefono']}</li>
                        <li style="margin-top: 15px;"><strong>File ricevuti:</strong></li>
                        <li style="margin-left: 20px; margin-top: 5px;">
                            <span style="color: #4CAF50; font-size: 18px;">✓</span> Logo aziendale [<a href="{marchio_link}" style="color: #0066cc;">Link</a>]
                        </li>
                        <li style="margin-left: 20px;">
                            <span style="color: #4CAF50; font-size: 18px;">✓</span> Immagine rappresentativa del progetto [<a href="{image_link}" style="color: #0066cc;">Link</a>]
                        </li>
                        <li style="margin-left: 20px;">
                            <span style="color: #4CAF50; font-size: 18px;">✓</span> Presentazione del progetto [<a href="{ppt_link}" style="color: #0066cc;">Link</a>]
                        </li>
                    </ul>
                </div>
                
                <p>Per eventuali necessità non esitare a contattarci scrivendo a <a href="mailto:pea@helaglobe.com">pea@helaglobe.com</a> o chiamando il numero 055.4939527.</p>
                
                <p>Per aggiornamenti sul Patient Engagament Award segui la nostra pagina <a href="https://www.linkedin.com/company/helaglobe/">LinkedIn</a> e iscriviti alla newsletter di Helaglobe, visitando il nuovo sito <a href="https://helaglobe.com/">https://helaglobe.com/</a></p>
                
                <p>Grazie</p>
                
                <p>Il team Helaglobe</p>
                
                <hr>
                <p style="font-size: 12px; color: #666;">
                    Questa è una email automatica. Per favore non rispondere a questo indirizzo.<br>
                    Data invio: {datetime.now().strftime('%d/%m/%Y %H:%M')}
                </p>
            </body>
            </html>
            """
            msg.attach(MIMEText(html_body, 'html'))
            
            server.send_message(msg)
            return True
            
        except smtplib.SMTPRecipientsRefused:
            return "L'indirizzo email fornito non è valido o non può ricevere email"
        except smtplib.SMTPResponseException as e:
            if e.smtp_code == 550:
                return "L'indirizzo email non è stato trovato o non può ricevere email"
            return f"Errore del server di posta: {e.smtp_error.decode()}"
        except smtplib.SMTPAuthenticationError:
            return "Errore di autenticazione del server email"
        except Exception as e:
            return f"Errore nell'invio dell'email: {str(e)}"
        finally:
            if server:
                server.quit()


def send_confirmation_email(recipient_email, form_data, file_ids=None):
    """
    Funzione wrapper per inviare l'email di conferma
    """
    handler = EmailHandler()
    return handler.send_confirmation_email(recipient_email, form_data, file_ids) 