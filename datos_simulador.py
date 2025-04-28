# app.py — Simulador con datos reales (ENE 2022 → ENE 2024)
# --------------------------------------------------------------------
# Copia‑pega este archivo único en tu repo y corre:
#   pip install streamlit pandas plotly statsmodels
#   streamlit run app.py
# No necesitas ningún Excel: los valores se embeben aquí mismo.

import pandas as pd
import streamlit as st
import plotly.express as px
import statsmodels.api as sm

# ------------------------------------------------------------
# 1. Datos embebidos (24 observaciones)
# ------------------------------------------------------------
FECHAS = [
    "2022-01-01", "2022-02-01", "2022-03-01", "2022-04-01", "2022-05-01", "2022-06-01", "2022-07-01", "2022-08-01", "2022-09-01", "2022-10-01", "2022-11-01", "2022-12-01", 
    "2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01", "2023-05-01", "2023-06-01", "2023-07-01", "2023-08-01", "2023-09-01", "2023-10-01", "2023-11-01", "2024-01-01",
]

PBI = [
    139.5, 138.0, 153.9, 156.1, 163.1, 163.9, 164.1, 164.1, 160.4, 159.9, 158.4, 158.8, 
    153.3, 155.1, 155.4, 149.1, 152.7, 151.6, 149.0, 150.7, 147.5, 146.7, 145.5, 137.3,
]

IPC = [
    605.0317, 633.4341, 676.0566, 716.9399, 753.147, 790.0339, 848.1981, 906.0927, 961.026, 1021.4317, 1074.5121, 1130.1678,
    1203.0185, 1262.3126, 1381.1601, 1497.2147, 1613.5895, 1709.6115, 1818.0838, 2044.2832, 2304.9242, 2496.273, 2816.0628, 4261.5324,
]

TCN = [
    103.9846, 106.3071, 109.4585, 113.3345, 117.7737, 122.6234, 129.7928, 137.5014, 144.5326, 152.8706, 160.1581, 170.9467,
    182.4677, 192.9011, 203.1055, 216.5559, 231.1908, 248.7617, 266.4647, 322.1341, 349.998, 350.0204, 353.8404, 818.3455,
]

ITCRM = [
    101.986673, 102.691842, 101.306247, 99.81559, 96.439443, 98.453567, 99.747081, 101.563098, 103.669433, 106.696137, 109.341478, 112.468594,
    113.955688, 111.881694, 93.588477, 93.80799, 93.048879, 93.964437, 95.847331, 104.82483, 100.667193, 89.628422, 83.19384, 132.780097,
]

DF = pd.DataFrame({
    "fecha": pd.to_datetime(FECHAS),
    "PBI": PBI,
    "IPC_%": IPC,
    "TCN": TCN,
    "ITCRM": ITCRM,
})

# ------------------------------------------------------------
# 2. Streamlit — configuración
# ------------------------------------------------------------
st.set_page_config(page_title="Simulador Macro 2022-2024", layout="wide")
st.title("Simulador Macroeconómico (ene‑2022 → ene‑2024)")

st.markdown(
    """
**Fuente:** Hoja *datos* de *Series argentina (2).xlsx* — columnas EMAE, IPC, TCN, ITCRM.
Dataset embebido para evitar dependencias externas.

### Cómo funciona el simulador
Usamos el modelo lineal didáctico:
```math
PBI_t = β₀ + β₁·IPC_t + β₂·TCN_t + β₃·ITCRM_t
```
Sin rezagos ni efectos no lineales; sirve solo para análisis de sensibilidad *ceteris‑paribus*.
""",
    unsafe_allow_html=True)

modo = st.sidebar.radio("Modo", ["Exploración", "Simulador"], index=0)

# 3. Exploración ------------------------------------------------------------
if modo == "Exploración":
    var = st.selectbox("Variable", ["PBI", "IPC_%", "TCN", "ITCRM"])
    fig = px.line(DF, x="fecha", y=var, markers=True, title=f"Evolución de {var}")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(DF.set_index("fecha"))

# 4. Simulador --------------------------------------------------------------
else:
    # Modelo lineal
    X = sm.add_constant(DF[["IPC_%", "TCN", "ITCRM"]])
    modelo = sm.OLS(DF["PBI"], X).fit()

    base_row = DF.iloc[-1]  # 2024‑01

    st.write("### Valores históricos (ene‑2024)")
    st.write(base_row[["PBI", "IPC_%", "TCN", "ITCRM"]])

    col1, col2, col3 = st.columns(3)
    d_ipc  = col1.slider("Shock IPC (%)",  -30.0, 30.0, 0.0, 0.5)
    d_tcn  = col2.slider("Shock TCN (%)",  -30.0, 30.0, 0.0, 0.5)
    d_itcr = col3.slider("Shock ITCRM (%)", -30.0, 30.0, 0.0, 0.5)

    X_new = [1,
             base_row["IPC_%"] * (1 + d_ipc/100),
             base_row["TCN"]    * (1 + d_tcn/100),
             base_row["ITCRM"] * (1 + d_itcr/100)]

    pbi_sim = float(modelo.predict([X_new]))
    diff_pct = (pbi_sim - base_row["PBI"]) / base_row["PBI"] * 100

    st.metric("PBI simulado (ene‑2024)", f"{pbi_sim:.2f}", f"{diff_pct:+.2f}% vs histórico")

    fig2 = px.bar(x=["Histórico", "Simulado"],
                  y=[base_row["PBI"], pbi_sim],
                  text=[f"{base_row['PBI']:.1f}", f"{pbi_sim:.1f}"],
                  labels={"x": "", "y": "PBI"})
    fig2.update_traces(textposition="outside")
    st.plotly_chart(fig2, use_container_width=True)

    st.info("Ejemplo didáctico — interpretaciones con cautela.")
