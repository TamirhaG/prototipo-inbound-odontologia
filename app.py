import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime

# -------------------------
# Verificar existencia de dataset
# -------------------------
if os.path.exists("leads_ver4.csv"):
    leads_df = pd.read_csv("leads_ver4.csv")
    servicios_unicos = sorted(leads_df["servicio"].dropna().unique())
    canales_unicos = sorted(leads_df["canal"].dropna().unique())

    # Asegurar que TikTok esté incluido
    if "TikTok" not in canales_unicos:
        canales_unicos.append("TikTok")

    canales_unicos = sorted(canales_unicos)
else:
    st.error("❌ No se encontró el archivo 'leads_ver4.csv'. Asegúrate de que esté en la misma carpeta que 'app.py'.")
    st.stop()

# -------------------------
# Cargar modelo entrenado
# -------------------------
modelo = joblib.load("modelo/modelo_inbound_clinica.pkl")

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
    if numero.startswith('9'):
        if numero[1:3] in ['41', '42', '43', '44']:
            return 'claro'
        elif numero[1:3] in ['70', '71', '72']:
            return 'movistar'
    return 'otro'

def procesar_input(
    nombre, correo, telefono, servicio, canal, urgencia,
    horario_contacto, dias_desde_contacto,
    interes_confirmado, referido, tratamiento_previo
):
    # Convertir horario textual a hora estimada
    if horario_contacto == 'Mañana':
        hora_contacto = 9
        momento_dia = 'mañana'
    elif horario_contacto == 'Tarde':
        hora_contacto = 15
        momento_dia = 'tarde'
    else:
        hora_contacto = 20
        momento_dia = 'noche'

    # Longitud del nombre
    longitud_nombre = len(nombre.strip())

    # Dominio del correo
    dominio_correo = correo.split('@')[-1].lower().strip()

    # Operador del teléfono
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

    operador = operador_desde_prefijo(telefono)

    # Canal simplificado
    canal_simplificado = simplificar_canal(canal)

    # Variables combinadas (como en entrenamiento)
    urgencia_momento = urgencia.lower() + "_" + momento_dia
    canal_servicio = canal_simplificado + "_" + servicio.lower().replace(" ", "_")
    dominio_operador = dominio_correo + "_" + operador

    return pd.DataFrame([{
        'servicio': servicio,
        'canal_simplificado': canal_simplificado,
        'urgencia': urgencia,
        'hora_contacto': hora_contacto,
        'momento_dia': momento_dia,
        'longitud_nombre': longitud_nombre,
        'dominio_correo': dominio_correo,
        'operador_telefono': operador,
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

    # Crear carpeta si no existe
    os.makedirs("data", exist_ok=True)

    ruta = 'data/leads_clasificados.csv'
    if os.path.exists(ruta):
        df_antiguo = pd.read_csv(ruta)
        df_nuevo = pd.concat([df_antiguo, salida], ignore_index=True)
    else:
        df_nuevo = salida

    df_nuevo.to_csv(ruta, index=False)

# -------------------------
# Interfaz Streamlit con Tabs
# -------------------------

st.set_page_config(page_title="Clasificación de Leads", layout="centered")

tab1, tab2 = st.tabs(["📋 Registrar Lead", "📊 Dashboard"])

# -------------------------
# TAB 1: Registro y predicción
# -------------------------
with tab1:
    st.title("🦷 Clasificación Inteligente de Leads")
    st.markdown("Completa el formulario para registrar un nuevo lead y predecir su nivel de interés.")

    with st.form("formulario_lead"):
        nombre = st.text_input("Nombre completo")
        correo = st.text_input("Correo electrónico")
        telefono = st.text_input("Número de teléfono")
        servicio = st.selectbox("Servicio de interés", servicios_unicos)
        canal = st.selectbox("Canal de contacto", canales_unicos)
        urgencia = st.selectbox("Nivel de urgencia", ["Baja", "Media", "Alta"])
        horario_contacto = st.selectbox("Horario de contacto", ["Mañana", "Tarde", "Noche"])
        dias_desde_contacto = st.number_input("Días desde el contacto inicial", min_value=0, max_value=60, value=5)
        interes_confirmado = st.radio("¿Interés confirmado?", ["Sí", "No"])
        referido = st.radio("¿Fue referido por otro paciente?", ["Sí", "No"])
        tratamiento_previo = st.radio("¿Ha recibido tratamiento previo en la clínica?", ["Sí", "No"])

        submit = st.form_submit_button("Registrar y Clasificar")


    if submit:
        if not nombre or not correo or not telefono:
            st.warning("⚠️ Por favor, completa todos los campos obligatorios.")
        else:
            df_input = procesar_input(
                nombre, correo, telefono, servicio, canal, urgencia,
                horario_contacto, dias_desde_contacto,
                interes_confirmado, referido, tratamiento_previo
            )
            
            pred = modelo.predict(df_input)[0]
            proba = modelo.predict_proba(df_input)[0][1]

            if pred == 1:
                st.success(f"✅ Este lead muestra **ALTO INTERÉS**. (Prob: {proba:.2f})")
            else:
                st.info(f"Este lead muestra **BAJO INTERÉS**. (Prob: {proba:.2f})")

            guardar_lead(df_input, pred)

# -------------------------
# TAB 2: Dashboard de seguimiento
# -------------------------
with tab2:
    st.title("📊 Dashboard de Leads Clasificados")

    ruta = "data/leads_clasificados.csv"
    if os.path.exists(ruta):
        df_leads = pd.read_csv(ruta)

        st.subheader("🔢 Resumen")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total registrados", len(df_leads))
        with col2:
            tasa = (df_leads['interes_activo'].sum() / len(df_leads)) * 100
            st.metric("Tasa de interés alto", f"{tasa:.2f}%")

        st.subheader("🦷 Servicios más solicitados")
        st.bar_chart(df_leads['servicio'].value_counts())

        st.subheader("📱 Canales más usados")
        st.bar_chart(df_leads['canal_simplificado'].value_counts())

        st.subheader("📈 Últimos registros")
        st.dataframe(df_leads.tail(10))

        st.download_button(
            label="📥 Descargar CSV",
            data=df_leads.to_csv(index=False).encode("utf-8"),
            file_name="leads_clasificados.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ Aún no hay registros clasificados.")
