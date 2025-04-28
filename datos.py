import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from urllib.error import HTTPError
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Tablero Macroeconómico – Unidad 1", layout="wide")

# ---------------------------------------------------------------------------
# DEFINICIONES
# ---------------------------------------------------------------------------
DEFINICIONES = {
    "Producto interno bruto (PBI)": "Bienes y servicios de demanda final producidos dentro de una economía durante un periodo determinado (generalmente un año).",
    "Inflación": "Aumento sostenido en el tiempo del nivel general de precios.",
    "Desempleo": "Porcentaje de personas que integran la población económicamente activa que no tienen trabajo y lo buscan activamente.",
    "Tipo de cambio": "Cantidad de unidades de moneda nacional necesarias para obtener una unidad de moneda extranjera."
}

# ---------------------------------------------------------------------------
# BARRA LATERAL
# ---------------------------------------------------------------------------
side = st.sidebar
side.title("Indicadores")
indicador = side.radio("Elegí un indicador", list(DEFINICIONES.keys()))
side.markdown("### Definición")
side.info(DEFINICIONES[indicador])
side.markdown("### Instrucciones")
side.markdown(
    """
    1. Seleccioná el indicador arriba.  
    2. Ajustá el rango de fechas con el *slider*.  
    3. Deslizá el cursor sobre la línea para ver valores puntuales.  
    4. Los datos se actualizan una vez al día.  
    """
)

# ---------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------------------
API_BASE = "https://apis.datos.gob.ar/series/api/series"

IDS = {
    # Todas series mensuales
    "Producto interno bruto (PBI)": "10.3_VMATS_1993_M_36",  # EMAE base 1993 (índice)
    "Inflación": "148.3_I2NG_2016_M_15",                      # IPC variación % mensual
    "Desempleo": "101.1_IUT_T_0_0_30",                       # Desocupación trimestral (se interpolará)
    "Tipo de cambio": "32.1_DOLAR_OFICIAL_0_0_16"             # TC fin de mes
}

@st.cache_data(ttl=86_400)
def traer_serie_csv(serie_id: str) -> pd.DataFrame:
    """Descarga una serie desde apis.datos.gob.ar y devuelve DataFrame."""
    url = f"{API_BASE}?ids={serie_id}&format=csv&collapse=month"
    try:
        df = pd.read_csv(url, parse_dates=["indice_tiempo"])
    except HTTPError as e:
        st.error(f"No se pudo descargar la serie {serie_id}: {e}")
        return pd.DataFrame(columns=["fecha", "valor"])
    df.rename(columns={"indice_tiempo": "fecha", serie_id: "valor"}, inplace=True)
    return df.dropna()

@st.cache_data(ttl=86_400)
def cargar_datos(ind):
    serie_id = IDS[ind]
    df = traer_serie_csv(serie_id)

    # Tratamiento especial para Desempleo trimestral → mensual
    if ind == "Desempleo" and not df.empty:
        df.set_index("fecha", inplace=True)
        df = df.asfreq("M")
        df["valor"] = df["valor"].interpolate(method="linear")
        df.reset_index(inplace=True)
    return df

# ---------------------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------------------
with st.spinner("Descargando datos…"):
    df = cargar_datos(indicador)

if df.empty:
    st.stop()

# ---------------------------------------------------------------------------
# CONVERSIÓN DE FECHAS A datetime (para evitar KeyError en slider)
# ---------------------------------------------------------------------------
min_ts = df["fecha"].min()
max_ts = df["fecha"].max()

min_date = min_ts.to_pydatetime()
max_date = max_ts.to_pydatetime()

# Valor inicial (3 años atrás, 1 si Inflación)
yrs_back = 1 if indicador == "Inflación" else 3
try:
    default_start = max_date.replace(year=max_date.year - yrs_back)
except ValueError:
    default_start = max_date - relativedelta(years=yrs_back)

inicio, fin = st.slider(
    "Rango de fechas",
    min_value=min_date,
    max_value=max_date,
    value=(default_start, max_date),
    format="YYYY-MM"
)

# ---------------------------------------------------------------------------
# FILTRADO Y VISUALIZACIÓN
# ---------------------------------------------------------------------------
mask = (df["fecha"] >= pd.to_datetime(inicio)) & (df["fecha"] <= pd.to_datetime(fin))
subset = df.loc[mask]

fig = px.line(subset, x="fecha", y="valor",
              title=f"{indicador} – {inicio.strftime('%Y-%m')} a {fin.strftime('%Y-%m')}",
              markers=True)
fig.update_layout(hovermode="x unified", xaxis_title="Fecha", yaxis_title="Valor", height=500)

st.plotly_chart(fig, use_container_width=True)

# Tabla detallada
with st.expander("Ver datos tabulados"):
    st.dataframe(subset.rename(columns={"fecha": "Fecha", "valor": "Valor"}))

# Fuente
st.caption(f"Fuente: APIs de datos.gob.ar (INDEC/BCRA) – actualizado al {max_date.strftime('%d-%m-%Y')}")
