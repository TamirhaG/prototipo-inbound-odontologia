# Inbound Marketing con IA para Clínica Odontológica

Este proyecto es parte del curso **"Desarrollo de soluciones con IA"** de la carrera **Ciencia de Datos e Inteligencia Artificial**. Se ha desarrollado un prototipo funcional que implementa una solución de captación y análisis de leads (clientes potenciales) usando herramientas de IA.

---

## Objetivo del proyecto

Crear un sistema que permita:
- Captar leads desde diversos canales digitales (redes sociales, WhatsApp, etc.).
- Visualizar métricas clave de conversión y engagement.
- Entrenar un modelo de IA para predecir el interés real de un lead (versión futura).
- Apoyar a la clínica en sus procesos de marketing y atención.

---

## Componentes del prototipo

### 1. **Captura de leads**
- Formulario en Streamlit con los siguientes campos:
  - Nombre, correo, teléfono
  - Servicio de interés (ortodoncia, limpieza, etc.)
  - Canal de contacto (Instagram, WhatsApp, etc.)
- Los datos se almacenan en un archivo CSV (`leads_ver1.csv`)

### 2. **Dashboard de análisis**
- Total de leads registrados
- Tasa de conversión (interés activo)
- Gráficos:
  - Leads por servicio
  - Leads activos vs no activos
- Tabla de leads recientes
- Descarga de archivo CSV

### 3. **Modelo de IA** 
- Entrenamiento con datos históricos
- Predicción del nivel de interés de un lead nuevo

---

## Tecnologías utilizadas

- `Python`
- `Streamlit` (para frontend interactivo)
- `Pandas` y `Matplotlib` (para análisis y visualización)
- `scikit-learn` (para IA, versión futura)
- Control de versiones con `Git` y desarrollo en `GitHub.dev`

---

## Estructura del repositorio

```plaintext
prototipo-inbound-odontologia/
│
├── app.py                  # App principal en Streamlit
├── leads_ver1.csv          # Base de datos de leads (datos simulados)
├── requirements.txt        # Dependencias del proyecto
├── modelo/
│   └── modelo_interes.pkl  # Modelo IA entrenado
├── utils/
│   └── visualizaciones.py  # Funciones auxiliares 
└── README.md               # Este archivo

```

---

## Cómo ejecutar

```bash
# Requisitos: Python 3.8+ y pip
pip install -r requirements.txt
streamlit run app.py
```

---

## Estado actual

Fase 1: Captura y visualización de leads  
Fase 2: Entrenamiento del modelo predictivo  
Fase 3: Recolección de feedback de usuarios y mejoras finales

---

## Autora

**Tamirha Giraldo**  
Estudiante de Ciencia de Datos e Inteligencia Artificial  

---

