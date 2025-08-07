import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime
import re

# -------------------------
# Cargar modelo
# -------------------------
modelo = joblib.load('modelo/modelo_inbound_clinica.pkl')

# -------------------------
# Utilidades
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
    numero = str(numero)
    if numero.startswith('9'):
        if numero[1:3] in ['41', '42', '43', '44']:
            return 'claro'
        elif numero[1:3] in ['70', '71', '72']:
            return 'movistar'
    return 'otro'

def validar_correo(correo):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo)

def procesar_input(nombre, correo, telefono, servicio, canal, urgencia, hora_contacto,
                   interes_confirmado, referido, tratamiento_previo, dias_desde_contacto):
    
    momento_dia = clasificar_momento(hora_contacto)
    longitud_nombre = len(nombre.strip())
    dominio_correo = correo.split('@')[-1].lower().strip()
    operador_telefono = operador_desde_prefijo(telefono)
    canal_simplificado = simplificar_canal(canal)
    
    urgencia_momento = urgencia.lower() + "_" + momento_dia
    canal_servicio = canal_simplificado + "_" + servicio.lower().replace(" ", "_")
    dominio_operador = dominio_correo + "_" + operador_telefono

    return pd.DataFrame([{
        'servicio': servicio,
        'canal_simplificado': canal_simplificado,
        'urgencia': urgencia,
        'hora_contacto': hora_contacto,
        'momento_dia': momento_dia,
        'longitud_nombre': longitud_nombre,
        'dominio_correo': dominio_correo,
        'operador_telefono': operador_telefono,
        'interes_confirmado': interes_confirmado,
        'dias_desde_contacto': dias_desde_contacto,
        'referido': referido,
        'tratamiento_previo': tratamiento_previo,
        'urgencia_momento': urgencia_momento,
        'canal_servicio': canal_servicio,
        'dominio_operador': dominio_operador
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
    
    servicio = st.selectbox("Servicio de interés", [
        "Ortodoncia", "Limpieza dental", "Blanqueamiento", "Implantes", "Evaluación general", "Endodoncia"
    ])

    canal = st.selectbox("Canal de contacto", [
        "Instagram", "Facebook", "WhatsApp", "TikTok", "Web", "Otro"
    ])

    urgencia = st.selectbox("Nivel de urgencia", ["Baja", "Media", "Alta"])
    
    hora_contacto = st.slider("Hora de contacto (0 a 23)", 0, 23, 12)

    interes_confirmado = st.selectbox("¿Interés confirmado?", ["Sí", "No"])
    referido = st.selectbox("¿Fue referido por otro paciente?", ["Sí", "No"])
    tratamiento_previo = st.selectbox("¿Ha recibido tratamiento previo en la clínica?", ["Sí", "No"])

    dias_desde_contacto = st.number_input("Días desde el contacto inicial", min_value=0, max_value=90, value=5)

    submit = st.form_submit_button("Registrar y Clasificar")

# -------------------------
# Predicción
# -------------------------
if submit:
    if not nombre or not correo or not telefono:
        st.warning("⚠️ Por favor, completa todos los campos obligatorios.")
    elif not validar_correo(correo):
        st.warning("⚠️ El correo electrónico no es válido.")
    else:
        df_input = procesar_input(nombre, correo, telefono, servicio, canal, urgencia, hora_contacto,
                                  interes_confirmado, referido, tratamiento_previo, dias_desde_contacto)
        pred = modelo.predict(df_input)[0]
        proba = modelo.predict_proba(df_input)[0][1]

        if pred == 1:
            st.success(f"✅ Este lead muestra **ALTO INTERÉS**. (Probabilidad: {proba:.2f})")
        else:
            st.info(f"Este lead muestra **BAJO INTERÉS**. (Probabilidad: {proba:.2f})")

        guardar_lead(df_input, pred)
