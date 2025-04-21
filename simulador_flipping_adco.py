import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Simulador de Flipping ADCO", layout="centered")
st.title("🏘️ Simulador de Flipping Inmobiliario")
st.caption("Versión Pro creada por ADCO Investments")

st.header("📥 Datos del Proyecto")

# Compra
st.subheader("📌 Compra del Inmueble")
superficie = st.number_input("Superficie del piso (m²)", value=80)
ubicacion = st.text_input("Ubicación del piso", value="Madrid")
precio_compra = st.number_input("Precio de compra propuesto (€)", value=950000)
comision_compra = st.number_input("Comisión de compra (%)", value=0.0)
gastos_legales = st.number_input("Gastos legales (€)", value=5000)
gastos_administrativos = st.number_input("Gastos administrativos (€)", value=3000)
itp = st.number_input("Impuesto de compra (ITP o IVA) (%)", value=2.0)
ibi = st.number_input("IBI (€)", value=600.0)
tasacion = st.number_input("Tasación (€)", value=400.0)
registro = st.number_input("Registro de la propiedad (€)", value=1000.0)

# Reforma
st.subheader("🔨 Reforma del Inmueble")
superficie_reforma = st.number_input("Superficie a reformar (m²)", value=80)
coste_reforma_m2 = st.number_input("Coste por m² de reforma (€)", value=1500)
costes_adicionales = st.number_input("Costes adicionales de reforma (€)", value=5000)
iva_reforma = st.number_input("IVA en reformas (%)", value=10.0)

# Venta
st.subheader("💰 Venta del Inmueble")
comision_venta = st.number_input("Comisión de venta (%)", value=3.0)

# Financiamiento
st.subheader("🏦 Financiamiento")
porcentaje_prestamo = st.number_input("Monto del préstamo (% sobre compra)", value=70.0)
tasa_interes = st.number_input("Tasa de interés (%)", value=4.0)
plazo = st.number_input("Plazo del préstamo (años)", value=1)

# Cálculos
coste_reforma_total = superficie_reforma * coste_reforma_m2 + costes_adicionales
coste_reforma_total_iva = coste_reforma_total * (1 + iva_reforma / 100)
gastos_totales = (
    precio_compra +
    precio_compra * comision_compra / 100 +
    gastos_legales +
    gastos_administrativos +
    precio_compra * itp / 100 +
    ibi +
    tasacion +
    registro +
    coste_reforma_total_iva
)
precio_venta_minimo = gastos_totales * 1.2

st.subheader("📈 Precio de Venta Sugerido")
st.metric("Precio de venta mínimo (ROI 20%)", f"{precio_venta_minimo:,.2f} €")
precio_venta = st.number_input("Precio de venta propuesto (€)", value=int(precio_venta_minimo))

# Resultados
ganancia_neta = precio_venta - gastos_totales
roi_total = (ganancia_neta / gastos_totales) * 100

st.subheader("📊 Resultados")
st.write(f"**Precio de venta final:** {precio_venta:,.2f} €")
st.write(f"**Coste total de reforma (con IVA):** {coste_reforma_total_iva:,.2f} €")
st.write(f"**Inversión total (sin intereses):** {gastos_totales:,.2f} €")
st.write(f"**Ganancia neta del proyecto:** {ganancia_neta:,.2f} €")
st.write(f"**ROI total:** {roi_total:.2f} %")

# Tabla de comparables reales
if os.path.exists("comparables_chamberi.csv"):
    st.subheader("🏘️ Comparables en Chamberí (datos reales)")
    comparables_df = pd.read_csv("comparables_chamberi.csv")
    comparables_df["Link"] = comparables_df["Link"].apply(lambda x: f"[Ver anuncio]({x})")
    st.write(comparables_df.to_markdown(index=False), unsafe_allow_html=True)
else:
    st.info("No se encontraron comparables reales para Chamberí.")


