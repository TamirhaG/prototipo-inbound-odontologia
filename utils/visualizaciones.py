import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def mostrar_dashboard(df):
    st.header("📊 Dashboard de Visualización")

    st.subheader("Resumen General")
    total_leads = df.shape[0]
    total_positivos = df["interes_activo"].sum()
    conversion_rate = round((total_positivos / total_leads) * 100, 2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Leads", total_leads)
    col2.metric("Interesados", total_positivos)
    col3.metric("Tasa de Conversión (%)", f"{conversion_rate}%")

    st.subheader("Servicios Más Solicitados")
    servicios = df["servicio"].value_counts().head(10)
    fig1, ax1 = plt.subplots()
    servicios.plot(kind='bar', ax=ax1)
    ax1.set_ylabel("Cantidad")
    ax1.set_xlabel("Servicio")
    ax1.set_title("Top Servicios")
    st.pyplot(fig1)

    st.subheader("Canales de Contacto")
    canales = df["canal"].value_counts()
    fig2, ax2 = plt.subplots()
    canales.plot(kind='bar', color='skyblue', ax=ax2)
    ax2.set_ylabel("Cantidad")
    ax2.set_xlabel("Canal")
    ax2.set_title("Distribución de Canales de Contacto")
    st.pyplot(fig2)

    if "probabilidad" in df.columns:
        st.subheader("Distribución de Probabilidades de Conversión")
        fig3, ax3 = plt.subplots()
        df["probabilidad"].hist(bins=20, ax=ax3)
        ax3.set_xlabel("Probabilidad")
        ax3.set_ylabel("Frecuencia")
        st.pyplot(fig3)
