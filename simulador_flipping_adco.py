import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from numpy_financial import irr
import streamlit as st
import pandas as pd
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
    "Concepto": [
        "🏠 Precio de compra",
        "🏠 Comisión de compra",
        "🏠 ITP / IVA de compra",
        "🏠 Gastos legales",
        "🏠 Gastos administrativos",
        "🏠 IBI",
        "🛠️ Coste de reforma (con IVA)",
        "💼 Inversión total",
        "🏦 Préstamo solicitado",
        "💸 Intereses del préstamo",
        "💼 Capital propio invertido",
        "📈 Precio de venta",
        "📈 Comisión de venta",
        "📊 Ganancia neta esperada",
        "📊 ROI real (%)",
        "📊 TIR real (%)"
    ],
    "Valor estimado (€)": [
        f"{precio_compra:,.0f}",
        f"{precio_compra * comision_compra / 100:,.0f}",
        f"{precio_compra * itp / 100:,.0f}",
        f"{gastos_legales:,.0f}",
        f"{gastos_administrativos:,.0f}",
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
st.markdown(frase_inversion)

# --- ESCENARIOS DE PRECIO DE VENTA ---
st.subheader("🎯 Escenarios: ¿Qué pasa si vendes por más o menos?")

delta_precio = st.slider("Variación en el precio de venta (%)", -20, 20, (-10, 10), step=5)

escenarios_resultados = []
for variacion in range(delta_precio[0], delta_precio[1] + 1, 5):
    factor = 1 + variacion / 100
    nuevo_precio_venta = precio_venta * factor
    nueva_comision_venta = nuevo_precio_venta * comision_venta / 100
    ingreso_final = nuevo_precio_venta - nueva_comision_venta - intereses_totales - devolucion_prestamo
    nueva_ganancia_neta = ingreso_final - capital_propio
    nuevo_roi = (nueva_ganancia_neta / capital_propio * 100) if capital_propio > 0 else 0
    flujo = [-capital_propio] + [0] * (plazo_anios - 1) + [ingreso_final]
    nuevo_tir = irr(flujo) * 100 if ingreso_final > 0 else 0

    escenarios_resultados.append({
        "Variación Precio Venta": f"{variacion:+d}%",
        "Precio de Venta (€)": f"{nuevo_precio_venta:,.0f}",
        "ROI (%)": f"{nuevo_roi:.2f}",
        "TIR (%)": f"{nuevo_tir:.2f}"
    })

df_escenarios = pd.DataFrame(escenarios_resultados)
st.table(df_escenarios)


st.title("🏘️ Comparador de Subzonas – Idealista + ADCO")
st.caption("Obtén datos precisos de comparables reales por subzona")

# Subzonas y URLs
SUBZONAS_M30 = {
    "Chamberí": {
        "Almagro": "https://www.idealista.com/venta-viviendas/madrid/chamberi/almagro/",
        "Trafalgar": "https://www.idealista.com/venta-viviendas/madrid/trafalgar/",
        "Ríos Rosas": "https://www.idealista.com/venta-viviendas/madrid/chamberi/rios-rosas/",
        "Arapiles": "https://www.idealista.com/venta-viviendas/madrid/chamberi/arapiles/",
        "Vallehermoso": "https://www.idealista.com/venta-viviendas/madrid/chamberi/vallehermoso/",
        "Gaztambide": "https://www.idealista.com/venta-viviendas/madrid/chamberi/gaztambide/"
    },
    "Salamanca": {
        "Recoletos": "https://www.idealista.com/venta-viviendas/madrid/salamanca/recoletos/",
        "Castellana": "https://www.idealista.com/venta-viviendas/madrid/salamanca/castellana/",
        "Lista": "https://www.idealista.com/venta-viviendas/madrid/salamanca/lista/",
        "Goya": "https://www.idealista.com/venta-viviendas/madrid/salamanca/goya/",
        "Fuente del Berro": "https://www.idealista.com/venta-viviendas/madrid/salamanca/fuente-del-berro/",
        "Guindalera": "https://www.idealista.com/venta-viviendas/madrid/salamanca/guindalera/"
    },
    "Centro": {
        "Sol": "https://www.idealista.com/venta-viviendas/madrid/centro/sol/",
        "Justicia": "https://www.idealista.com/venta-viviendas/madrid/centro/justicia/",
        "Malasaña-Universidad": "https://www.idealista.com/venta-viviendas/madrid/centro/universidad/",
        "La Latina": "https://www.idealista.com/venta-viviendas/madrid/centro/palacio/",
        "Lavapiés": "https://www.idealista.com/venta-viviendas/madrid/centro/embajadores/",
        "Embajadores": "https://www.idealista.com/venta-viviendas/madrid/centro/cortes/"
    }
}

# Selección dinámica
zona = st.selectbox("Selecciona zona", list(SUBZONAS_M30.keys()))
subzona = st.selectbox("Selecciona subzona", list(SUBZONAS_M30[zona].keys()))

def scrapear_subzona(nombre, url_base):
    scraperapi_key = "c21a8e492547f96ed694f796c0355091"
    headers_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)"
    ]
    propiedades = []

    for page in range(1, 3):
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
                    "Subzona": nombre,
                    "Título": title,
                    "Precio (€)": price,
                    "Superficie (m²)": m2,
                    "€/m²": f"{eur_m2:,.0f}",
                    "Link": link
                })
        except Exception as e:
            st.warning(f"Error al scrapear {nombre}: {e}")

    return pd.DataFrame(propiedades)

