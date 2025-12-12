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

st.write("v1.0 Laatst aangepast 11-12-2025, data validatie heeft plaatsgevonden met Cumlaude percentages, leerlingen naar MBO gelabeld.")
st.write("v0.91 Laatst aangepast 9-12-2025, data verbetering voor onduidelijke doorstroomcategorieën (bijv. h4->VAVO), toelichting pagina Analyse gesplitst.")
st.write("v0.8 Laatst aangepast 3-12-2025, extra pagina met analyse gesplitst en tekortpunten.")
st.write("v0.7 Laatst aangepast 26-11-2025, Eerste pagina om groepen doorstroom te vergelijken")
st.sidebar.success("Select een optie")