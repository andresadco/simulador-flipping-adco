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

# Configuración inicial
st.set_page_config(page_title="Simulador Flipping Inmobiliario – ADCO", layout="wide")

# Título principal
st.title("🏘️ Simulador de Flipping Inmobiliario – ADCO")
st.caption("Desarrollado por ADCO Investments – andres@adco.es")

# --- Sección de inputs del proyecto ---
st.header("📥 Datos del Proyecto")
with st.expander("🏗️ Detalles del Proyecto"):
    col1, col2 = st.columns(2)

    with col1:
        superficie = st.number_input("Superficie total (m²)", value=80)
        superficie_reforma = st.number_input("Superficie a reformar (m²)", value=60)
        coste_reforma_m2 = st.number_input("Coste por m² de reforma (€)", value=1400)
        costes_adicionales = st.number_input("Costes adicionales de reforma (€)", value=5000)
        iva_reforma = st.number_input("IVA en reforma (%)", value=10.0)

    with col2:
        precio_compra = st.number_input("Precio de compra (€)", value=850000)
        comision_compra = st.number_input("Comisión de compra (%)", value=2.0)
        gastos_legales = st.number_input("Gastos legales (€)", value=3000)
        gastos_administrativos = st.number_input("Gastos administrativos (€)", value=3000)
        itp = st.number_input("ITP o IVA de compra (%)", value=6.0)
        ibi = st.number_input("IBI (€)", value=500)

st.subheader("💰 Precio de Venta y Comisión")
precio_venta = st.number_input("Precio de venta esperado (€)", value=1350000)
comision_venta = st.number_input("Comisión de venta (%)", value=3.0)

st.subheader("🏦 Financiamiento")
usa_deuda = st.radio("¿Usar financiamiento?", ["No", "Sí"])
if usa_deuda == "Sí":
    porcentaje_prestamo = st.number_input("Porcentaje de préstamo (%)", value=70.0)
    interes_prestamo = st.number_input("Interés anual (%)", value=4.0)
    plazo_anios = st.number_input("Plazo del préstamo (años)", value=1)
else:
    porcentaje_prestamo, interes_prestamo, plazo_anios = 0.0, 0.0, 1

# --- Cálculos financieros ---

st.header("📊 Análisis Financiero")

coste_reforma = superficie_reforma * coste_reforma_m2 + costes_adicionales
coste_reforma_iva = coste_reforma * (1 + iva_reforma / 100)

costo_total = (
    precio_compra * (1 + comision_compra / 100) +
    precio_compra * (itp / 100) +
    gastos_legales + gastos_administrativos + ibi +
    coste_reforma_iva
)

comision_venta_eur = precio_venta * comision_venta / 100

monto_prestamo = costo_total * porcentaje_prestamo / 100
intereses_totales = monto_prestamo * interes_prestamo / 100 * plazo_anios
capital_propio = costo_total - monto_prestamo

ingresos_finales = precio_venta - comision_venta_eur - intereses_totales - monto_prestamo

flujo_neto = [-capital_propio] + [0] * (plazo_anios - 1) + [ingresos_finales]
roi = (ingresos_finales - capital_propio) / capital_propio * 100 if capital_propio > 0 else 0
TIR = irr(flujo_neto) * 100 if flujo_neto[-1] > 0 else 0

precio_sugerido = capital_propio * 1.2 + comision_venta_eur + intereses_totales + monto_prestamo

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("ROI Real", f"{roi:.2f}%")
with col2:
    st.metric("TIR Real", f"{TIR:.2f}%")
with col3:
    st.metric("Precio sugerido (20% ROI)", f"{precio_sugerido:,.0f} €")

fig, ax = plt.subplots()
ax.bar(["Capital", "Ganancia"], [capital_propio, ingresos_finales - capital_propio], color=["gray", "green"])
ax.set_ylabel("€")
ax.set_title("Inversión vs Ganancia")
st.pyplot(fig)

