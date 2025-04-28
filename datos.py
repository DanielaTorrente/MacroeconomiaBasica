import streamlit as st
import pandas as pd
import plotly.express as px
import requests, io, os
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

# Conexión
offline = side.checkbox("Modo sin conexión (usar CSV locales 🗎)")

side.markdown("### Instrucciones")
side.markdown(
    """
    1. Seleccioná el indicador arriba.  
    2. Ajustá el rango de fechas con el *slider*.  
    3. Deslizá el cursor sobre la línea para ver valores puntuales.  
    4. Los datos se actualizan una vez al día cuando hay conexión.  
    5. Si la descarga falla, activá **Modo sin conexión** y guardá el CSV en la carpeta *data/*.  
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
def traer_serie(serie_id: str, sin_conexion: bool) -> pd.DataFrame:
    """Devuelve DataFrame con columnas fecha, valor. Si *sin_conexion* lee ./data/serie_id.csv"""
    if sin_conexion:
        ruta = os.path.join("data", f"{serie_id}.csv")
        if not os.path.exists(ruta):
            st.error(f"No encontré {ruta}. Descargá primero el CSV manualmente y colocalo en la carpeta data/.")
            return pd.DataFrame(columns=["fecha", "valor"])
        df = pd.read_csv(ruta, parse_dates=["indice_tiempo"])
    else:
        url = f"{API_BASE}?ids={serie_id}&format=csv&collapse=month"
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            df = pd.read_csv(io.StringIO(r.text), parse_dates=["indice_tiempo"])
        except Exception as e:
            st.warning("Fallo la descarga desde la API. Activá 'Modo sin conexión' y usá un CSV local.")
            st.exception(e)
            return pd.DataFrame(columns=["fecha", "valor"])
    df.rename(columns={"indice_tiempo": "fecha", serie_id: "valor"}, inplace=True)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df.dropna(subset=["valor"], inplace=True)
    return df

@st.cache_data(ttl=86_400)
def cargar_datos(ind, sin_conexion=False):
    serie_id = IDS[ind]
    df = traer_serie(serie_id, sin_conexion)
    # Desempleo trimestral → mensual
    if ind == "Desempleo" and not df.empty:
        df.set_index("fecha", inplace=True)
        df = df.asfreq("M")
        df["valor"] = df["valor"].interpolate(method="linear")
        df.reset_index(inplace=True)
    return df

# ---------------------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------------------
with st.spinner("Cargando datos…"):
    df = cargar_datos(indicador, offline)

if df.empty:
    st.stop()

# ---------------------------------------------------------------------------
# CONTROL DE FECHAS
# ---------------------------------------------------------------------------
min_ts, max_ts = df["fecha"].min(), df["fecha"].max()
min_date, max_date = min_ts.to_pydatetime(), max_ts.to_pydatetime()

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

if subset.empty:
    st.warning("No hay datos para el rango seleccionado. Probá ampliar el período.")
    st.stop()

fig = px.line(subset, x="fecha", y="valor",
              title=f"{indicador} – {inicio.strftime('%Y-%m')} a {fin.strftime('%Y-%m')}",
              markers=True)
fig.update_layout(hovermode="x unified", xaxis_title="Fecha", yaxis_title="Valor", height=500)

st.plotly_chart(fig, use_container_width=True)

with st.expander("Ver datos tabulados"):
    st.dataframe(subset.rename(columns={"fecha": "Fecha", "valor": "Valor"}))

st.caption("Fuente: APIs de datos.gob.ar (INDEC/BCRA) – actualización diaria cuando hay conexión")

