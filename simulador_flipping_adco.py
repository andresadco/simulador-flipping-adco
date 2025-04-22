import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from numpy_financial import irr

st.set_page_config(page_title="Simulador Pro ADCO", layout="centered")
st.title("🏘️ Simulador de Flipping Inmobiliario – Versión Avanzada")
st.caption("Desarrollado por ADCO Investments – andres@adco.es")

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
usa_deuda = st.radio("¿Vas a usar financiamiento?", ["No", "Sí"])

if usa_deuda == "Sí":
    st.subheader("🏦 Detalles del Préstamo")
    porcentaje_prestamo = st.number_input("Préstamo bancario (% del total de inversión)", value=70.0)
    interes_prestamo = st.number_input("Interés anual (%)", value=4.0)
    plazo_anios = st.number_input("Plazo del préstamo (años)", value=1)
else:
    porcentaje_prestamo = 0.0
    interes_prestamo = 0.0
    plazo_anios = 1

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

# Préstamo y flujo real
monto_prestamo = inversion_total * porcentaje_prestamo / 100
intereses_totales = monto_prestamo * interes_prestamo / 100 * plazo_anios
capital_propio = inversion_total - monto_prestamo
devolucion_prestamo = monto_prestamo

# Flujo de caja
flujo_neto = [-capital_propio]
for _ in range(plazo_anios - 1):
    flujo_neto.append(0)
flujo_neto.append(precio_venta - comision_venta_eur - intereses_totales - devolucion_prestamo)

ganancia_neta = flujo_neto[-1]
roi = (ganancia_neta / capital_propio) * 100 if capital_propio > 0 else 0
tir = irr(flujo_neto) * 100 if flujo_neto[-1] > 0 else 0

precio_venta_sugerido = (capital_propio * 1.2) + comision_venta_eur + intereses_totales + devolucion_prestamo

st.metric("💰 ROI real", f"{roi:.2f}%")
st.metric("📈 TIR real", f"{tir:.2f}%")
st.metric("💡 Precio sugerido con 20% ROI", f"{precio_venta_sugerido:,.0f} €")

# --- GRÁFICO BARRAS ---
st.subheader("📊 Comparación de Costes vs Ganancia")
fig, ax = plt.subplots()
ax.bar(["Capital Propio", "Ganancia Neta"], [capital_propio, ganancia_neta], color=["gray", "green"])
st.pyplot(fig)

# --- RESUMEN EJECUTIVO ---
st.subheader("📋 Resumen Ejecutivo de la Inversión")

resumen_data = {
    "Concepto": [
        "Precio de compra",
        "Comisión de compra",
        "Gastos legales",
        "Gastos administrativos",
        "ITP / IVA de compra",
        "IBI",
        "Coste de reforma (con IVA)",
        "💰 Inversión total",
        "🏦 Préstamo solicitado",
        "💸 Intereses del préstamo",
        "💼 Capital propio invertido",
        "📈 Precio de venta",
        "Comisión de venta",
        "Ganancia neta esperada",
        "ROI real (%)",
        "TIR real (%)"
    ],
    "Valor estimado (€)": [
        f"{precio_compra:,.0f}",
        f"{precio_compra * comision_compra / 100:,.0f}",
        f"{gastos_legales:,.0f}",
        f"{gastos_administrativos:,.0f}",
        f"{precio_compra * itp / 100:,.0f}",
        f"{ibi:,.0f}",
        f"{coste_reforma_iva:,.0f}",
        f"{inversion_total:,.0f}",
        f"{monto_prestamo:,.0f}",
        f"{intereses_totales:,.0f}",
        f"{capital_propio:,.0f}",
        f"{precio_venta:,.0f}",
        f"{comision_venta_eur:,.0f}",
        f"{ganancia_neta:,.0f}",
        f"{roi:.2f}",
        f"{tir:.2f}"
    ]
}

df_resumen = pd.DataFrame(resumen_data)
st.dataframe(df_resumen, hide_index=True)

# --- COMPARABLES ---
csv_path = f"comparables_{zona.lower()}.csv"
if os.path.exists(csv_path):
    st.subheader(f"🏘️ Comparables en {zona}")
    df_comp = pd.read_csv(csv_path)
    df_comp["Link"] = df_comp["Link"].apply(lambda x: f"<a href='{x}' target='_blank'>Ver anuncio</a>")
    st.write(df_comp.to_html(index=False, escape=False), unsafe_allow_html=True)
else:
    st.warning(f"No hay comparables para {zona}. Haz scraping o súbelos.")


