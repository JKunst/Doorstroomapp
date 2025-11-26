import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Data analyse ! ")
st.write("Gebaseerd op de Cumlaude data van de schooljaren 2017-2018 tot 2024-2025. "
        "Tekortpunten opgeteld over de vakken per leerling. Deze worden in buckets gebruikt in deze rekentool. "
        "De overgangen worden weergegeven op basis van de kolom Leerfase (afk) in Cumlaude, "
        "waarbij voor doublure dit aan de afkorting is toegevoegd. "
         ""
         "Laat vragen of opmerkingen vooral weten.")

st.sidebar.success("Select een optie")