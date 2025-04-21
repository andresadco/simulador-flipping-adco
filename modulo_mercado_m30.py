
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Módulo de Mercado - ADCO", layout="centered")

st.title("Inteligencia de Mercado - Flipping ADCO")
st.markdown("Consulta de precios promedio por zona dentro de la M-30")

# Zonas dentro de la M-30
zonas_m30 = [
    "Chamberí", "Salamanca", "Retiro", "Centro", 
    "Chamartín", "Arganzuela", "Tetuán", 
    "Usera Norte", "Moncloa-Aravaca", "Latina Norte", "Carabanchel Norte"
]

zona_seleccionada = st.selectbox("Selecciona una zona", zonas_m30)

# Simulación de base de datos de precios por zona (ejemplo estático)
precios_m2 = {
    "Chamberí": 5280,
    "Salamanca": 6830,
    "Retiro": 4950,
    "Centro": 4780,
    "Chamartín": 5600,
    "Arganzuela": 4260,
    "Tetuán": 4170,
    "Usera Norte": 2900,
    "Moncloa-Aravaca": 5000,
    "Latina Norte": 3400,
    "Carabanchel Norte": 3100
}

# Simulación de comparables (se reemplazará por scraping real)
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

precio_zona = precios_m2.get(zona_seleccionada, None)
comparables_zona = comparables.get(zona_seleccionada, [])

st.markdown("---")
st.subheader("Resultado del análisis")

if precio_zona:
    st.markdown(f"**Precio medio por m² en {zona_seleccionada}:** €{precio_zona:,.2f}/m²")

    if comparables_zona:
        df = pd.DataFrame(comparables_zona)
        df["€/m²"] = df["Precio"] / df["Superficie"]
        st.markdown("**Comparables activos:**")
        st.dataframe(df)
    else:
        st.info("No hay comparables simulados para esta zona todavía.")
else:
    st.warning("No se encontró información para esta zona.")

st.markdown("---")
st.caption("Datos simulados - versión de desarrollo para scraping Idealista")
