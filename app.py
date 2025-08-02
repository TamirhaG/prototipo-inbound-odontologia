import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from utils.visualizaciones import grafico_servicios, grafico_interes
import os

# ---------------- CONFIGURACIÓN GENERAL ----------------
st.set_page_config(page_title="Captura de Leads - Clínica Odontológica", layout="centered")

# ---------------- FUNCIONES AUXILIARES ----------------
CSV_FILE = "leads_ver1.csv"

def cargar_datos():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["nombre", "correo", "telefono", "servicio", "canal", "interes_activo"])

def guardar_dato(df_nuevo):
    df_actual = cargar_datos()
    df_actual = pd.concat([df_actual, df_nuevo], ignore_index=True)
    df_actual.to_csv(CSV_FILE, index=False)

def generar_descarga_csv(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return buffer

# ---------------- INTERFAZ PRINCIPAL ----------------
st.title("🦷 Captura y Visualización de Leads")
st.markdown("Este prototipo permite registrar leads y visualizar su análisis.")

tabs = st.tabs(["➕ Registrar Lead", "📊 Análisis de Leads"])

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

        enviar = st.form_submit_button("Guardar Lead")

        if enviar:
            if nombre and correo and telefono:
                df_nuevo = pd.DataFrame([{
                    "nombre": nombre,
                    "correo": correo,
                    "telefono": telefono,
                    "servicio": servicio,
                    "canal": canal,
                    "interes_activo": 1 if interes_activo == "Sí" else 0
                }])
                guardar_dato(df_nuevo)
                st.success("✅ Lead registrado con éxito.")
            else:
                st.error("❗ Por favor, completa todos los campos obligatorios.")

# ---------------- TAB 2: DASHBOARD ----------------
with tabs[1]:
    df = cargar_datos()

    if df.empty:
        st.info("Aún no hay leads registrados.")
    else:
        st.subheader("📈 Métricas generales")
        total_leads = len(df)
        tasa_interes = df["interes_activo"].mean() * 100

        col1, col2 = st.columns(2)
        col1.metric("Total de Leads", total_leads)
        col2.metric("Tasa de Conversión", f"{tasa_interes:.1f}%")

        st.divider()
        st.subheader("📊 Gráficos")

        col3, col4 = st.columns(2)

        with col3:
            fig1 = grafico_servicios(df)
            st.pyplot(fig1)

        with col4:
            fig2 = grafico_interes(df)
            st.pyplot(fig2)


        st.divider()
        st.subheader("📋 Últimos Leads Registrados")
        st.dataframe(df.tail(10))

        csv_buffer = generar_descarga_csv(df)
        st.download_button("📥 Descargar CSV completo", data=csv_buffer, file_name="leads.csv", mime="text/csv")
