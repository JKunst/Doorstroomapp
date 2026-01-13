import streamlit as st

@st.dialog("Nieuw per versie van app (Huidige 1.1)")
def release_notes():
    st.markdown("""
    v1.1 Aanpassing paginavolgorde, precentages in tabel, filters boven tabellen in 3 jaars vergelijk.  \n
v1.0 Laatst aangepast 11-12-2025, data validatie heeft plaatsgevonden met Cumlaude percentages, leerlingen naar MBO gelabeld.  \n
v0.91 Laatst aangepast 9-12-2025, data verbetering voor onduidelijke doorstroomcategorieën (bijv. h4->VAVO), toelichting pagina Analyse gesplitst.  \n
v0.8 Laatst aangepast 3-12-2025, extra pagina met analyse gesplitst en tekortpunten.  \n
v0.7 Laatst aangepast 26-11-2025, Eerste pagina om groepen doorstroom te vergelijken.  \n
    """)

@st.dialog("Hulp met filters", width="large")
def filter_helper():
    st.markdown("""
                Als je de filters als volgt instelt, selecteer je de leerlingen (voor het eerst) in havo 4 in schooljaar 2022-2023. Je vergelijkt deze met de leerlingen de doublanten in dat jaar h4_doublure:""")
    st.image(
            "components/input_example.jpg",
            caption="Voorbeeldinstelling",
            use_container_width=True
        )
    st.markdown("""Geeft dit de volgende output""")
    st.image(
        "components/output_example.jpg",
        caption="Voorbeeldoutput",
        use_container_width=True
    )

@st.dialog("Hulp met filters deel 2", width="large")
def filter_helper_2():
    st.markdown("""
                Als je de vervolgens gaat kijken naar de leerlingen met 4-6 tekortpunten""")
    st.image(
            "components/input_example_2.png",
            caption="Voorbeeldinstelling",
            use_container_width=True
        )
    st.markdown("""Geeft dit de volgende stromen (2e plaatje)""")
    st.image(
        "components/output_example_2.png",
        caption="Doorstroom geselecteerde leerlingen",
        use_container_width=True
    )