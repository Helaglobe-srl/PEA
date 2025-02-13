import streamlit as st

st.set_page_config(page_title="Iscrizione Completata", page_icon="✅")

st.image("images/logo_pea.jpg", width=200)
st.title("✅ Iscrizione completata con successo!")

# messaggio di conferma email
st.info("""
    Riceverai un'email di conferma dell'avvenuta iscrizione con il riepilogo dei dati inseriti 
    al tuo indirizzo email.
    
    Controlla la tua casella di posta per tutti i dettagli.
""")

# bottone Torna alla Home
if st.button("Torna alla Home"):
    # resetta tutte le variabili di sessione
    for key in st.session_state.keys():
        del st.session_state[key]
    st.switch_page("app.py") 