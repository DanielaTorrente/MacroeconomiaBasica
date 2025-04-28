# tablero_macroeconomia.py — Tablero interactivo 2022‑2024 + Variaciones + Respuestas identificadas
# ----------------------------------------------------------------------------------
# Ejecutar con:
#   pip install streamlit pandas plotly
#   streamlit run tablero_macroeconomia.py

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ============================================================
# 1  Datos suministrados (ene‑2022 → dic‑2024)
# ============================================================
_raw = [
    ("112022",146.50,1079.28, 90.10,162.12),("122022",144.50,1134.59, 93.21,172.90),
    ("12023",143.00,1202.98, 95.14,182.24),("22023",137.60,1282.71, 94.77,191.89),
    ("32023",155.40,1381.16, 93.59,203.11),("42023",149.10,1497.21, 93.81,216.56),
    ("52023",152.70,1613.59, 93.05,231.19),("62023",151.60,1709.61, 93.96,248.76),
    ("72023",149.00,1818.08, 95.85,266.46),("82023",150.70,2044.28,104.82,322.13),
    ("92023",147.50,2304.92,100.67,350.00),("102023",146.70,2496.27, 89.63,350.02),
    ("112023",145.50,2816.06, 83.19,353.84),("12024",137.30,4261.53,132.78,818.35),
    ("22024",133.80,4825.79,115.76,834.91),("32024",142.40,5357.09,105.87,850.34),
    ("42024",145.50,5830.23, 97.02,868.96),("52024",154.80,6073.72, 93.43,886.86),
    ("62024",145.40,6351.71, 89.90,903.78),("72024",148.20,6607.75, 87.88,923.77),
    ("82024",146.00,6883.44, 87.16,942.92),("92024",143.70,7122.24, 86.05,961.83),
    ("102024",146.00,7313.95, 84.05,981.57),("112024",146.10,7491.43, 81.75,1001.84),
    ("122024",146.00,7694.01, 79.79,1020.71),
]

def parse_mmYYYY(code:str):
    digits=''.join(ch for ch in code if ch.isdigit())
    if len(digits)<5:
        return None
    m,y=int(digits[:-4]),int(digits[-4:])
    if not(1<=m<=12) or y<1900:
        return None
    return pd.Timestamp(year=y,month=m,day=1)

rows=[]
for c,pbi,ipc,itcrm,tcn in _raw:
    f=parse_mmYYYY(c)
    if f is None:
        continue
    rows.append({"Fecha":f,"PBI":pbi,"IPC":ipc,"ITCRM":itcrm,"TCN":tcn})

df=pd.DataFrame(rows).sort_values("Fecha").reset_index(drop=True)

# ============================================================
# 2  Configuración Streamlit
# ============================================================
st.set_page_config(page_title="Tablero Macro 2022‑2024", layout="wide")

st.title("🌎 Tablero Interactivo de Indicadores (2022‑2024)")

# Identificación del estudiante
nombre = st.text_input("✍️ Ingresa tu nombre o correo institucional para registrar tus respuestas:")
if nombre:
    st.success(f"Respuestas registradas para: {nombre}")
else:
    st.warning("Por favor escribe tu nombre antes de continuar.")

# Tabs
modo = st.tabs(["Gráficos", "Variaciones"])

# ------------------------------------------------------------
# Pestaña 1 – Gráficos
# ------------------------------------------------------------
with modo[0]:
    indicadores=["PBI","IPC","ITCRM","TCN"]
    col1,col2=st.columns(2)
    ind1=col1.selectbox("Indicador 1",indicadores)
    ind2=col2.selectbox("Indicador 2 (opcional)", ["Ninguno"]+indicadores)
    rmin=df["Fecha"].min().to_pydatetime(); rmax=df["Fecha"].max().to_pydatetime()
    rango=st.slider("Rango de fechas", min_value=rmin, max_value=rmax, value=(rmin,rmax))
    dff=df[(df["Fecha"]>=rango[0])&(df["Fecha"]<=rango[1])]
    fig=go.Figure(); fig.add_trace(go.Scatter(x=dff["Fecha"],y=dff[ind1],name=ind1,yaxis="y1"))
    if ind2!="Ninguno":
        fig.add_trace(go.Scatter(x=dff["Fecha"],y=dff[ind2],name=ind2,yaxis="y2"))
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(dff, height=220)

    st.download_button("Descargar CSV", dff.to_csv(index=False), "indicadores_filtrados.csv", "text/csv")

    respuesta = st.text_area("💬 Tu reflexión sobre los indicadores:")
    if st.button("💾 Guardar reflexión"):
        if nombre:
            st.session_state.setdefault("respuestas", []).append((nombre, "Gráficos", respuesta))
            st.success("Respuesta guardada!")
        else:
            st.error("Debes ingresar tu nombre arriba antes de guardar.")

# ------------------------------------------------------------
# Pestaña 2 – Variaciones + Simulador
# ------------------------------------------------------------
with modo[1]:
    df_var=df.copy()
    df_var["Inflacion_%"] = df_var["IPC"].pct_change()*100
    df_var["ΔITCRM_%"]   = df_var["ITCRM"].pct_change()*100
    st.subheader("Tasas de variación")
    fig2=go.Figure()
    fig2.add_trace(go.Scatter(x=df_var["Fecha"], y=df_var["Inflacion_%"], name="Inflación %"))
    fig2.add_trace(go.Scatter(x=df_var["Fecha"], y=df_var["ΔITCRM_%"], name="Δ ITCRM %"))
    fig2.update_layout(template="plotly_white")
    st.plotly_chart(fig2,use_container_width=True)

    # Simulador simple: aplicar shocks para el último mes
    base=df_var.iloc[-1]
    d_ipc=st.slider("Shock IPC var % (último mes)", -30.0, 30.0, 0.0, 0.5)
    d_itcrm=st.slider("Shock ITCRM var % (último mes)", -30.0, 30.0, 0.0, 0.5)
    ipc_new = base["Inflacion_%"]*(1+d_ipc/100)
    it_new  = base["ΔITCRM_%"]*(1+d_itcrm/100)
    st.metric("Inflación ajustada", f"{ipc_new:.2f}%", f"{d_ipc:+.2f}%")
    st.metric("Δ ITCRM ajustado", f"{it_new:.2f}%", f"{d_itcrm:+.2f}%")

    respuesta2 = st.text_area("💬 Tu reflexión sobre las variaciones:")
    if st.button("💾 Guardar reflexión", key="var"):
        if nombre:
            st.session_state.setdefault("respuestas", []).append((nombre, "Variaciones", respuesta2))
            st.success("Respuesta guardada!")
        else:
            st.error("Debes ingresar tu nombre arriba antes de guardar.")

# ------------------------------------------------------------
# Descargar todas las respuestas
# ------------------------------------------------------------
if st.sidebar.button("⬇️ Descargar todas las respuestas"):
    rows = st.session_state.get("respuestas", [])
    if rows:
        txt="Nombre\tSeccion\tRespuesta\n"+"\n".join(f"{n}\t{s}\t{r}" for n,s,r in rows)
        st.sidebar.download_button("Descargar .txt", txt, file_name="respuestas_estudiantes.txt")
    else:
        st.sidebar.info("No hay respuestas aún.")
