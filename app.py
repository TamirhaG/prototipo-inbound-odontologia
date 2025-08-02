import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Inbound Marketing Clínica Odontológica", layout="wide")

st.title("🦷 Inbound Marketing para Clínica Odontológica")

# Menú de navegación
seccion = st.sidebar.selectbox("📌 Menú de Navegación", ["📥 Registro de Leads", "📊 Dashboard"])

# Ruta del CSV
csv_file = "leads_ver1.csv"

# ================================
# 📥 SECCIÓN: REGISTRO DE LEADS
# ================================
if seccion == "📥 Registro de Leads":
    st.header("📥 Registro de Leads")

    with st.form(key='lead_form'):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo")
            correo = st.text_input("Correo electrónico")
            telefono = st.text_input("Teléfono")

        with col2:
            interes = st.selectbox("Servicio de interés", [
                "Ortodoncia", "Implantes", "Blanqueamiento",
                "Limpieza dental", "Evaluación general", "Endodoncia"
            ])
            canal = st.selectbox("Canal de contacto", ["Instagram", "Facebook", "WhatsApp", "Otro"])

        submit = st.form_submit_button("Registrar Lead")

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
            df = pd.read_csv(csv_file)
            df = pd.concat([df, pd.DataFrame([nuevo_lead])], ignore_index=True)
        except FileNotFoundError:
            df = pd.DataFrame([nuevo_lead])

        df.to_csv(csv_file, index=False)
        st.success("✅ Lead registrado exitosamente.")


# ========================
# 📊 SECCIÓN: DASHBOARD
# ========================
elif seccion == "📊 Dashboard":
    st.header("📊 Dashboard de Leads")

    try:
        df = pd.read_csv(csv_file)

        total_leads = len(df)
        leads_activados = df[df["interes_activo"] == "Sí"]
        tasa_conversion = (len(leads_activados) / total_leads * 100) if total_leads > 0 else 0

        col1, col2 = st.columns(2)
        col1.metric("👥 Total de Leads", total_leads)
        col2.metric("✅ Tasa de Conversión", f"{tasa_conversion:.1f}%")

        # Gráfico 1: Leads por tipo de tratamiento
        st.subheader("Distribución por Servicio de Interés")
        fig1, ax1 = plt.subplots()
        df["interes"].value_counts().plot(kind='bar', color="#4db6ac", ax=ax1)
        ax1.set_ylabel("Número de Leads")
        st.pyplot(fig1)

        # Gráfico 2: Leads por estado de interés
        st.subheader("Interés Activo vs No Activo")
        fig2, ax2 = plt.subplots()
        df["interes_activo"].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, colors=["#66bb6a", "#ef5350"], ax=ax2)
        ax2.set_ylabel("")
        st.pyplot(fig2)

        # Vista de tabla
        st.subheader("Últimos 10 Leads Registrados")
        st.dataframe(df.sort_values(by="fecha_registro", ascending=False).head(10))

        # Botón para descargar CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Leads (CSV)", csv, "leads.csv", "text/csv")

    except FileNotFoundError:
        st.warning("No se encontró el archivo de leads.")
