
# ADCO - Simulador de Flipping Inmobiliario Profesional
# Incluye: ROI + TIR + sensibilidad + scraping comparables + PDF export

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Simulador Pro ADCO", layout="centered")
st.title("🏘️ Simulador de Flipping Inmobiliario – Versión Avanzada")
st.caption("Desarrollado por ADCO Investments – andres@adco.es")

# Logo
st.image("ADCO_LOGO_SIMPLE.png", width=150)

st.header("📥 Datos del Proyecto")

# --- INPUTS ---
with st.expander("🏗️ Detalles del Proyecto"):
    col1, col2 = st.columns(2)

    with col1:
        superficie = st.number_input("Superficie total (m²)", value=80)
        superficie_reforma = st.number_input("Superficie a reformar (m²)", value=60)
        coste_reforma_m2 = st.number_input("Coste por m² de reforma (€)", value=1400)
        costes_adicionales = st.number_input("Costes adicionales de reforma (€)", value=5000)
        iva_reforma = st.number_input("IVA en reforma (%)", value=10.0)
        zona = st.selectbox("Zona del piso", ["Chamberí", "Salamanca", "Retiro"])

    with col2:
        precio_compra = st.number_input("Precio de compra (€)", value=850000)
        comision_compra = st.number_input("Comisión de compra (%)", value=2.0)
        gastos_legales = st.number_input("Gastos legales (€)", value=3000)
        gastos_administrativos = st.number_input("Gastos administrativos (€)", value=3000)
        itp = st.number_input("ITP o IVA de compra (%)", value=6.0)
        ibi = st.number_input("IBI (€)", value=500)

# Venta
st.subheader("💰 Precio de Venta y Comisión")
precio_venta = st.number_input("Precio de venta esperado (€)", value=1350000)
comision_venta = st.number_input("Comisión de venta (%)", value=3.0)

# Financiamiento
st.subheader("🏦 Financiación")
porcentaje_prestamo = st.number_input("Préstamo bancario (% del precio de compra)", value=70.0)
interes_prestamo = st.number_input("Interés anual (%)", value=4.0)
plazo_anios = st.number_input("Plazo del préstamo (años)", value=1)

# --- CÁLCULOS ---
st.header("📊 Análisis Financiero")

coste_reforma = superficie_reforma * coste_reforma_m2 + costes_adicionales
coste_reforma_iva = coste_reforma * (1 + iva_reforma / 100)
gastos_total_compra = (
    precio_compra * (1 + comision_compra / 100) +
    precio_compra * (itp / 100) +
    gastos_legales + gastos_administrativos + ibi
)
inversion_total = gastos_total_compra + coste_reforma_iva
comision_venta_eur = precio_venta * comision_venta / 100
ganancia_neta = precio_venta - comision_venta_eur - inversion_total

roi = ganancia_neta / inversion_total * 100

# TIR (aproximada solo con flujo neto)
flujo_neto = [ -inversion_total ] + [ precio_venta - comision_venta_eur ]
tir = np.irr(flujo_neto) * 100 if flujo_neto[1] > 0 else 0

st.metric("ROI total", f"{roi:.2f}%")
st.metric("TIR estimada", f"{tir:.2f}%")


# --- ANÁLISIS DE SENSIBILIDAD ---
st.subheader("📈 Análisis de Sensibilidad")

variaciones_precio = [-0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15]
variaciones_reforma = [-0.1, -0.05, 0, 0.05, 0.1]

resultados = []
for vp in variaciones_precio:
    for vr in variaciones_reforma:
        nuevo_precio_venta = precio_venta * (1 + vp)
        nuevo_coste_reforma = coste_reforma * (1 + vr)
        nuevo_total = gastos_total_compra + nuevo_coste_reforma * (1 + iva_reforma / 100)
        nuevo_ganancia = nuevo_precio_venta - nuevo_precio_venta * comision_venta / 100 - nuevo_total
        nuevo_roi = nuevo_ganancia / nuevo_total * 100
        flujo = [ -nuevo_total, nuevo_precio_venta - nuevo_precio_venta * comision_venta / 100 ]
        nuevo_tir = np.irr(flujo) * 100 if flujo[1] > 0 else 0
        resultados.append([f"{int(vp*100)}%", f"{int(vr*100)}%", round(nuevo_roi, 2), round(nuevo_tir, 2)])

df_sens = pd.DataFrame(resultados, columns=["ΔPrecio Venta", "ΔCoste Reforma", "ROI (%)", "TIR (%)"])
st.dataframe(df_sens)

# --- GRÁFICO BARRAS ---
st.subheader("📊 Comparación de Costes vs Ganancia")
fig, ax = plt.subplots()
ax.bar(["Inversión Total", "Ganancia Neta"], [inversion_total, ganancia_neta], color=["gray", "green"])
st.pyplot(fig)

# --- COMPARABLES (CSV dinámico) ---
csv_path = f"comparables_{zona.lower()}.csv"
if os.path.exists(csv_path):
    st.subheader(f"🏘️ Comparables en {zona}")
    df_comp = pd.read_csv(csv_path)
    df_comp["Link"] = df_comp["Link"].apply(lambda x: f"<a href='{x}' target='_blank'>Ver anuncio</a>")
    st.write(df_comp.to_html(index=False, escape=False), unsafe_allow_html=True)
else:
    st.warning(f"No hay comparables para {zona}. Haz scraping o súbelos.")

# Aquí irá el botón de exportación a PDF en versión final



