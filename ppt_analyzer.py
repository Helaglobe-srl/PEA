from pptx import Presentation
from openai import OpenAI
import streamlit as st
import re

def extract_text_from_ppt(file_path):
    """
    Estrae il testo da un file PowerPoint
    """
    prs = Presentation(file_path)
    text_content = []

    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                text_content.append(shape.text)
    
    return "\n".join(text_content)

def analyze_with_gpt(text_content):
    """
    Analizza il testo estratto usando GPT per ottenere categoria, descrizione e obiettivo
    """
    client = OpenAI(api_key=st.secrets["openai_api_key"])
    
    prompt = f"""Analizza questa presentazione PowerPoint e fornisci una risposta strutturata con questi elementi:

    1. CATEGORIA: [specifica una sola categoria tra: ACCESSO E POLICY MAKING, AWARENESS, EMPOWERMENT, PATIENT EXPERIENCE, PATIENT SUPPORT PROGRAM]
    2. DESCRIZIONE: [fornisci un riassunto dettagliato del progetto evitando l'uso di virgolette doppie (") - usa solo virgolette singole (') se necessario]
    3. OBIETTIVO: [descrivi l'obiettivo principale del progetto evitando l'uso di virgolette doppie (") - usa solo virgolette singole (') se necessario]

    Usa esattamente questi delimitatori nella tua risposta:
    <CATEGORIA>categoria</CATEGORIA>
    <DESCRIZIONE>descrizione</DESCRIZIONE>
    <OBIETTIVO>obiettivo</OBIETTIVO>

    IMPORTANTE: 
    - Non usare MAI virgolette doppie (") nel testo
    - Se devi citare qualcosa, usa solo virgolette singole (')
    - Non usare MAI il carattere backslash (\)
    
    Contenuto della presentazione:
    {text_content}"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Sei un assistente esperto nell'analisi di presentazioni PowerPoint. Fornisci riassunti strutturati e completi."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.7
    )
    
    return response.choices[0].message.content

def extract_sections(gpt_response):
    """
    Estrae le sezioni dalla risposta di GPT
    """
    categoria = re.search(r'<CATEGORIA>(.*?)</CATEGORIA>', gpt_response, re.DOTALL)
    descrizione = re.search(r'<DESCRIZIONE>(.*?)</DESCRIZIONE>', gpt_response, re.DOTALL)
    obiettivo = re.search(r'<OBIETTIVO>(.*?)</OBIETTIVO>', gpt_response, re.DOTALL)
    
    return {
        "categoria": categoria.group(1).strip() if categoria else "Non specificata",
        "descrizione": descrizione.group(1).strip() if descrizione else "Non disponibile",
        "obiettivo": obiettivo.group(1).strip() if obiettivo else "Non specificato"
    }

def analyze_ppt(file_path):
    """
    Funzione principale che coordina l'estrazione e l'analisi del PPT
    """
    # 1. Estrai il testo dal PPT
    text_content = extract_text_from_ppt(file_path)
    
    # 2. Analizza e riscrivi con GPT
    gpt_response = analyze_with_gpt(text_content)
    
    # 3. Estrai e restituisci le sezioni (categoria, descrizione e obiettivo)
    return extract_sections(gpt_response) 