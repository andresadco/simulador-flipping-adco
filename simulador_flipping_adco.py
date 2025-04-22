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

#  Costo de Venta
precio_venta = st.number_input("Precio de venta esperado (€)", value=1350000)
st.subheader("💰Comisión")

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

# Capital propio invertido
capital_propio = inversion_total * (1 - porcentaje_prestamo / 100)

# Costo de préstamo
monto_prestamo = inversion_total * porcentaje_prestamo / 100
intereses_totales = monto_prestamo * interes_prestamo / 100 * plazo_anios

# Flujo de caja neto para el inversionista (después de intereses)
flujo_neto = [-capital_propio, precio_venta - comision_venta_eur - intereses_totales]

# ROI y TIR con préstamo
ganancia_neta = flujo_neto[1]
roi = ganancia_neta / capital_propio * 100 if capital_propio > 0 else 0
tir = irr(flujo_neto) * 100 if flujo_neto[1] > 0 else 0

# Precio sugerido para ROI 20%
precio_venta_sugerido = (capital_propio * 1.2) + comision_venta_eur + intereses_totales

st.metric("💰 ROI real (con préstamo)", f"{roi:.2f}%")
st.metric("📈 TIR real", f"{tir:.2f}%")
st.metric("💡 Precio sugerido con 20% ROI", f"{precio_venta_sugerido:,.0f} €")

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
        nuevo_capital = nuevo_total * (1 - porcentaje_prestamo / 100)
        nuevo_intereses = nuevo_total * (porcentaje_prestamo / 100) * interes_prestamo / 100 * plazo_anios
        nuevo_ingreso = nuevo_precio_venta - nuevo_precio_venta * comision_venta / 100 - nuevo_intereses
        nuevo_ganancia = nuevo_ingreso - nuevo_capital
        nuevo_roi = nuevo_ganancia / nuevo_capital * 100 if nuevo_capital > 0 else 0
        flujo = [-nuevo_capital, nuevo_ingreso]
        nuevo_tir = irr(flujo) * 100 if flujo[1] > 0 else 0
        resultados.append([f"{int(vp*100)}%", f"{int(vr*100)}%", round(nuevo_roi, 2), round(nuevo_tir, 2)])

df_sens = pd.DataFrame(resultados, columns=["ΔPrecio Venta", "ΔCoste Reforma", "ROI (%)", "TIR (%)"])
st.dataframe(df_sens)

# --- GRÁFICO BARRAS ---
st.subheader("📊 Comparación de Costes vs Ganancia")
fig, ax = plt.subplots()
ax.bar(["Capital Propio", "Ganancia Neta"], [capital_propio, ganancia_neta], color=["gray", "green"])
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


# RESUMEN EJECUTIVO
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





