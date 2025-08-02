import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Captura de Leads - Clínica Odontológica", layout="centered")

st.title("🦷 Captura de Leads - Clínica Odontológica")
st.markdown("Simula el registro de leads desde redes sociales o web.")

# Formulario
with st.form(key='lead_form'):
    nombre = st.text_input("Nombre completo")
    correo = st.text_input("Correo electrónico")
    telefono = st.text_input("Número de teléfono")
    
    interes = st.selectbox("Servicio de interés", [
        'Ortodoncia',
        'Implantes',
        'Blanqueamiento',
        'Limpieza dental',
        'Evaluación general',
        'Endodoncia'
    ])
    
    canal = st.selectbox("Canal de contacto", ["Instagram", "Facebook", "WhatsApp", "Otro"])
    
    submit = st.form_submit_button("Enviar")

# Al enviar
if submit:
    nuevo_lead = {
        "nombre": nombre,
        "correo": correo,
        "telefono": telefono,
        "interes": interes,
        "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "canal": canal,
        "interes_activo": "Pendiente"
    }

    try:
        df = pd.read_csv("leads_ver1.csv")
        df = pd.concat([df, pd.DataFrame([nuevo_lead])], ignore_index=True)
    except FileNotFoundError:
        df = pd.DataFrame([nuevo_lead])
    
    df.to_csv("leads_ver1.csv", index=False)
    st.success("✅ Lead registrado correctamente.")
