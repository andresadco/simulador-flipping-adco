import streamlit as st
import numpy as np
import pandas as pd
from fpdf import FPDF
from io import BytesIO
import base64

st.set_page_config(page_title="Simulador Flipping - ADCO", layout="centered")

st.title("Simulador de Flipping Inmobiliario")
st.markdown("Versión Pro creada por **ADCO Investments**")

# --- INTELIGENCIA DE MERCADO (simulada) ---
zonas_m30 = [
    "Chamberí", "Salamanca", "Retiro", "Centro", 
    "Chamartín", "Arganzuela", "Tetuán", 
    "Usera Norte", "Moncloa-Aravaca", "Latina Norte", "Carabanchel Norte"
]

zona_seleccionada = st.selectbox("Zona del proyecto (M-30)", zonas_m30)

precios_m2 = {
    "Chamberí": 5280, "Salamanca": 6830, "Retiro": 4950, "Centro": 4780,
    "Chamartín": 5600, "Arganzuela": 4260, "Tetuán": 4170, "Usera Norte": 2900,
    "Moncloa-Aravaca": 5000, "Latina Norte": 3400, "Carabanchel Norte": 3100
}

comparables = {
    "Chamberí": [
        {"Dirección": "C/ Eloy Gonzalo", "Superficie": 83, "Precio": 460000, "Estado": "Reformado"},
        {"Dirección": "C/ Galileo", "Superficie": 76, "Precio": 395000, "Estado": "A reformar"},
        {"Dirección": "C/ Trafalgar", "Superficie": 90, "Precio": 495000, "Estado": "Reformado"},
    ],
    "Salamanca": [
        {"Dirección": "C/ Claudio Coello", "Superficie": 80, "Precio": 630000, "Estado": "Reformado"},
        {"Dirección": "C/ Goya", "Superficie": 70, "Precio": 520000, "Estado": "Reformado"},
        {"Dirección": "C/ Príncipe de Vergara", "Superficie": 85, "Precio": 690000, "Estado": "A reformar"},
    ],
    "Centro": [
        {"Dirección": "C/ Atocha", "Superficie": 65, "Precio": 370000, "Estado": "Reformado"},
        {"Dirección": "C/ Huertas", "Superficie": 55, "Precio": 295000, "Estado": "Reformado"},
        {"Dirección": "C/ Embajadores", "Superficie": 78, "Precio": 410000, "Estado": "A reformar"},
    ]
}

# INPUTS
st.header("Datos del Proyecto")

# Compra
st.subheader("Compra del Inmueble")
superficie = st.number_input("Superficie del piso (m²)", value=80)
precio_compra = st.number_input("Precio de compra propuesto (€)", value=200000)
comision_compra_pct = st.number_input("Comisión de compra (%)", value=2.0)
gastos_legales = st.number_input("Gastos legales (€)", value=1000)
gastos_admin = st.number_input("Gastos administrativos (€)", value=800)
itp = st.number_input("Impuesto de compra (ITP o IVA) (%)", value=7.0)
ibi = st.number_input("IBI (€)", value=300)
tasacion = st.number_input("Tasación (€)", value=400)
registro = st.number_input("Registro de la propiedad (€)", value=600)

# Reforma
st.subheader("Reforma del Inmueble")
superficie_reformar = st.number_input("Superficie a reformar (m²)", value=70)
coste_m2_reforma = st.number_input("Coste por m² de reforma (€)", value=600)
costes_adicionales = st.number_input("Costes adicionales de reforma (€)", value=5000)
iva_reforma = st.number_input("IVA en reformas (%)", value=10.0)

# Financiamiento
st.subheader("Financiamiento")
porcentaje_prestamo = st.number_input("Monto del préstamo (% sobre compra)", value=70.0)
interes = st.slider("Tasa de interés (%)", 0.0, 10.0, 4.0)
plazo = st.number_input("Plazo del préstamo (años)", value=1)

# Escenarios
st.subheader("Escenarios")
variacion_precio_venta = st.slider("Variación del precio de venta (%)", -15, 15, 0)

# CÁLCULOS
coste_obra = superficie_reformar * coste_m2_reforma
iva_obra = coste_obra * iva_reforma / 100
reforma_total = coste_obra + costes_adicionales + iva_obra

comision_compra = precio_compra * comision_compra_pct / 100
impuesto_compra = precio_compra * itp / 100

inversion_total = (
    precio_compra + comision_compra + gastos_legales + gastos_admin +
    impuesto_compra + ibi + tasacion + registro + reforma_total
)

# Calcular precio de venta mínimo para 20% ROI
precio_venta_objetivo = inversion_total * 1.2

# Simular precio ajustado por escenario
precio_venta_final = precio_venta_objetivo * (1 + variacion_precio_venta / 100)
comision_venta_pct = 3.0
comision_venta = precio_venta_final * comision_venta_pct / 100

prestamo = precio_compra * porcentaje_prestamo / 100
intereses = prestamo * (interes / 100) * plazo
gastos_totales = inversion_total + intereses + comision_venta

ganancia_neta = precio_venta_final - gastos_totales
roi_total = (ganancia_neta / inversion_total) * 100 if inversion_total > 0 else 0
tir = (ganancia_neta / inversion_total + 1) ** (1 / plazo) - 1 if inversion_total > 0 else 0
precio_m2 = precio_venta_final / superficie if superficie > 0 else 0

# RESULTADOS
st.markdown("---")
st.header("Resultados del Análisis")

st.markdown(f"✅ Precio mínimo objetivo para 20% ROI: €{precio_venta_objetivo:,.2f}")
st.markdown(f"📈 Precio de venta final con escenario: €{precio_venta_final:,.2f}")
st.markdown(f"💶 Precio de venta por m²: €{precio_m2:,.2f}/m²")
st.markdown(f"🏗️ Coste total de reforma (con IVA): €{reforma_total:,.2f}")
st.markdown(f"💼 Inversión total (sin intereses): €{inversion_total:,.2f}")
st.markdown(f"📉 Gastos totales (con intereses + venta): €{gastos_totales:,.2f}")
st.markdown(f"💰 Ganancia neta del proyecto: €{ganancia_neta:,.2f}")
st.markdown(f"📊 ROI total: {roi_total:.2f} %")
st.markdown(f"📆 Rentabilidad anualizada (TIR): {tir * 100:.2f} %")

# Análisis de mercado
st.markdown("---")
st.subheader("📍 Inteligencia de Mercado (M-30)")

precio_zona = precios_m2.get(zona_seleccionada)
st.markdown(f"**Precio medio por m² en {zona_seleccionada}:** €{precio_zona:,.2f}/m²")

if superficie > 0:
    st.markdown(f"**Tu precio estimado:** €{precio_m2:,.2f}/m²")
    diferencia = precio_m2 - precio_zona
    porcentaje = (diferencia / precio_zona) * 100
    if porcentaje > 0:
        st.success(f"Estás por encima del mercado (+{porcentaje:.1f}%)")
    else:
        st.info(f"Estás por debajo del mercado ({porcentaje:.1f}%)")

# Mostrar comparables
comparables_zona = comparables.get(zona_seleccionada, [])
if comparables_zona:
    df = pd.DataFrame(comparables_zona)
    df["€/m²"] = df["Precio"] / df["Superficie"]
    st.markdown("**Comparables activos:**")
    st.dataframe(df)
else:
    st.warning("No hay comparables simulados para esta zona.")

