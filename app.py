import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime

# Cargar leads solo si el archivo existe
if os.path.exists("leads_ver4.csv"):
    leads_df = pd.read_csv("leads_ver4.csv")
    servicios_unicos = sorted(leads_df["servicio"].dropna().unique())
    canales_unicos = sorted(leads_df["canal"].dropna().unique())
    if "TikTok" not in canales_unicos:
        canales_unicos.append("TikTok")
else:
    st.error("❌ No se encontró el archivo 'leads_ver4.csv'. Asegúrate de que esté en la misma carpeta que 'app.py'.")
    st.stop()

# -------------------------
# Cargar modelo entrenado
# -------------------------
modelo = joblib.load('modelo/modelo_inbound_clinica.pkl')

# Obtener lista única de servicios y canales
servicios_unicos = sorted(leads_df["servicio"].dropna().unique())
canales_unicos = sorted(leads_df["canal"].dropna().unique())

# -------------------------
# Funciones auxiliares
# -------------------------

def clasificar_momento(hora):
    if 6 <= hora < 12:
        return 'mañana'
    elif 12 <= hora < 18:
        return 'tarde'
    else:
        return 'noche'

def simplificar_canal(canal):
    canal = canal.lower()
    if 'whatsapp' in canal:
        return 'whatsapp'
    elif any(x in canal for x in ['facebook', 'instagram', 'tiktok']):
        return 'redes'
    elif 'web' in canal:
        return 'web'
    else:
        return 'otro'

def operador_desde_prefijo(numero):
    if numero is None:
        return 'otro'
    numero = str(numero)
    if numero.startswith(('9')):
        if numero[1:3] in ['41', '42', '43', '44']:
            return 'claro'
        elif numero[1:3] in ['70', '71', '72']:
            return 'movistar'
    return 'otro'

def procesar_input(nombre, correo, telefono, servicio, canal, urgencia, hora_contacto):
    return pd.DataFrame([{
        'servicio': servicio,
        'canal_simplificado': simplificar_canal(canal),
        'urgencia': urgencia,
        'hora_contacto': hora_contacto,
        'momento_dia': clasificar_momento(hora_contacto),
        'longitud_nombre': len(nombre.strip()),
        'dominio_correo': correo.split('@')[-1].lower().strip(),
        'operador_telefono': operador_desde_prefijo(telefono)
    }])

def guardar_lead(data, pred):
    salida = data.copy()
    salida['interes_activo'] = pred
    salida['fecha_registro'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ruta = 'data/leads_clasificados.csv'
    if os.path.exists(ruta):
        df_antiguo = pd.read_csv(ruta)
        df_nuevo = pd.concat([df_antiguo, salida], ignore_index=True)
    else:
        df_nuevo = salida

    df_nuevo.to_csv(ruta, index=False)

# -------------------------
# Interfaz Streamlit
# -------------------------

st.set_page_config(page_title="Clasificación de Leads", layout="centered")

st.title("🦷 Clasificación Inteligente de Leads - Clínica Odontológica")
st.markdown("Completa el formulario para registrar un nuevo lead y predecir su nivel de interés.")

with st.form("formulario_lead"):
    nombre = st.text_input("Nombre completo")
    correo = st.text_input("Correo electrónico")
    telefono = st.text_input("Número de teléfono")

    servicio = st.selectbox("Servicio de interés", servicios_unicos)

    canal = st.selectbox("Canal de contacto", canales_unicos)

    urgencia = st.selectbox("Nivel de urgencia", [
        "Baja", "Media", "Alta"
    ])

    hora_contacto = st.slider("Hora de contacto", 0, 23, 12)

    submit = st.form_submit_button("Registrar y Clasificar")

# -------------------------
# Predicción
# -------------------------

if submit:
    if not nombre or not correo or not telefono:
        st.warning("⚠️ Por favor, completa todos los campos obligatorios.")
    else:
        df_input = procesar_input(nombre, correo, telefono, servicio, canal, urgencia, hora_contacto)
        pred = modelo.predict(df_input)[0]
        proba = modelo.predict_proba(df_input)[0][1]  # probabilidad clase 1

        if pred == 1:
            st.success(f"✅ Este lead muestra **ALTO INTERÉS**. (Prob: {proba:.2f})")
        else:
            st.info(f"Este lead muestra **BAJO INTERÉS**. (Prob: {proba:.2f})")

        # Guardar el lead en CSV
        guardar_lead(df_input, pred)
