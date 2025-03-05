import streamlit as st

st.set_page_config(page_title="Iscrizione Completata", page_icon="✅")

col1, col2, col3 = st.columns([1,1,1])
with col2:
    st.image("images/LOGO_PEA.webp", use_container_width=True)
st.title("✅ Iscrizione completata con successo!")

# messaggio di conferma dell'iscrizione
st.info("""
    Grazie per aver candidato il tuo progetto!  

    Riceverai un'e-mail di conferma, con il riepilogo dei dati inseriti.  

    Controlla la tua casella di posta per tutti i dettagli. Se non ricevi l'email, ti preghiamo di controllare anche la cartella dello spam. 

    Per eventuali necessità scrivi a peaward@helaglobe.com o chiama al numero 055.4939527.  

    Grazie, 

    Il team Helaglobe 
""")

# bottone Torna alla Home
col1, col2, col3 = st.columns([1,1,1])
with col2:
    if st.button("Candida un altro progetto"):
        # resetta tutte le variabili di sessione
        for key in st.session_state.keys():
            del st.session_state[key]
        st.switch_page("app.py") 