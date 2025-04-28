import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

st.set_page_config(page_title="Tablero Macroeconómico – Unidad 1", layout="wide")

# ----- Definiciones ---------------------------------------------------------- #
DEFINICIONES = {
    "Producto interno bruto (PBI)": "Bienes y servicios de demanda final producidos dentro de una economía durante un periodo determinado (generalmente un año).",
    "Inflación": "Aumento sostenido en el tiempo del nivel general de precios.",
    "Desempleo": "Porcentaje de personas que integran la población económicamente activa que no tienen trabajo y lo buscan activamente.",
    "Tipo de cambio": "Cantidad de unidades de moneda nacional necesarias para obtener una unidad de moneda extranjera."
}

# Sidebar – Selección de indicador
st.sidebar.title("Indicadores")
indicador = st.sidebar.radio(
    "Elegí un indicador",
    list(DEFINICIONES.keys())
)

# Sidebar – Definición
st.sidebar.markdown("### Definición")
st.sidebar.info(DEFINICIONES[indicador])

# Sidebar – Instrucciones
st.sidebar.markdown("### Instrucciones")
st.sidebar.markdown(
    """
1. Seleccioná el indicador arriba.
2. Usá el _slider_ de fechas para acotar el rango.
3. Hacé **zoom** o pasá el cursor por la línea para ver valores.
4. Los datos se actualizan automáticamente cada día (fuentes INDEC, BCRA, MECON).
"""
)

# ----- Funciones auxiliares -------------------------------------------------- #
@st.cache_data(ttl=86_400)
def traer_serie_csv(serie_id: str) -> pd.DataFrame:
    """Descarga una serie mensual desde apis.datos.gob.ar y devuelve un DataFrame."""
    url = f"https://apis.datos.gob.ar/series/api/series/?ids={serie_id}&format=csv&collapse=month"
    df = pd.read_csv(url, parse_dates=["indice_tiempo"])
    df.rename(columns={"indice_tiempo": "fecha", serie_id: "valor"}, inplace=True)
    return df.dropna()

def cargar_datos(ind):
    """Despacha la serie según el indicador seleccionado."""
    if ind == "Producto interno bruto (PBI)":
        # EMAE nivel general (serie base 2004=100)
        return traer_serie_csv("143.3_EMAE_0_0_26")
    if ind == "Inflación":
        # IPC nivel general variación % mensual (base dic‑2016=100)
        return traer_serie_csv("148.3_I2NG_2016_M_15")
    if ind == "Desempleo":
        # Tasa de desocupación urbana trimestral – se interpola a mensual para graficar
        return traer_serie_csv("101.1_IUT_T_0_0_30")
    if ind == "Tipo de cambio":
        # Dólar oficial mayorista fin de mes
        return traer_serie_csv("32.1_DOLAR_OFICIAL_0_0_16")

# Carga de datos
with st.spinner("Descargando datos…"):
    df = cargar_datos(indicador)

# ----- Selección de rango temporal ------------------------------------------ #
min_date = df["fecha"].min()
max_date = df["fecha"].max()

inicio, fin = st.slider(
    "Seleccioná el rango de fechas",
    min_value=min_date,
    max_value=max_date,
    value=(max(min_date, max_date.replace(year=max_date.year-3)), max_date),
    format="YYYY-MM"
)

mask = (df["fecha"] >= inicio) & (df["fecha"] <= fin)
df_rango = df.loc[mask]

# ----- Visualización --------------------------------------------------------- #
fig = px.line(
    df_rango,
    x="fecha",
    y="valor",
    title=f"{indicador} ({inicio.strftime('%Y-%m')} – {fin.strftime('%Y-%m')})",
    markers=True
)
fig.update_layout(hovermode="x unified")

st.plotly_chart(fig, use_container_width=True)

# Tabla de datos
with st.expander("Ver datos tabulados"):
    st.dataframe(df_rango.rename(columns={"fecha": "Fecha", "valor": "Valor"}))