# Botón para lanzar el scraping
if st.button("🔍 Obtener comparables de la subzona"):
    with st.spinner("Consultando Idealista..."):
        url = SUBZONAS_M30[zona][subzona]
        df_resultado = scrapear_subzona(subzona, url)
        if not df_resultado.empty:
            df_resultado["Link"] = df_resultado["Link"].apply(lambda x: f"[Ver anuncio]({x})")
            st.session_state["df_subzona"] = df_resultado
            st.success(f"Se obtuvieron {len(df_resultado)} propiedades en {subzona}")
        else:
            st.error("No se encontraron comparables.")

# Si ya hay datos guardados en sesión, los mostramos
if "df_subzona" in st.session_state:
    df_subzona = st.session_state["df_subzona"]

    st.subheader("📊 Análisis de Comparables")

    df_subzona["€/m²"] = df_subzona["€/m²"].str.replace(",", "").astype(float)
    df_subzona["Superficie (m²)"] = df_subzona["Superficie (m²)"].astype(str).str.replace(",", ".").astype(float)

    promedio = df_subzona["€/m²"].mean()
    minimo = df_subzona["€/m²"].min()
    maximo = df_subzona["€/m²"].max()

    st.metric("📍 Promedio €/m²", f"{promedio:,.0f} €")
    st.metric("📉 Mínimo €/m²", f"{minimo:,.0f} €")
    st.metric("📈 Máximo €/m²", f"{maximo:,.0f} €")

    st.subheader("🎛️ Filtro de comparables por €/m²")
    rango = st.slider("Selecciona el rango €/m²", int(minimo), int(maximo), (int(minimo), int(maximo)))

    df_filtrado = df_subzona[(df_subzona["€/m²"] >= rango[0]) & (df_subzona["€/m²"] <= rango[1])]
    df_filtrado["Link"] = df_filtrado["Link"].apply(lambda x: f"[Ver anuncio]({x})")

    st.write(f"🔎 Se muestran {len(df_filtrado)} propiedades dentro del rango seleccionado.")
    st.write(df_filtrado.to_markdown(index=False), unsafe_allow_html=True)

        # --- Análisis de Comparables Obtenidos ---
        st.subheader("📊 Análisis de Comparables")

        if not df_subzona.empty:
            # Conversión para cálculo
            df_subzona["€/m²"] = df_subzona["€/m²"].str.replace(",", "").astype(float)
            df_subzona["Superficie (m²)"] = df_subzona["Superficie (m²)"].astype(str).str.replace(",", ".").astype(float)

            promedio = df_subzona["€/m²"].mean()
            minimo = df_subzona["€/m²"].min()
            maximo = df_subzona["€/m²"].max()

            st.metric("📍 Promedio €/m²", f"{promedio:,.0f} €")
            st.metric("📉 Mínimo €/m²", f"{minimo:,.0f} €")
            st.metric("📈 Máximo €/m²", f"{maximo:,.0f} €")

            # Filtro por rango si se desea
            st.subheader("🎛️ Filtro de comparables por €/m²")
            rango = st.slider("Selecciona el rango €/m²", int(minimo), int(maximo), (int(minimo), int(maximo)))

            df_filtrado = df_subzona[(df_subzona["€/m²"] >= rango[0]) & (df_subzona["€/m²"] <= rango[1])]
            df_filtrado["Link"] = df_filtrado["Link"].apply(lambda x: f"[Ver anuncio]({x})")

            st.write(f"🔎 Se muestran {len(df_filtrado)} propiedades dentro del rango seleccionado.")
            st.write(df_filtrado.to_markdown(index=False), unsafe_allow_html=True)

