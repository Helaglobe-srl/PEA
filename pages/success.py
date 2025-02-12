import streamlit as st
import time

st.set_page_config(page_title="Iscrizione Completata", page_icon="✅")

st.image("images/logo_pea.jpg", width=200)
st.title("✅ Iscrizione completata con successo!")

# bottone Torna alla Home
if st.button("Torna alla Home"):
    # resetta tutte le variabili di sessione
    for key in st.session_state.keys():
        del st.session_state[key]
    st.switch_page("app.py") 