# --- Escenarios de Precio de Venta ---
st.subheader("🎯 Escenarios de Precio de Venta")
delta_precio = st.slider("Variación (%)", -20, 20, (-10, 10), step=5)
resultados = []
for v in range(delta_precio[0], delta_precio[1] + 1, 5):
    factor = 1 + v / 100
    nuevo_precio = precio_venta * factor
    nueva_comision = nuevo_precio * comision_venta / 100
    nuevo_ingreso = nuevo_precio - nueva_comision - intereses_totales - monto_prestamo
    nueva_ganancia = nuevo_ingreso - capital_propio
    nuevo_roi = (nueva_ganancia / capital_propio) * 100 if capital_propio > 0 else 0
    nueva_TIR = irr([-capital_propio] + [0] * (plazo_anios - 1) + [nuevo_ingreso]) * 100 if nuevo_ingreso > 0 else 0

    resultados.append({
        "Variación": f"{v:+d}%",
        "Nuevo Precio (€)": f"{nuevo_precio:,.0f}",
        "ROI (%)": f"{nuevo_roi:.2f}",
        "TIR (%)": f"{nueva_TIR:.2f}"
    })

st.dataframe(pd.DataFrame(resultados))

# --- Comparador de Subzonas ---
st.header("🏙️ Comparador de Subzonas")

SUBZONAS_M30 = {
    "Chamberí": {"Almagro": "https://www.idealista.com/venta-viviendas/madrid/chamberi/almagro/"},
    "Salamanca": {"Recoletos": "https://www.idealista.com/venta-viviendas/madrid/barrio-de-salamanca/recoletos/"},
    "Centro": {"Sol": "https://www.idealista.com/venta-viviendas/madrid/centro/sol/"}
}

zona = st.selectbox("Zona", list(SUBZONAS_M30.keys()))
subzona = st.selectbox("Subzona", list(SUBZONAS_M30[zona].keys()))

# Función de Scraping Mejorada
def scrapear_subzona(nombre, url_base):
    scraperapi_key = "c21a8e492547f96ed694f796c0355091"
    propiedades = []

    for page in range(1, 3):
        time.sleep(random.uniform(1.5, 3.0))
        params = {"api_key": scraperapi_key, "url": f"{url_base}pagina-{page}.htm"}
        headers = {"User-Agent": random.choice(["Mozilla/5.0 (Windows NT 10.0; Win64; x64)"])}

        try:
            response = requests.get("http://api.scraperapi.com", params=params, headers=headers, timeout=20)
            soup = BeautifulSoup(response.text, "html.parser")
            items = soup.select(".item-info-container")

            for item in items:
                title = item.select_one("a.item-link").get_text(strip=True)
                price = item.select_one(".item-price").get_text(strip=True).replace("€", "").replace(".", "")
                price = float(price.replace(" ", "")) if price else 0
                details = item.select(".item-detail")

                m2, planta, ascensor, estado = 0, "", "No", ""
                for d in details:
                    text = d.get_text(strip=True).lower()
                    if "m²" in text:
                        m2 = float(text.split("m²")[0].strip().replace(",", "."))
                    if "planta" in text:
                        planta = text
                    if "ascensor" in text:
                        ascensor = "Sí"
                    if any(word in text for word in ["reformado", "nuevo", "a reformar"]):
                        estado = text

                eur_m2 = price / m2 if m2 else 0

                propiedades.append({
                    "Subzona": nombre,
                    "Título": title,
                    "Precio (€)": f"{price:,.0f}",
                    "Superficie (m²)": m2,
                    "€/m²": f"{eur_m2:,.0f}",
                    "Planta": planta,
                    "Ascensor": ascensor,
                    "Estado": estado,
                    "Link": f"[Ver anuncio](https://www.idealista.com{item.select_one('a.item-link')['href']})"
                })
        except:
            continue

    return pd.DataFrame(propiedades)

if st.button("🔍 Buscar Comparables"):
    url = SUBZONAS_M30[zona][subzona]
    df = scrapear_subzona(subzona, url)
    if not df.empty:
        st.success(f"Se encontraron {len(df)} propiedades en {subzona}")
        st.dataframe(df)
    else:
        st.warning("No se encontraron propiedades en esta subzona.")
