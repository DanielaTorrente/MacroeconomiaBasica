import streamlit as st
import pandas as pd
import plotly.express as px
import requests, io, os, pathlib
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="Tablero Macroeconómico – Unidad 1", layout="wide")

# ---------------------------------------------------------------------------
# 1. DEFINICIONES
# ---------------------------------------------------------------------------
DEFINICIONES = {
    "Producto interno bruto (PBI)": "Bienes y servicios de demanda final producidos dentro de una economía durante un periodo determinado (generalmente un año).",
    "Inflación": "Aumento sostenido en el tiempo del nivel general de precios.",
    "Desempleo": "Porcentaje de personas que integran la población económicamente activa que no tienen trabajo y lo buscan activamente.",
    "Tipo de cambio": "Cantidad de unidades de moneda nacional necesarias para obtener una unidad de moneda extranjera."
}

# ---------------------------------------------------------------------------
# 2. SERIES OFICIALES (API datos.gob.ar)
# ---------------------------------------------------------------------------
API_BASE = "https://apis.datos.gob.ar/series/api/series"
SERIES = {
    "Producto interno bruto (PBI)": "10.3_VMATS_1993_M_36",   # EMAE índice (mensual)
    "Inflación": "148.3_I2NG_2016_M_15",                     # IPC variación % mensual
    "Desempleo": "101.1_IUT_T_0_0_30",                      # Desocupación urbana (trimestral)
    "Tipo de cambio": "32.1_DOLAR_OFICIAL_0_0_16"            # TC oficial fin de mes
}

DATA_DIR = pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 3. DESCARGA Y CARGA DE DATOS REALES
# ---------------------------------------------------------------------------

def url_csv(serie_id: str) -> str:
    return f"{API_BASE}?ids={serie_id}&format=csv&collapse=month"

@st.cache_data(show_spinner=False, ttl=86_400)
def descargar_serie(serie_id: str) -> pd.DataFrame:
    """Descarga la serie desde datos.gob.ar y la devuelve como DataFrame."""
    r = requests.get(url_csv(serie_id), timeout=30)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text), parse_dates=["indice_tiempo"])

@st.cache_data(show_spinner=False, ttl=86_400)
def cargar_csv_local(serie_id: str) -> pd.DataFrame:
    ruta = DATA_DIR / f"{serie_id}.csv"
    if not ruta.exists():
        return pd.DataFrame()
    return pd.read_csv(ruta, parse_dates=["indice_tiempo"])

@st.cache_data(show_spinner=False, ttl=0)
def guardar_csv(df: pd.DataFrame, serie_id: str):
    ruta = DATA_DIR / f"{serie_id}.csv"
    df.to_csv(ruta, index=False)

# ---------------------------------------------------------------------------
# 4. SIDEBAR
# ---------------------------------------------------------------------------
side = st.sidebar
side.title("Indicadores")
indicador = side.radio("Elegí un indicador", list(DEFINICIONES.keys()))
side.markdown("### Definición")
side.info(DEFINICIONES[indicador])

side.markdown("---")
if side.button("⬇️ Descargar / actualizar todas las series"):
    with st.spinner("Descargando series oficiales …"):
        success = True
        for sid in SERIES.values():
            try:
                df_tmp = descargar_serie(sid)
                guardar_csv(df_tmp, sid)
            except Exception as e:
                success = False
                st.error(f"No se pudo descargar {sid}: {e}")
        if success:
            side.success("✅ Series guardadas en ./data.")

side.caption("La app usa primero los archivos locales en ./data/. Si faltan, intentará descargarlos del API oficial de datos.gob.ar (INDEC/BCRA). Se cachea 24 h.")

# ---------------------------------------------------------------------------
# 5. OBTENER DATOS (PRIORIDAD: LOCAL → ONLINE)
# ---------------------------------------------------------------------------
serie_id = SERIES[indicador]
df = cargar_csv_local(serie_id)

if df.empty:
    try:
        df = descargar_serie(serie_id)
        guardar_csv(df, serie_id)
        st.toast("Serie descargada directamente del API oficial.")
    except Exception as err:
        st.error("No se pudo obtener la serie desde el API ni desde archivos locales. Verificá tu conexión o descargá las series con el botón del sidebar.")
        st.stop()

# ---------------------------------------------------------------------------
# 6. PREPARAR DATOS
# ---------------------------------------------------------------------------

df.rename(columns={"indice_tiempo": "fecha", serie_id: "valor"}, inplace=True)
df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
df.dropna(subset=["valor"], inplace=True)

if indicador == "Desempleo":
    # Convertir trimestral a mensual para que el slider sea uniforme
    df.set_index("fecha", inplace=True)
    df = df.asfreq("M")
    df["valor"] = df["valor"].interpolate(method="linear")
    df.reset_index(inplace=True)

# ---------------------------------------------------------------------------
# 7. SLIDER DE FECHAS
# ---------------------------------------------------------------------------
min_date, max_date = df["fecha"].min().to_pydatetime(), df["fecha"].max().to_pydatetime()

years_back_default = 3 if indicador != "Inflación" else 1
def_start = max_date - relativedelta(years=years_back_default)

inicio, fin = st.slider(
    "Rango de fechas",
    min_value=min_date,
    max_value=max_date,
    value=(def_start, max_date),
    format="YYYY-MM",
)

subset = df[(df["fecha"] >= pd.to_datetime(inicio)) & (df["fecha"] <= pd.to_datetime(fin))]
if subset.empty:
    st.warning("No hay datos para el rango seleccionado.")
    st.stop()

# ---------------------------------------------------------------------------
# 8. GRÁFICO
# ---------------------------------------------------------------------------
fig = px.line(
    subset,
    x="fecha",
    y="valor",
    title=f"{indicador} – {inicio.strftime('%Y-%m')} a {fin.strftime('%Y-%m')}",
    markers=True,
)
fig.update_layout(hovermode="x unified", xaxis_title="Fecha", yaxis_title="Valor", height=500)

st.plotly_chart(fig, use_container_width=True)

with st.expander("Ver datos tabulados"):
    st.dataframe(subset.rename(columns={"fecha": "Fecha", "valor": "Valor"}))

st.caption("Fuente: APIs oficiales de datos.gob.ar (INDEC • BCRA). Las series se descargan y almacenan localmente para trabajar sin conexión.")
