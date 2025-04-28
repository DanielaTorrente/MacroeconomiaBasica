# tablero_macroeconomia.py — Tablero interactivo 2022‑2024 + Variaciones
# -----------------------------------------------------------------------------
# Ejecutar con:
#   pip install streamlit pandas plotly
#   streamlit run tablero_macroeconomia.py
# ——————————————————————————————————————————————————————————

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ------------------------------------------------------------
# 1  Datos suministrados (ene‑2022 → dic‑2024) — valores reales
# ------------------------------------------------------------
_raw = [
    ("112022", 146.50, 1079.28,  90.10, 162.12),
    ("122022", 144.50, 1134.59,  93.21, 172.90),
    ("12023",  143.00, 1202.98,  95.14, 182.24),
    ("22023",  137.60, 1282.71,  94.77, 191.89),
    ("32023",  155.40, 1381.16,  93.59, 203.11),
    ("42023",  149.10, 1497.21,  93.81, 216.56),
    ("52023",  152.70, 1613.59,  93.05, 231.19),
    ("62023",  151.60, 1709.61,  93.96, 248.76),
    ("72023",  149.00, 1818.08,  95.85, 266.46),
    ("82023",  150.70, 2044.28, 104.82, 322.13),
    ("92023",  147.50, 2304.92, 100.67, 350.00),
    ("102023", 146.70, 2496.27,  89.63, 350.02),
    ("112023", 145.50, 2816.06,  83.19, 353.84),
    # 121899 descartado
    ("12024",  137.30, 4261.53, 132.78, 818.35),
    ("22024", 133.80, 4825.79, 115.76, 834.91),
    ("32024", 142.40, 5357.09, 105.87, 850.34),
    ("42024", 145.50, 5830.23,  97.02, 868.96),
    ("52024", 154.80, 6073.72,  93.43, 886.86),
    ("62024", 145.40, 6351.71,  89.90, 903.78),
    ("72024", 148.20, 6607.75,  87.88, 923.77),
    ("82024", 146.00, 6883.44,  87.16, 942.92),
    ("92024", 143.70, 7122.24,  86.05, 961.83),
    ("102024",146.00, 7313.95,  84.05, 981.57),
    ("112024",146.10, 7491.43,  81.75,1001.84),
    ("122024",146.00, 7694.01,  79.79,1020.71),
]

def parse_mmYYYY(code: str):
    digits = ''.join(ch for ch in code if ch.isdigit())
    if len(digits) < 5:
        return None
    m, y = int(digits[:-4]), int(digits[-4:])
    if not (1 <= m <= 12) or y < 1900:
        return None
    return pd.Timestamp(year=y, month=m, day=1)

rows = [
    {"Fecha": parse_mmYYYY(c), "EMAE": pbi, "IPC": ipc, "ITCRM": itcrm, "TCN": tcn}
    for c, pbi, ipc, itcrm, tcn in _raw if parse_mmYYYY(c) is not None
]

df = pd.DataFrame(rows).sort_values("Fecha").reset_index(drop=True)

# -----------------------------------------------------------------
# 2  Funciones auxiliares
# -----------------------------------------------------------------

def tasa_variacion(series: pd.Series) -> pd.Series:
    """Δ% intermensual"""
    return series.pct_change()*100

# Pre‑calcular variaciones
for col in ["IPC", "ITCRM"]:
    df[f"Var_%_{col}"] = tasa_variacion(df[col])

# -----------------------------------------------------------------
# 3  Interfaz Streamlit
# -----------------------------------------------------------------

st.set_page_config(page_title="Tablero Macro 2022‑2024", layout="wide")
st.title("🌎 Tablero Interactivo de Indicadores Macroeconómicos (2022‑2024)")

st.markdown("""
### Definiciones
| Sigla | Descripción | Fuente |
|-------|-------------|--------|
| **EMAE** | Estimador Mensual de Actividad Económica; aproxima el PIB. | INDEC |
| **IPC**  | Índice de Precios al Consumidor. | INDEC |
| **TCN**  | Tipo de Cambio Nominal (promedio mensual, ARS/USD). | BCRA |
| **ITCRM**| Índice de Tipo de Cambio Real Multilateral. | BCRA |

---
**Fórmulas clave**

* **Inflación mensual**:  
$\displaystyle \pi_t = \frac{IPC_t - IPC_{t-1}}{IPC_{t-1}}\times 100$
* **ITCRM básico** (conceptual):  
$\displaystyle ITCRM_t = TCN_t\times\frac{P_{socios}}{P_{arg}}$

---
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Sección", ["Gráficos", "Variaciones IPC/ITCRM"])

# ------------------------------ Sección 1 -----------------------------------
if menu == "Gráficos":
    st.subheader("📈 Evolución de indicadores")
    indicadores = ["EMAE", "IPC", "ITCRM", "TCN"]
    col1, col2 = st.columns(2)
    ind1 = col1.selectbox("Indicador 1", indicadores)
    ind2 = col2.selectbox("Indicador 2 (opcional)", ["Ninguno"]+indicadores)

    r1, r2 = st.slider(
        "Rango de fechas",
        min_value=df["Fecha"].min().to_pydatetime(),
        max_value=df["Fecha"].max().to_pydatetime(),
        value=(df["Fecha"].min().to_pydatetime(), df["Fecha"].max().to_pydatetime()),
    )
    df_filt = df[(df["Fecha"]>=r1)&(df["Fecha"]<=r2)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filt["Fecha"], y=df_filt[ind1], name=ind1, yaxis="y1"))
    if ind2!="Ninguno":
        fig.add_trace(go.Scatter(x=df_filt["Fecha"], y=df_filt[ind2], name=ind2, yaxis="y2"))
        fig.update_layout(yaxis2=dict(title=ind2, overlaying="y", side="right"))
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df_filt, height=250)
    st.download_button("Descargar CSV", df_filt.to_csv(index=False), "indicadores.csv", "text/csv")

    st.markdown("""
---
### ✏️ Consignas de reflexión
1. Describe la tendencia del **EMAE** y vincúlala con los picos del **IPC**.
2. ¿Qué sucedió con el **ITCRM** cuando el **TCN** superó los 800 ARS/USD?
3. ¿Observas una relación entre depreciaciones del peso y aceleraciones de la inflación?
4. ¿En qué meses el **ITCRM** sugiere mayor competitividad cambiaria?
""")

# ---------------------------- Sección 2 -------------------------------------
else:
    st.subheader("📊 Variaciones mensuales de IPC e ITCRM")

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=df["Fecha"], y=df["Var_%_IPC"], name="Δ% IPC"))
    fig2.add_trace(go.Bar(x=df["Fecha"], y=df["Var_%_ITCRM"], name="Δ% ITCRM", opacity=0.7))
    fig2.update_layout(barmode="group", template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(df[["Fecha","Var_%_IPC","Var_%_ITCRM"]], height=250)

    st.download_button("Descargar variaciones", df[["Fecha","Var_%_IPC","Var_%_ITCRM"]].to_csv(index=False),
                       "variaciones_ipc_itcrm.csv", "text/csv")

    st.markdown("""
#### Consignas para esta sección
1. Identifica el mes con la mayor inflación mensual. ¿Coincide con un salto del ITCRM?
2. ¿Hubo meses donde el ITCRM cayó mientras la inflación subía? Explica posibles causas.
3. ¿Qué patrón ves en las variaciones del ITCRM tras las grandes devaluaciones?
""")
