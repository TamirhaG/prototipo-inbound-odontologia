import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from utils.visualizaciones import grafico_servicios, grafico_interes
import os

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Cargar el modelo 
import joblib
modelo = joblib.load("modelo/modelo_inbound_clinica.pkl")

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(page_title="Captura de Leads - Clínica Odontológica", layout="centered")

# ---------------- FUNCIONES AUXILIARES ----------------
CSV_FILE = "leads_ver4.csv"

def cargar_datos():
    columnas = [
        "nombre", "correo", "telefono", "servicio", "canal", "interes_activo",
        "horario_contacto", "dias_desde_contacto", "referido", "tratamiento_prev"
    ]

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)

        # Asegurar columnas (por si el archivo es antiguo)
        for col in columnas:
            if col not in df.columns:
                df[col] = None

        # Normalizar valores de interes_activo
        if "interes_activo" in df.columns:
            df["interes_activo"] = df["interes_activo"].replace({"Sí": 1, "No": 0})
            df["interes_activo"] = pd.to_numeric(df["interes_activo"].replace({"Sí": 1, "No": 0}), errors="coerce").fillna(0).astype(int).clip(0, 1)

        return df
    else:
        return pd.DataFrame(columns=columnas)

def guardar_dato(df_nuevo):
    df_actual = cargar_datos()
    correo_nuevo = df_nuevo["correo"].iloc[0].strip().lower()
    correos_actuales = df_actual["correo"].str.strip().str.lower()

    if correo_nuevo not in correos_actuales.values:
        df_actual = pd.concat([df_actual, df_nuevo], ignore_index=True)
        df_actual.to_csv(CSV_FILE, index=False)
    else:
        st.warning("⚠️ Este lead ya fue registrado.")

