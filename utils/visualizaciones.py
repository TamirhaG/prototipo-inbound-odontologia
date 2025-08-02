import matplotlib.pyplot as plt

def grafico_servicios(df):
    conteo_servicios = df["servicio"].value_counts()
    fig, ax = plt.subplots()
    ax.bar(conteo_servicios.index, conteo_servicios.values, color="#66b3ff")
    ax.set_title("Leads por Servicio")
    ax.set_xticklabels(conteo_servicios.index, rotation=45)
    return fig

def grafico_interes(df):
    activos = df["interes_activo"].value_counts().sort_index()
    fig, ax = plt.subplots()
    ax.pie(activos, labels=["No Interesado", "Interesado"], autopct="%1.1f%%", colors=["#f1948a", "#58d68d"])
    ax.set_title("Distribución de Interés")
    return fig
