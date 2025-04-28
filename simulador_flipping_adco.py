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
st.title("🏨 Simulador de Flipping Inmobiliario – Versión Avanzada")
st.caption("Desarrollado por ADCO Investments – andres@adco.es")

st.header("📥 Datos del Proyecto")

# --- INPUTS ---
with st.expander("🌇️ Detalles del Proyecto"):
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
    porcentaje_prestamo = st.number_input("Préstamo bancario (% del total de inversión)", value=60.0)
    interes_prestamo = st.number_input("Interés del préstamo (%)", value=4.0)
    plazo_prestamo = st.number_input("Plazo del préstamo (años)", value=2)

# --- FILTRO DE COMPARABLES ---
st.header("🗂️ Filtro de comparables por €/m²")

# Simulamos carga de comparables
df_filtrado = pd.DataFrame({
    "Precio_m2": np.random.randint(4000, 15000, 100),
    "Ascensor": random.choices(["Sí", "No", "Desconocido"], k=100),
    "Estado": random.choices(["Reformado", "Para Reformar", "Desconocido"], k=100),
    "Planta": random.choices(["Bajo", "1ª", "2ª", "Ático", "Desconocido"], k=100)
})

# Rango de precios
precio_min = int(df_filtrado["Precio_m2"].min())
precio_max = int(df_filtrado["Precio_m2"].max())

rango_precio = st.slider("Selecciona el rango €/m²", min_value=precio_min, max_value=precio_max, value=(precio_min, precio_max))

# Filtros con multiselect
ascensor_op = st.multiselect("Ascensor", options=df_filtrado["Ascensor"].unique(), default=["Desconocido"])
estado_op = st.multiselect("Estado del piso", options=df_filtrado["Estado"].unique(), default=["Desconocido"])
planta_op = st.multiselect("Planta", options=df_filtrado["Planta"].unique(), default=["Desconocido"])

# Aplicar filtros
filtrado = df_filtrado.copy()

filtrado = filtrado[(filtrado["Precio_m2"] >= rango_precio[0]) & (filtrado["Precio_m2"] <= rango_precio[1])]

if "Desconocido" not in ascensor_op:
    filtrado = filtrado[filtrado["Ascensor"].isin(ascensor_op)]

if "Desconocido" not in estado_op:
    filtrado = filtrado[filtrado["Estado"].isin(estado_op)]

if "Desconocido" not in planta_op:
    filtrado = filtrado[filtrado["Planta"].isin(planta_op)]

st.write(f"🔍 Se muestran {len(filtrado)} propiedades dentro del rango y filtros aplicados.")

# Mostrar tabla
st.dataframe(filtrado)