def generar_descarga_csv(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer

import re
def es_correo_valido(correo):
    return re.match(r"[^@]+@[^@]+\.[^@]+", correo.strip())

# ---------------- INTERFAZ PRINCIPAL ----------------
st.title("🦷 Captura y Visualización de Leads")
st.markdown("Este prototipo permite registrar leads y visualizar su análisis.")

tabs = st.tabs(["🤖 Registro y Predicción de Lead", "📊 Análisis de Leads"])

# ---------------- TAB 1: REGISTRO ----------------
with tabs[0]:
    with st.form("lead_formulario"):
        st.subheader("Registrar nuevo lead")

        nombre = st.text_input("Nombre completo", max_chars=50)
        correo = st.text_input("Correo electrónico")
        telefono = st.text_input("Número de teléfono")
        servicio = st.selectbox("Servicio de interés", ["Ortodoncia", "Limpieza dental", "Blanqueamiento", "Implantes", "Evaluación general", "Endodoncia"])
        canal = st.selectbox("Canal de contacto", ["Instagram", "Facebook", "WhatsApp", "TikTok", "Otro"])
        interes_activo = st.selectbox("¿Interés confirmado?", ["Sí", "No"])
        horario = st.selectbox("Horario de contacto", ["Mañana", "Tarde", "Noche"])
        dias_desde = st.number_input("Días desde el contacto inicial", min_value=0, step=1)
        referido = st.selectbox("¿Fue referido por otro paciente?", ["Sí", "No"])
        tratamiento_prev = st.selectbox("¿Ha recibido tratamiento previo en la clínica?", ["Sí", "No"])
        canal_origen = st.selectbox("Canal de origen", ["Página web", "Google Ads", "Recomendación", "Llamada directa"])
        urgencia = st.selectbox("Nivel de urgencia", ["Alta", "Media", "Baja"])
        mensaje_largo = st.selectbox("¿Mensaje largo?", ["Sí", "No"])
        hora_contacto = st.slider("Hora de contacto (0-23)", min_value=0, max_value=23)
        dias_recientes = st.selectbox("¿Días recientes?", ["Sí", "No"])

        enviar = st.form_submit_button("Guardar Lead y Predecir")

        if enviar:
            if nombre.strip() and correo.strip() and telefono.strip() and es_correo_valido(correo):
                # Guardar lead en CSV
                df_nuevo = pd.DataFrame([{
                    "nombre": nombre.strip().title(),
                    "correo": correo.strip().lower(),
                    "telefono": telefono.strip(),
                    "servicio": servicio,
                    "canal": canal,
                    "interes_activo": 1 if interes_activo == "Sí" else 0,
                    "horario_contacto": horario,
                    "dias_desde_contacto": dias_desde,
                    "referido": 1 if referido == "Sí" else 0,
                    "tratamiento_prev": 1 if tratamiento_prev == "Sí" else 0
                }])

                guardar_dato(df_nuevo)
                st.success("✅ Lead registrado con éxito.")

                # Preparar datos para predicción
                # Construir DataFrame base
                df_pred = pd.DataFrame([{
                    'servicio': servicio,
                    'canal': canal,
                    'canal_origen': canal_origen,
                    'urgencia': urgencia,
                    'mensaje_largo': 1 if mensaje_largo == "Sí" else 0,
                    'referido': 1 if referido == "Sí" else 0,
                    'tratamiento_prev': 1 if tratamiento_prev == "Sí" else 0,
                    'es_mañana': 1 if horario == "Mañana" else 0,
                    'dias_recientes': 1 if dias_recientes == "Sí" else 0,
                    'hora_contacto': hora_contacto,
                    'dias_desde_contacto': dias_desde  # ← aquí estaba el error
                }])


                # Ingeniería de variables adicionales
                df_pred['momento_dia'] = df_pred['hora_contacto'].apply(
                    lambda h: "mañana" if h < 12 else ("tarde" if h < 18 else "noche")
                )

                df_pred['longitud_nombre'] = len(nombre.strip())

                df_pred['dominio_correo'] = correo.strip().split("@")[-1].lower() if "@" in correo else "desconocido"

                def operador_peruano(numero):
                    if pd.isna(numero):
                        return "desconocido"
                    numero = str(numero)
                    if len(numero) < 12:
                        return "otro"
                    prefix = numero[5:8]
                    if prefix in ['981', '982', '983', '984', '985']:
                        return "claro"
                    elif prefix in ['990', '991', '992', '993', '994']:
                        return "movistar"
                    else:
                        return "otro"

                df_pred['operador_telefono'] = operador_peruano(telefono)

                def simplificar_canal(c):
                    c = str(c).lower()
                    if "whatsapp" in c:
                        return "whatsapp"
                    elif any(r in c for r in ["facebook", "instagram", "tiktok"]):
                        return "redes_sociales"
                    elif "web" in c:
                        return "web"
                    else:
                        return "otro"

                df_pred['canal_simplificado'] = simplificar_canal(canal)

                try:
                    # Reordenar columnas según las usadas en el entrenamiento
                    features_ordenadas = [
                        'servicio', 'canal', 'canal_origen', 'urgencia', 'mensaje_largo',
                        'referido', 'tratamiento_prev', 'es_mañana', 'dias_recientes',
                        'hora_contacto', 'dias_desde_contacto', 'momento_dia',
                        'longitud_nombre', 'dominio_correo', 'operador_telefono', 'canal_simplificado'
                    ]

                    df_pred = df_pred[features_ordenadas]

                    # Pasar directamente al modelo (pipeline hace el procesamiento)
                    prob = modelo.predict_proba(df_pred)[0][1]


                    st.markdown("---")
                    st.subheader("🤖 Predicción de Conversión")
                    st.success(f"🔮 Probabilidad estimada: **{prob*100:.1f}%**")

                    if prob >= 0.7:
                        st.markdown("✅ Alta probabilidad de conversión")
                    elif prob >= 0.4:
                        st.markdown("🟡 Probabilidad moderada de conversión")
                    else:
                        st.markdown("🔻 Baja probabilidad de conversión")

                except Exception as e:
                    st.error(f"❗ Error al predecir: {e}")
    
                    
            else:
                st.error("❗ Por favor, completa todos los campos correctamente (correo válido requerido).")


# ---------------- TAB 2: DASHBOARD ----------------
with tabs[1]:
    df = cargar_datos()

    if df.empty:
        st.info("ℹ️ Aún no hay leads registrados.")
    else:
        st.subheader("📈 Métricas generales")
        total_leads = len(df)
        tasa_interes = df["interes_activo"].mean() * 100 if "interes_activo" in df else 0

        col1, col2 = st.columns(2)
        col1.metric("Total de Leads", total_leads)
        col2.metric("Tasa de Conversión", f"{tasa_interes:.1f}%")

        st.divider()

        st.subheader("📊 Gráficos")

        col3, col4 = st.columns(2)

        with col3:
            try:
                fig1 = grafico_servicios(df)
                st.pyplot(fig1)
            except Exception as e:
                st.warning(f"⚠️ Error al generar gráfico de servicios: {e}")

        with col4:
            try:
                fig2 = grafico_interes(df)
                st.pyplot(fig2)
            except Exception as e:
                st.warning(f"⚠️ Error al generar gráfico de interés: {e}")

        st.divider()

        st.subheader("📋 Últimos Leads Registrados")

        columnas_mostrar = [
            "nombre", "correo", "telefono", "servicio", "canal", "interes_activo",
            "horario_contacto", "dias_desde_contacto", "referido", "tratamiento_prev"
        ]

        # Mostrar sólo si las columnas existen
        columnas_presentes = [col for col in columnas_mostrar if col in df.columns]
        st.dataframe(df[columnas_presentes].tail(10))

        # Botón de descarga
        csv_buffer = generar_descarga_csv(df)
        st.download_button("📥 Descargar CSV completo", data=csv_buffer, file_name="leads.csv", mime="text/csv")
