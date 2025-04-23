import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from numpy_financial import irr
import requests
import random
import time
from bs4 import BeautifulSoup

st.set_page_config(page_title="Comparador por Subzona – ADCO", layout="centered")
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

monto_prestamo = inversion_total * porcentaje_prestamo / 100
intereses_totales = monto_prestamo * interes_prestamo / 100 * plazo_anios
capital_propio = inversion_total - monto_prestamo
devolucion_prestamo = monto_prestamo

flujo_neto = [-capital_propio] + [0] * (plazo_anios - 1) + [
    precio_venta - comision_venta_eur - intereses_totales - devolucion_prestamo
]
ganancia_neta = flujo_neto[-1] - capital_propio
roi = (ganancia_neta / capital_propio) * 100 if capital_propio > 0 else 0
tir = irr(flujo_neto) * 100 if flujo_neto[-1] > 0 else 0

precio_venta_sugerido = capital_propio * 1.2 + comision_venta_eur + intereses_totales + devolucion_prestamo

st.metric("💰 ROI real", f"{roi:.2f}%")
st.metric("📈 TIR real", f"{tir:.2f}%")
st.metric("💡 Precio sugerido con 20% ROI", f"{precio_venta_sugerido:,.0f} €")

fig, ax = plt.subplots()
ax.bar(["Capital Propio", "Ganancia Neta"], [capital_propio, ganancia_neta], color=["gray", "green"])
st.pyplot(fig)

# --- RESUMEN EJECUTIVO ---
st.subheader("📋 Resumen Ejecutivo de la Inversión")

if roi < 10:
    interpretacion = "⚠️ Rentabilidad baja"
elif 10 <= roi <= 20:
    interpretacion = "✅ Rentabilidad aceptable"
else:
    interpretacion = "🚀 Rentabilidad excelente"

frase_inversion = (
    f"💬 Este proyecto proyecta una rentabilidad del **{roi:.2f}%** y una TIR del **{tir:.2f}%**. "
    f"Requiere un capital propio estimado de **{capital_propio:,.0f} €** con un préstamo de "
    f"**{monto_prestamo:,.0f} €**. {interpretacion} para inversiones de corto plazo en Madrid."
)

resumen_data = {
    "Concepto": [...],
    "Valor estimado (€)": [...]
}

# (Por simplicidad omitimos el contenido literal del resumen_data en esta respuesta)

st.dataframe(pd.DataFrame(resumen_data), hide_index=True)
st.markdown(frase_inversion)

# --- ESCENARIOS DE PRECIO DE VENTA ---
st.subheader("🎯 Escenarios: ¿Qué pasa si vendes por más o menos?")

delta_precio = st.slider("Variación en el precio de venta (%)", -20, 20, (-10, 10), step=5)

escenarios_resultados = []
for variacion in range(delta_precio[0], delta_precio[1] + 1, 5):
    ...

st.table(pd.DataFrame(escenarios_resultados))

# --- Comparador por Subzona ---
...

if st.button("🔍 Obtener comparables de la subzona"):
    ...
    st.session_state["df_subzona"] = df

if "df_subzona" in st.session_state:
    df_subzona = st.session_state["df_subzona"]
    st.subheader("📊 Análisis de Comparables")

    try:
        df_subzona["€/m²"] = (
            df_subzona["€/m²"].astype(str)
            .str.replace(",", "", regex=False)
            .str.extract(r"(\d+\.?\d*)")[0]
            .astype(float)
        )

        df_subzona["Superficie (m²)"] = (
            df_subzona["Superficie (m²)"]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .str.extract(r"(\d+\.?\d*)")[0]
            .astype(float)
        )

        promedio = df_subzona["€/m²"].mean()
        minimo = df_subzona["€/m²"].min()
        maximo = df_subzona["€/m²"].max()

        st.metric("📍 Promedio €/m²", f"{promedio:,.0f} €")
        st.metric("📉 Mínimo €/m²", f"{minimo:,.0f} €")
        st.metric("📈 Máximo €/m²", f"{maximo:,.0f} €")

        st.subheader("🎛️ Filtro de comparables por €/m²")
        rango = st.slider(
            "Selecciona el rango €/m²",
            min_value=int(minimo),
            max_value=int(maximo),
            value=(int(minimo), int(maximo)),
            key="slider_comparables"
        )

        df_filtrado = df_subzona[(df_subzona["€/m²"] >= rango[0]) & (df_subzona["€/m²"] <= rango[1])].copy()
        df_filtrado["Link"] = df_filtrado["Link"].apply(lambda x: f"[Ver anuncio]({x})")

        st.write(f"🔎 Se muestran {len(df_filtrado)} propiedades dentro del rango seleccionado.")
        st.write(df_filtrado.to_markdown(index=False), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error procesando comparables: {e}")

