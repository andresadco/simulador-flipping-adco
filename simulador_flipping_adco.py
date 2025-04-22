import streamlit as st
import pandas as pd
import numpy as np
import requests
import random
import time
from bs4 import BeautifulSoup

st.set_page_config(page_title="Simulador Flipping ADCO", layout="wide")
st.title("🏘️ Simulador de Flipping Inmobiliario + Comparables Idealista")

# --- INPUTS DEL SIMULADOR ---
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
usar_deuda = st.selectbox("¿Usar financiamiento?", ["No", "Sí"])
if usar_deuda == "Sí":
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
precio_venta = st.number_input("Precio de venta propuesto (€)", value=int(precio_venta_minimo))

# Resultado
ganancia_neta = precio_venta - gastos_totales
roi_total = (ganancia_neta / gastos_totales) * 100

st.subheader("📊 Resultados")
st.metric("Ganancia neta del proyecto", f"{ganancia_neta:,.2f} €")
st.metric("ROI total", f"{roi_total:.2f} %")

# --- SCRAPING IDEALISTA ---
st.header("🏘️ Comparables Idealista")

ZONAS_M30 = {
    "Chamberí": "https://www.idealista.com/venta-viviendas/madrid/chamberi/",
    "Salamanca": "https://www.idealista.com/venta-viviendas/madrid/salamanca-madrid/",
    "Retiro": "https://www.idealista.com/venta-viviendas/madrid/retiro/",
    "Centro": "https://www.idealista.com/venta-viviendas/madrid/centro-madrid/",
    "Arganzuela": "https://www.idealista.com/venta-viviendas/madrid/arganzuela/",
    "Tetuán": "https://www.idealista.com/venta-viviendas/madrid/tetuan/",
    "Chamartín": "https://www.idealista.com/venta-viviendas/madrid/chamartin/"
}

zonas_seleccionadas = st.multiselect("Selecciona zonas para obtener comparables:", list(ZONAS_M30.keys()), default=["Chamberí"])

def scrapear_idealista(zonas):
    scraperapi_key = "c21a8e492547f96ed694f796c0355091"
    headers_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)"
    ]
    propiedades = []

    for zona in zonas:
        url_base = ZONAS_M30[zona]
        for page in range(1, 2):
            time.sleep(random.uniform(1.5, 3.0))
            params = {
                "api_key": scraperapi_key,
                "url": f"{url_base}pagina-{page}.htm"
            }
            headers = {
                "User-Agent": random.choice(headers_list),
                "Accept-Language": "es-ES,es;q=0.9"
            }
            try:
                response = requests.get("http://api.scraperapi.com", params=params, headers=headers, timeout=20)
                soup = BeautifulSoup(response.text, "html.parser")
                items = soup.select(".item-info-container")
                for item in items:
                    title = item.select_one("a.item-link").get_text(strip=True)
                    price_tag = item.select_one(".item-price")
                    price = price_tag.get_text(strip=True).replace("€", "").replace(".", "") if price_tag else "0"
                    details = item.select(".item-detail")
                    m2 = "0"
                    for detail in details:
                        text = detail.get_text(strip=True)
                        if "m²" in text:
                            m2 = text.split("m²")[0].strip().replace(",", ".")
                            break
                    link = "https://www.idealista.com" + item.select_one("a.item-link")["href"]
                    try:
                        m2_val = float(m2) if m2.replace('.', '', 1).isdigit() else 0
                        price_val = float(price)
                        eur_m2 = price_val / m2_val if m2_val else 0
                    except:
                        eur_m2 = 0
                    propiedades.append({
                        "Zona": zona,
                        "Título": title,
                        "Precio (€)": price,
                        "Superficie (m²)": m2,
                        "€/m²": round(eur_m2),
                        "Link": link
                    })
            except Exception as e:
                st.warning(f"Error al scrapear {zona}: {e}")

    df = pd.DataFrame(propiedades)
    return df

if st.button("🔄 Obtener comparables ahora"):
    with st.spinner("Obteniendo datos desde Idealista..."):
        df_result = scrapear_idealista(zonas_seleccionadas)
        if not df_result.empty:
            st.success(f"Se obtuvieron {len(df_result)} propiedades.")
            st.dataframe(df_result)
        else:
            st.error("No se encontraron resultados.")


