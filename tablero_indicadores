# tablero_macroeconomia.py

import pandas as pd
import plotly.graph_objects as go

try:
    import streamlit as st
except ModuleNotFoundError:
    raise ModuleNotFoundError("Streamlit no está instalado en el entorno. Ejecuta 'pip install streamlit' en tu consola para instalarlo.")

# 1. Título del Tablero
st.title('🌎 Tablero Interactivo de Indicadores Macroeconómicos')

# 1.5 Guía de uso del Tablero
st.markdown("""
## 🧭 Guía de Uso del Tablero

Bienvenidos/as al tablero interactivo de Macroeconomía Básica. Aquí podrán analizar la evolución de variables claves de la economía argentina.

### ¿Cómo utilizar el tablero?
- **Seleccione uno o dos indicadores** económicos a analizar.
- **Defina el rango de fechas** que desea observar utilizando el control deslizante.
- **Observe los gráficos interactivos**, pasando el mouse sobre los puntos para ver los valores exactos.
- **Descargue los datos** si desea trabajarlos offline.
- **Responda las preguntas** propuestas al pie del tablero para reflexionar sobre los resultados.

---

### Recordatorio de Definiciones:
- **PBI:** Valor monetario de los bienes y servicios de demanda final producidos en una economía en un período determinado (generalmente un año).
- **Inflación:** Aumento sostenido en el tiempo del Nivel General de Precios.
- **Desempleo:** Porcentaje de personas que forman la Población Económicamente Activa que no tienen trabajo y lo buscan activamente.
- **Tipo de cambio:** Cantidad de unidades de moneda nacional que debo entregar por una unidad de moneda extranjera.

---
""")

# 2. Definiciones teóricas
st.markdown("""
## 📖 Definiciones Clave
- **Producto Bruto Interno (PBI):** Valor monetario de los bienes y servicios de demanda final producidos en una economía en un período de tiempo determinado, generalmente un año.
- **Inflación:** Aumento sostenido en el tiempo del Nivel General de Precios.
- **Desempleo:** Porcentaje de personas que forman la Población Económicamente Activa que no tienen trabajo y lo buscan activamente.
- **Tipo de cambio:** Cantidad de unidades de moneda nacional que debo entregar por una unidad de moneda extranjera.
---
""")

# 3. Cargar datos simulados basados en datos reales
fechas = pd.date_range(start='2022-01-01', end='2025-01-01', freq='MS')
pbi_real = [130, 132, 131, 134, 136, 137, 138, 137, 136, 137, 138, 137,
             137, 138, 140, 141, 141, 140, 139, 138, 139, 140, 140, 139, 140,
             141, 142, 143, 144, 145, 145, 146, 147, 148, 149, 150]
inflacion_mensual = [3.9, 4.7, 6.7, 6.0, 5.1, 5.3, 7.4, 7.0, 6.2, 6.3, 5.1, 5.1,
                     6.0, 6.6, 7.7, 7.8, 6.3, 6.0, 12.4, 8.3, 12.8, 20.6, 25.5, 20.6, 15.0,
                     10.0, 9.5, 8.0, 7.5, 7.0, 6.8, 6.5, 6.2, 6.0, 5.8, 5.5]
desempleo = [7.0, 7.0, 6.9, 6.9, 6.9, 6.8, 6.8, 6.7, 6.7, 6.8, 6.8, 7.1,
             7.0, 7.0, 6.8, 6.8, 6.7, 6.9, 7.5, 7.8, 8.0, 8.1, 8.5, 8.3, 8.0,
             7.8, 7.5, 7.3, 7.0, 6.8, 6.5, 6.3, 6.2, 6.1, 6.0, 5.9]
tipo_cambio = [104, 107, 110, 112, 117, 120, 130, 135, 140, 150, 160, 170,
               180, 190, 210, 220, 230, 250, 310, 350, 400, 500, 600, 700, 750,
               760, 770, 780, 790, 800, 810, 820, 830, 840, 850, 860]

df_indicadores = pd.DataFrame({
    'Fecha': fechas,
    'PBI_Indexado': pbi_real,
    'Inflacion_Mensual_%': inflacion_mensual,
    'Desempleo_%': desempleo,
    'Tipo_Cambio_AR_USD': tipo_cambio
})

# 4. Consignas
st.markdown("""
### 📚 Consignas:
- Elija uno o dos indicadores económicos para analizar.
- Seleccione el rango de fechas de interés.
- Analice las variaciones y relaciones entre los indicadores.
- Responda las preguntas al pie del tablero.
""")

# 5. Selección de indicadores
disponibles = df_indicadores.columns[1:]
indicador1 = st.selectbox('Seleccione el primer indicador:', disponibles)
indicador2 = st.selectbox('Seleccione el segundo indicador para comparar (opcional):', ['Ninguno'] + list(disponibles))

# 6. Rango de fechas
rango_fechas = st.slider(
    'Seleccione el período:',
    min_value=df_indicadores['Fecha'].min().to_pydatetime(),
    max_value=df_indicadores['Fecha'].max().to_pydatetime(),
    value=(df_indicadores['Fecha'].min().to_pydatetime(), df_indicadores['Fecha'].max().to_pydatetime())
)

# 7. Filtrado
df_filtrado = df_indicadores[
    (df_indicadores['Fecha'] >= pd.to_datetime(rango_fechas[0])) &
    (df_indicadores['Fecha'] <= pd.to_datetime(rango_fechas[1]))
]

# 8. Gráfico interactivo
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_filtrado['Fecha'], y=df_filtrado[indicador1],
                         name=indicador1, yaxis='y1'))

if indicador2 != 'Ninguno':
    fig.add_trace(go.Scatter(x=df_filtrado['Fecha'], y=df_filtrado[indicador2],
                             name=indicador2, yaxis='y2'))

fig.update_layout(
    title=f'Evolución de {indicador1}' + (f' y {indicador2}' if indicador2 != 'Ninguno' else ''),
    xaxis_title='Fecha',
    yaxis=dict(title=indicador1),
    yaxis2=dict(title=indicador2, overlaying='y', side='right') if indicador2 != 'Ninguno' else None,
    legend=dict(x=0.01, y=0.99),
    template='plotly_white'
)

st.plotly_chart(fig)

# 9. Mostrar tabla
st.dataframe(df_filtrado)

# 10. Botón para descargar
st.download_button(
    label='📅 Descargar datos filtrados en CSV',
    data=df_filtrado.to_csv(index=False),
    file_name='datos_macroeconomicos_filtrados.csv',
    mime='text/csv'
)

# 11. Preguntas para la reflexión
st.markdown("""
---
### ✏️ Preguntas para responder:
1. ¿Qué patrones observás en la evolución de los indicadores seleccionados?
2. ¿Se observan relaciones entre los dos indicadores?
3. ¿Qué conclusiones se pueden extraer respecto al impacto del tipo de cambio sobre la inflación?
4. ¿Cómo evolucionó el desempleo frente a los cambios en el PBI?
5. ¿Qué eventos económicos podrían explicar los cambios observados?
---
""")
