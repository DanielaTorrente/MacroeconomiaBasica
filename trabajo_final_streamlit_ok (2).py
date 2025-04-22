
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# === Encabezado ===
st.title("📘 Trabajo Final – Curso de Posgrado")
st.markdown("""
**Curso:** Incorporando Python e Inteligencia Artificial en Nuestras Cátedras  
**Cátedra:** Macroeconomía Básica  
**Carreras:** Contador Público, Lic. en Economía, Lic. en Administración  
**Facultad:** Ciencias Económicas – UNNE  
**Docentes:** Prof. Daniela Torrente y Prof. Omar Quirelli
""")
st.markdown("---")

# === Objetivos ===
st.header("🎯 Objetivos de la actividad")
st.markdown("""
- Aplicar el modelo keynesiano de ingreso-gasto en un entorno computacional.  
- Simular el ingreso de equilibrio ante diferentes políticas fiscales.  
- Comprender el rol del multiplicador en el análisis macroeconómico.  
- Introducir el uso de Python como herramienta de análisis económico.
""")

# === Teoría ===
st.header("📚 Introducción teórica: el modelo keynesiano simple")
st.markdown("""
El modelo keynesiano de ingreso-gasto analiza cómo se determina el ingreso de equilibrio en una economía cerrada.

### Supuestos:
- Economía cerrada
- Precios constantes
- Solo mercado de bienes
- Oferta guiada por demanda
- I y G son exógenos

### Ecuaciones del modelo:
- Demanda agregada: \( DA = C + I + G \)  
- Consumo: \( C = C_0 + c(Y - T) \)  
- Equilibrio: \( Y = C_0 + c(Y - T) + I + G \)  
- Resolviendo: \( Y = \frac{1}{1 - c}(C_0 - cT + I + G) \)

El término \( \frac{1}{1-c} \) es el **multiplicador keynesiano**.
""")

# === Cuadro resumen ===
st.subheader("📌 Cuadro resumen del modelo keynesiano simple")
st.latex(r'''
\begin{array}{ll}
\text{Consumo autónomo} & C_0 \\
\text{PMC} & c \\
\text{Ingreso total} & Y \\
\text{Impuestos} & T \\
\text{Inversión autónoma} & I \\
\text{Gasto público} & G \\
\text{Demanda agregada} & DA = C + I + G \\
\text{Función de consumo} & C = C_0 + c(Y - T) \\
\text{Ingreso de equilibrio} & Y = \frac{1}{1 - c}(C_0 - cT + I + G)
\end{array}
''')

# === Primer simulador ===
st.header("🔧 Simulador 1: Modelo Keynesiano Simple")

st.sidebar.subheader("Parámetros – Simulador 1")
C0 = st.sidebar.slider("C₀ (consumo autónomo)", 0, 300, 100, 10)
c = st.sidebar.slider("c (PMC)", 0.1, 0.99, 0.8, 0.01)
I = st.sidebar.slider("I (inversión)", 0, 300, 50, 10)
G = st.sidebar.slider("G (gasto público)", 0, 300, 100, 10)

Y_eq_1 = 1 / (1 - c) * (C0 + I + G)
DA_1 = lambda Y: C0 + c * Y + I + G
Y_vals = np.linspace(0, 1500, 300)

fig1, ax1 = plt.subplots()
ax1.plot(Y_vals, Y_vals, "--", color="gray", label="45°")
ax1.plot(Y_vals, DA_1(Y_vals), label="DA", color="blue")
ax1.plot(Y_eq_1, DA_1(Y_eq_1), "ro", label=f"Equilibrio Y* = {Y_eq_1:.2f}")
ax1.set_xlabel("Ingreso (Y)")
ax1.set_ylabel("Demanda Agregada (DA)")
ax1.legend()
ax1.grid(True)
st.pyplot(fig1)

st.markdown(f"**Ingreso de equilibrio:** {Y_eq_1:.2f}<br>**Multiplicador:** {1 / (1 - c):.2f}", unsafe_allow_html=True)

# === Segundo simulador ===
st.header("🔧 Simulador 2: Modelo Keynesiano con impuestos proporcionales")

st.sidebar.subheader("Parámetros – Simulador 2")
t = st.sidebar.slider("t (tasa impositiva)", 0.0, 0.5, 0.15, 0.01)

mult_2 = 1 / (1 - c * (1 - t))
Y_eq_2 = mult_2 * (C0 + I + G)
DA_2 = lambda Y: C0 + c * (1 - t) * Y + I + G

fig2, ax2 = plt.subplots()
ax2.plot(Y_vals, Y_vals, "--", color="gray", label="45°")
ax2.plot(Y_vals, DA_2(Y_vals), label="DA con impuestos", color="green")
ax2.plot(Y_eq_2, DA_2(Y_eq_2), "ro", label=f"Equilibrio Y* = {Y_eq_2:.2f}")
ax2.set_xlabel("Ingreso (Y)")
ax2.set_ylabel("Demanda Agregada (DA)")
ax2.legend()
ax2.grid(True)
st.pyplot(fig2)

st.markdown(f"**Ingreso de equilibrio con impuestos:** {Y_eq_2:.2f}<br>**Multiplicador ajustado:** {mult_2:.2f}", unsafe_allow_html=True)

# === Consigna ===
st.header("📝 Consigna Final para Estudiantes")
st.markdown("""
Explorá los efectos de los distintos parámetros sobre el ingreso de equilibrio.  
- ¿Qué ocurre cuando aumenta el gasto público?  
- ¿Cómo cambia el equilibrio cuando sube la tasa impositiva?  
- ¿Qué combinación de parámetros genera mayor efecto multiplicador?

**Registrá tus observaciones y prepárate para compartirlas en clase.**
""")
