# tablero_macroeconomia.py — Tablero interactivo 2022‑2024
# --------------------------------------------------------------------
# Copia este archivo en tu proyecto y ejecuta:
#   pip install streamlit pandas plotly
#   streamlit run tablero_macroeconomia.py
# No requiere archivos externos: los valores se embeben aquí.

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ------------------------------------------------------------
# 1. Datos reales suministrados (ene‑2022 → dic‑2024)
# ------------------------------------------------------------
_raw = [
    ("112022",146.50,1079.28, 90.10, 162.12),
    ("122022",144.50,1134.59, 93.21, 172.90),
    ("12023",143.00,1202.98, 95.14, 182.24),
    ("22023",137.60,1282.71, 94.77, 191.89),
    ("32023",155.40,1381.16, 93.59, 203.11),
    ("42023",149.10,1497.21, 93.81, 216.56),
    ("52023",152.70,1613.59, 93.05, 231.19),
    ("62023",151.60,1709.61, 93.96, 248.76),
    ("72023",149.00,1818.08, 95.85, 266.46),
    ("82023",150.70,2044.28,104.82, 322.13),
    ("92023",147.50,2304.92,100.67, 350.00),
    ("102023",146.70,2496.27, 89.63, 350.02),
    ("112023",145.50,2816.06, 83.19, 353.84),
    ("121899",138.40,3533.19,124.87, 641.99),
    ("12024",137.30,4261.53,132.78, 818.35),
    ("22024",133.80,4825.79,115.76, 834.91),
    ("32024",142.40,5357.09,105.87, 850.34),
    ("42024",145.50,5830.23, 97.02, 868.96),
    ("52024",154.80,6073.72, 93.43, 886.86),
    ("62024",145.40,6351.71, 89.90, 903.78),
    ("72024",148.20,6607.75, 87.88, 923.77),
    ("82024",146.00,6883.44, 87.16, 942.92),
    ("92024",143.70,7122.24, 86.05, 961.83),
    ("102024",146.00,7313.95, 84.05, 981.57),
    ("112024",146.10,7491.43, 81.75,1001.84),
    ("122024",146.00,7694.01, 79.79,1020.71),
]

def parse_mmYYYY(code: str):
    """Convierte códigos como '112022' o '12023' a Timestamp.
    Descarta valores cuyo año sea < 1900 para evitar ValueError."""
    code = code.strip()
    if len(code) == 6:  # ej. 112022
        m, y = int(code[0]), int(code[1:])
    else:              # ej. 12023
        m, y = int(code[:-4]), int(code[-4:])
    if y < 1900 or m < 1 or m > 12:
        return None  # se descartará luego
    return pd.Timestamp(year=y, month=m, day=1)

rows = []
for c, pbi, ipc, itcrm, tcn in _raw:
    fecha = parse_mmYYYY(c)
    if fecha is None:
        continue
    rows.append({
        "Fecha": fecha,
        "PBI": pbi,
        "IPC": ipc,
        "ITCRM": itcrm,
        "TCN": tcn,
    })
for c, pbi, ipc, itcrm, tcn in _raw:
    rows.append({
        "Fecha": parse_mmYYYY(c),
        "PBI": pbi,
        "IPC": ipc,
        "ITCRM": itcrm,
        "TCN": tcn,
    })

df = pd.DataFrame(rows).sort_values("Fecha").reset_index(drop=True)

# ------------------------------------------------------------
# 2. Streamlit — configuración y textos
# ------------------------------------------------------------
st.set_page_config(page_title="Tablero Macro 2022‑2024", layout="wide")
st.title("🌎 Tablero Interactivo de Indicadores Macroeconómicos (2022‑2024)")

st.markdown(
    """
### Definiciones
| Sigla | Descripción | Fuente |
|-------|-------------|--------|
| **EMAE** | Estimador Mensual de Actividad Económica; aproxima la trayectoria mensual del PIB. | INDEC |
| **IPC** | Índice de Precios al Consumidor; variación del nivel general de precios. | INDEC |
| **TCN** | Tipo de Cambio Nominal promedio mensual (pesos por dólar). | BCRA |
| **ITCRM** | Índice de Tipo de Cambio Real Multilateral; mide competitividad frente a socios. | BCRA |

---
**Cómo usar el tablero**
1. Selecciona uno o dos indicadores.
2. Ajusta el rango de fechas.
3. Explora el gráfico interactivo y descarga la tabla filtrada.
""",
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# 3. Interactividad
# ------------------------------------------------------------
indicadores = ["PBI", "IPC", "ITCRM", "TCN"]
ind1 = st.selectbox("🔹 Indicador 1", indicadores)
ind2 = st.selectbox("🔹 Indicador 2 (opcional)", ["Ninguno"] + indicadores)

rango = st.slider(
    "🗓️ Rango de fechas",
    min_value=df["Fecha"].min().to_pydatetime(),
    max_value=df["Fecha"].max().to_pydatetime(),
    value=(df["Fecha"].min().to_pydatetime(), df["Fecha"].max().to_pydatetime()),
)

df_filt = df[(df["Fecha"] >= rango[0]) & (df["Fecha"] <= rango[1])]

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_filt["Fecha"], y=df_filt[ind1], name=ind1, yaxis="y1"))
if ind2 != "Ninguno":
    fig.add_trace(go.Scatter(x=df_filt["Fecha"], y=df_filt[ind2], name=ind2, yaxis="y2"))

fig.update_layout(
    title=f"Evolución de {ind1}" + (f" y {ind2}" if ind2 != "Ninguno" else ""),
    xaxis_title="Fecha",
    yaxis=dict(title=ind1),
    yaxis2=dict(title=ind2, overlaying="y", side="right") if ind2 != "Ninguno" else None,
    legend=dict(x=0.01, y=0.99),
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(df_filt, height=250)

st.download_button(
    "📥 Descargar CSV filtrado",
    data=df_filt.to_csv(index=False),
    file_name="indicadores_filtrados.csv",
    mime="text/csv",
)

# ------------------------------------------------------------
# 4. Consignas de análisis
# ------------------------------------------------------------
st.markdown(
    """
### ✏️ Consignas
1. Describe la tendencia del EMAE entre 2022 y 2024.
2. ¿Observas correlación visible entre IPC y TCN?
3. Al focalizar en 2023‑08 ↔ 2023‑11, ¿qué sucede con ITCRM y el tipo de cambio?
4. ¿Qué podría explicar el salto de IPC en 2023‑11?
5. Descarga el CSV filtrado y calcula la variación interanual del IPC.
"""
)
