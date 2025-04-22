
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

# Préstamo y flujo real
monto_prestamo = inversion_total * porcentaje_prestamo / 100
intereses_totales = monto_prestamo * interes_prestamo / 100 * plazo_anios
capital_propio = inversion_total - monto_prestamo
devolucion_prestamo = monto_prestamo

# Flujo de caja neto (después de intereses y devolución)
flujo_neto = [-capital_propio]
for _ in range(plazo_anios - 1):
    flujo_neto.append(0)
flujo_neto.append(precio_venta - comision_venta_eur - intereses_totales - devolucion_prestamo)

ganancia_neta = flujo_neto[-1]
roi = (ganancia_neta / capital_propio) * 100 if capital_propio > 0 else 0
tir = irr(flujo_neto) * 100 if flujo_neto[-1] > 0 else 0

precio_venta_sugerido = (capital_propio * 1.2) + comision_venta_eur + intereses_totales + devolucion_prestamo

st.metric("💰 ROI real (con préstamo + devolución)", f"{roi:.2f}%")
st.metric("📈 TIR real (con préstamo)", f"{tir:.2f}%")
st.metric("💡 Precio sugerido con 20% ROI", f"{precio_venta_sugerido:,.0f} €")

