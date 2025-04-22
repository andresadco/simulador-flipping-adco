

import streamlit as st
import pandas as pd
import requests
import random
import time
from bs4 import BeautifulSoup

st.set_page_config(page_title="Simulador Flipping ADCO", layout="wide")
st.title("🏘️ Simulador con Comparables Idealista (Zonas M-30)")

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
                        "Zona": zona,
                        "Título": title,
                        "Precio (€)": price,
                        "Superficie (m²)": m2,
                        "€/m²": f"{eur_m2:,.0f}",
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
            df_result["Link"] = df_result["Link"].apply(lambda x: f"[Ver anuncio]({x})")
            st.success(f"Se obtuvieron {len(df_result)} propiedades.")
            st.write(df_result.to_markdown(index=False), unsafe_allow_html=True)
        else:
            st.error("No se encontraron resultados.")

