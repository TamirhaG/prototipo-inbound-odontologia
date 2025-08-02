import matplotlib.pyplot as plt

def grafico_servicios(df):
    fig, ax = plt.subplots()
    df['servicio'].value_counts().plot(kind='bar', ax=ax, color='#85C1E9')
    ax.set_title("Leads por Servicio")
    ax.set_xlabel("Servicio")
    ax.set_ylabel("Cantidad")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

def grafico_interes(df):
    fig, ax = plt.subplots()
    df['interes_activo'].value_counts().sort_index().plot(kind='bar', ax=ax, color=['#58D68D', '#F1948A'])
    ax.set_xticklabels(['No interesado', 'Interesado'], rotation=0)
    ax.set_title("Leads Activos vs No Activos")
    ax.set_ylabel("Cantidad")
    plt.tight_layout()
    return fig