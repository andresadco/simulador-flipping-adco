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

# ——— SCRAPING FUNCION MODIFICADA CON FILTROS EXTRAS ———

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
                price = price_tag.get_text(strip=True).replace("\u20ac", "").replace(".", "") if price_tag else "0"
                details = item.select(".item-detail")

                m2 = "0"
                planta = ""
                ascensor = "No"
                estado = ""
                for detail in details:
                    text = detail.get_text(strip=True).lower()
                    if "m²" in text:
                        m2 = text.split("m²")[0].strip().replace(",", ".")
                    if "planta" in text:
                        planta = text
                    if "ascensor" in text:
                        ascensor = "Sí"
                    if any(palabra in text for palabra in ["reformado", "nuevo", "a reformar"]):
                        estado = text

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
                    "Planta": planta.title(),
                    "Ascensor": ascensor,
                    "Estado": estado.title(),
                    "Link": link
                })

        except Exception as e:
            st.warning(f"Error al scrapear {nombre}: {e}")

    return pd.DataFrame(propiedades)

# ——— ANALISIS Y FILTROS VISUALES ———

def mostrar_analisis_comparables(df_subzona):
    st.subheader("📊 Análisis de Comparables")

    try:
        df_subzona["€/m²"] = df_subzona["€/m²"].astype(str).str.replace(",", "").astype(float)
        df_subzona["Superficie (m²)"] = df_subzona["Superficie (m²)"].astype(str).str.replace(",", ".").astype(float)

        promedio = df_subzona["€/m²"].mean()
        minimo = df_subzona["€/m²"].min()
        maximo = df_subzona["€/m²"].max()

        st.metric("📍 Promedio €/m²", f"{promedio:,.0f} €")
        st.metric("📉 Mínimo €/m²", f"{minimo:,.0f} €")
        st.metric("📈 Máximo €/m²", f"{maximo:,.0f} €")

        with st.expander("🌟 Filtros avanzados", expanded=True):
            rango = st.slider("Selecciona el rango €/m²", int(minimo), int(maximo), (int(minimo), int(maximo)), key="slider_comparables")
            plantas = st.multiselect("Filtrar por planta", options=df_subzona["Planta"].unique(), default=list(df_subzona["Planta"].unique()))
            ascensor = st.radio("¿Con ascensor?", options=["Todos", "Sí", "No"], index=0, horizontal=True)
            estados = st.multiselect("Filtrar por estado del inmueble", options=df_subzona["Estado"].unique(), default=list(df_subzona["Estado"].unique()))

        df_filtrado = df_subzona[
            (df_subzona["€/m²"] >= rango[0]) &
            (df_subzona["€/m²"] <= rango[1]) &
            (df_subzona["Planta"].isin(plantas)) &
            (df_subzona["Estado"].isin(estados))
        ]
        if ascensor != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Ascensor"] == ascensor]

        df_filtrado["Link"] = df_filtrado["Link"].apply(lambda x: f"[Ver anuncio]({x})")

        st.write(f"🔎 Se muestran {len(df_filtrado)} propiedades dentro del filtro aplicado.")
        st.write(df_filtrado.to_markdown(index=False), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error procesando comparables: {e}")
