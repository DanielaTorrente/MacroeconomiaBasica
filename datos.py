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
# 2. SERIES DISPONIBLES (ID oficiales datos.gob.ar)
# ---------------------------------------------------------------------------
API_BASE = "https://apis.datos.gob.ar/series/api/series"
SERIES = {
    "Producto interno bruto (PBI)": "10.3_VMATS_1993_M_36",  # EMAE base 1993 (índice)
    "Inflación": "148.3_I2NG_2016_M_15",                      # IPC variación % mensual
    "Desempleo": "101.1_IUT_T_0_0_30",                       # Desocupación urbana trimestral
    "Tipo de cambio": "32.1_DOLAR_OFICIAL_0_0_16"             # TC fin de mes
}
DATA_DIR = pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 3. FUNCIONES AUXILIARES
# ---------------------------------------------------------------------------

def url_csv(serie_id: str) -> str:
    return f"{API_BASE}?ids={serie_id}&format=csv&collapse=month"

@st.cache_data(show_spinner=False, ttl=86_400)
def traer_csv_online(serie_id: str) -> pd.DataFrame:
    r = requests.get(url_csv(serie_id), timeout=20)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.text), parse_dates=["indice_tiempo"])

@st.cache_data(show_spinner=False, ttl=86_400)
def traer_csv_local(serie_id: str) -> pd.DataFrame:
    ruta = DATA_DIR / f"{serie_id}.csv"
    if not ruta.exists():
        return pd.DataFrame()
    return pd.read_csv(ruta, parse_dates=["indice_tiempo"])

@st.cache_data(show_spinner=False, ttl=0)
def descargar_y_guardar(serie_id: str) -> bool:
    """Descarga la serie y la guarda en ./data. Devuelve True si ok."""
    try:
        df = traer_csv_online(serie_id)
    except Exception:
        return False
    ruta = DATA_DIR / f"{serie_id}.csv"
    df.to_csv(ruta, index=False)
    return True

# ---------------------------------------------------------------------------
# 4. SIDEBAR
# ---------------------------------------------------------------------------
side = st.sidebar
side.title("Indicadores")
indicador = side.radio("Elegí un indicador", list(DEFINICIONES.keys()))
side.markdown("### Definición")
side.info(DEFINICIONES[indicador])

side.markdown("---")
side.markdown("### Conexión de datos")
modo = side.radio("Elegí la fuente de datos", ["Automático (online/local)", "Solo local"], index=0)

download_all = side.button("⬇️ Descargar / actualizar todas las series")
if download_all:
    with st.spinner("Descargando series…"):
        oks = []
        for sid in SERIES.values():
            oks.append(descargar_y_guardar(sid))
    if all(oks):
        side.success("Series descargadas correctamente ✔️")
    else:
        side.error("Alguna descarga falló. Verificá tu conexión.")

side.markdown(
    "Archivos CSV se guardan en *./data/*. Si trabajás completamente offline, colocá allí los archivos manualmente."
)

# ---------------------------------------------------------------------------
# 5. CARGA Y PREPARACIÓN DE DATOS
# ---------------------------------------------------------------------------
serie_id = SERIES[indicador]

# Estrategia: 1) intentar local, 2) si no hay y modo ≠ "Solo local" -> online -> guardar

df = traer_csv_local(serie_id)
if df.empty and modo == "Automático (online/local)":
    try:
        df = traer_csv_online(serie_id)
        # guardar para el futuro
        (DATA_DIR / f"{serie_id}.csv").write_text(df.to_csv(index=False))
    except Exception as e:
        st.error("No se pudo descargar la serie y no existe localmente. Cambiá a 'Solo local' o verifica tu red.")
        st.exception(e)
        st.stop()
elif df.empty:
    st.warning("No se encontró el CSV local. Colocalo en la carpeta *data/* o cambia a modo automático.")
    st.stop()

# Normalización columnas
df.rename(columns={"indice_tiempo": "fecha", serie_id: "valor"}, inplace=True)
df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
df.dropna(subset=["valor"], inplace=True)

# Desempleo trimestral → mensual
if indicador == "Desempleo":
    df.set_index("fecha", inplace=True)
    df = df.asfreq("M")
    df["valor"] = df["valor"].interpolate(method="linear")
    df.reset_index(inplace=True)

# ---------------------------------------------------------------------------
# 6. CONTROL RANGO DE FECHAS
# ---------------------------------------------------------------------------
min_ts, max_ts = df["fecha"].min(), df["fecha"].max()
min_date, max_date = min_ts.to_pydatetime(), max_ts.to_pydatetime()

yrs_back = 1 if indicador == "Inflación" else 3
try:
    default_start = max_date.replace(year=max_date.year - yrs_back)
except ValueError:
    default_start = max_date - relativedelta(years=yrs_back)

inicio, fin = st.slider(
    "Rango de fechas", min_value=min_date, max_value=max_date, value=(default_start, max_date), format="YYYY-MM"
)

mask = (df["fecha"] >= pd.to_datetime(inicio)) & (df["fecha"] <= pd.to_datetime(fin))
subset = df.loc[mask]
if subset.empty:
    st.warning("No hay datos para el rango seleccionado.")
    st.stop()

# ---------------------------------------------------------------------------
# 7. VISUALIZACIÓN
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

st.caption(
    "Fuente original: APIs de datos.gob.ar (INDEC/BCRA). Los CSV se almacenan en ./data/. "
    "Este tablero funciona sin conexión una vez descargado el set de datos."
)


