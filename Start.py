import streamlit as st
import st_pages
from components.popups import *

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)
st.markdown(
    """
    <style>
    .card-link {
        text-decoration: none;
    }

    .card {
        padding: 1.6rem;
        border-radius: 18px;
        height: 100%;
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        transition: all 0.2s ease;
        border: 1px solid rgba(0,0,0,0.05);
    }

    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 22px rgba(0,0,0,0.12);
    }

    .card h3 {
        margin-top: 0;
        margin-bottom: 0.6rem;
        font-size: 1.15rem;
    }

    .card p {
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.write("# Data analyse ! ")
st.write("Met deze tool kan je op ontdekkingstocht in de doorstroomdata. \n   \n"
         "Alle pagina's zijn gebaseerd op de Cumlaude data van de schooljaren 2017-2018 tot 2024-2025. "
        "De tekortpunten zijn voor het eindrapport opgeteld over de vakken per leerling. Deze worden gegroepeerd gebruikt in deze rekentool (0-3, 4-6 etc.). "
        "De overgangen worden weergegeven op basis van de kolom Leerfase (afk) in Cumlaude, "
        "waarbij voor doublure aan de afkorting is toegevoegd. Bijvoorbeeld h4_doublure geeft de groep die voor de tweede keer in havo 4 zit.  \n"

         )
st.write("Een vraag die je jezelf kan stellen is: Hoeveel leerlingen stromen op van H5 naar het VWO, of, wat is het effect van kansrijk bevorderen?")
st.write("Begin met stap 1 hieronder. Veel plezier!")

col2, col3, col4, col5 = st.columns(4)

with col2:
    st.markdown(
        """
        <a class="card-link" href="Analyse_gegroepeerd_naar_tekorten" target="_self">
            <div class="card" style="background-color:#F3F0FF;">
                <h3>1️⃣ Aantallen en doorstroom</h3>
                <p>
                    Onderzoek de aantallen leerlingen per groepen en waar ze naartoe gaan de opvolgende drie jaren.
                </p>
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        """
        <a class="card-link" href="Analyse_gesplitst" target="_self">
            <div class="card" style="background-color:#EEF2FF;">
                <h3>2️⃣ Analyse doorstroom / afstroom</h3>
                <p>
                    Doorstroom in de volgende drie jaar,
                    gesplitst naar doorstroom, afstroom of doublure.
                </p>
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        """
        <a class="card-link" href="Eenjaars_overgangen" target="_self">
            <div class="card" style="background-color:#ECFDF5;">
                <h3>3️⃣ Eenjaars overgangen</h3>
                <p>
                    Eenvoudige weergave van doorstroom
                    met één jaar vooruitkijken.
                </p>
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )

with col5:
    st.markdown(
        """
        <a class="card-link" href="Details_voor_groepen" target="_self">
            <div class="card" style="background-color:#FFF7ED;">
                <h3>4️⃣ Details voor groepen</h3>
                <p>
                    Leerlingnummers per groep om
                    de herkomst van data te controleren.
                </p>
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )
st.write("  \n    \n  \n  \n  \n  \n  \n  \n   \n")
st.write("  \n    \n  \n  \n  \n  \n  \n  \n   \n")
st.write("  \n    \n  \n  \n  \n  \n  \n  \n   \n")
st.button(
    "ℹ️ Uitleg: Wat is nieuw per versie 1.2?",
    on_click=release_notes
)
st.showSidebarNavigation = False
st_pages.hide_pages(["1_Analyse_per_leerfase", "3_Analyse_eenjaar_vooruit", "4_Analyse_gesplitst"])#st.sidebar.success("Select een optie")