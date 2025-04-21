import streamlit as st
import numpy as np
from fpdf import FPDF
from io import BytesIO
import base64

st.set_page_config(page_title="Simulador Flipping - ADCO", layout="centered")

st.title("Simulador de Flipping Inmobiliario")
st.markdown("Versión Pro creada por **ADCO Investments**")

# INPUTS
st.header("Datos del Proyecto")

# Compra
st.subheader("Compra del Inmueble")
superficie = st.number_input("Superficie del piso (m²)", value=80)
ubicacion = st.text_input("Ubicación del piso", "Madrid")
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

# PDF export
if st.button("Descargar resumen en PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Resumen de Proyecto - Flipping Inmobiliario", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Ubicación: {ubicacion}", ln=True)
    pdf.cell(200, 10, txt=f"Superficie total: {superficie} m²", ln=True)
    pdf.cell(200, 10, txt=f"Precio de compra: €{precio_compra:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Precio venta objetivo (20% ROI): €{precio_venta_objetivo:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Precio de venta final (escenario): €{precio_venta_final:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Precio por m²: €{precio_m2:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Inversión total: €{inversion_total:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Gastos totales: €{gastos_totales:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Ganancia neta: €{ganancia_neta:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"ROI total: {roi_total:.2f}%", ln=True)
    pdf.cell(200, 10, txt=f"TIR anual: {tir * 100:.2f}%", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, txt="Este análisis es estimativo y no constituye asesoría financiera.")
    pdf.multi_cell(0, 10, txt="Contacto: andres@adco.es")

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="ADCO_Flipping_Resumen.pdf">Haz clic aquí para descargar el PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
