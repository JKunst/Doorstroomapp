import pandas as pd
import plotly.graph_objects as go
from components.doorstroom_functions import *
from components.popups import *
import streamlit as st
import numpy as np
import os
#from streamlit-extras import card



# Mount Google Drive (if running in Colab, this will prompt authentication)
# In a local Streamlit environment, ensure the file path is accessible.
# drive.mount('/content/drive')

# --- Functions (copied from notebook) ---
st.set_page_config(layout="wide")
st.set_page_config(page_title="Met tekortpunten", page_icon="📈")
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

# --- Streamlit App Layout ---


# --- Passcode Authentication ---
CORRECT_PASSCODE = "BovenbouwSuc6"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True #Aanpassen

if False: #not st.session_state.logged_in: #override van login
    st.subheader("Login")
    passcode_attempt = st.text_input("Enter Passcode en klik de knop!", type="password")
    if st.button("Login"):
        if passcode_attempt == CORRECT_PASSCODE:
            st.session_state.logged_in = True
            st.rerun()  # Rerun to hide login and show app content
        else:
            st.error("Incorrect Passcode")
else:
    # --- Data Loading ---
    @st.cache_data
    def load_data():
        # Adjust this path if your Streamlit app is not in the Colab /content/drive/MyDrive/Data directory
        file_path = 'updated_df.xlsx'
        if not os.path.exists(file_path):
            st.error(
                f"Error: Data file not found at {file_path}. Please ensure 'updated_df.xlsx' is in your Google Drive's 'Data' folder and Drive is mounted (if running in Colab) or the path is correct.")
            st.stop()
        try:
            df = pd.read_excel(file_path)
            # Ensure 'Schooljaar' is int and 'Inschrijvingsdatum' is datetime
            df['Schooljaar'] = df['Schooljaar'].astype(int)
            df['Inschrijvingsdatum'] = pd.to_datetime(df['Inschrijvingsdatum'])

            # Create 'Tekortpunten_Bucket' column
            bins = [-1, 2, 6, 9, np.inf]
            labels = ['0-3', '4-6', '7-9', '10+']
            df['Tekortpunten_Bucket'] = pd.cut(df['Tekortpunten'], bins=bins, labels=labels, right=True,
                                               include_lowest=True)

            return df
        except Exception as e:
            st.error(f"Error loading or processing data: {e}")
            st.stop()


    updated_df = load_data()

    # --- Sidebar for Filters ---

    # Schooljaar_start and Schooljaar_eind
    all_schoolyears = sorted(updated_df['Schooljaar'].unique().tolist())
    if len(all_schoolyears) > 1:
        default_schooljaar_start_idx = 0  # First year
        default_schooljaar_end_idx = min(2, len(all_schoolyears) - 1)  # Third year, or last if fewer than 3
    else:
        default_schooljaar_start_idx = 0
        default_schooljaar_end_idx = 0



    # Leerfase_start
    all_leerfases = sorted(updated_df['Leerfase (afk)'].dropna().unique().tolist())
    all_leerfases.pop(0)
    all_leerfases.pop(0)
    all_leerfases.pop(0)
    all_leerfases.pop(0)
    all_leerfases.pop(0)
    all_leerfases.pop(0)
    all_leerfases.pop(0)
    all_leerfases.pop(0)
    all_tekortpunten_buckets = sorted(updated_df['Tekortpunten_Bucket'].dropna().unique().tolist())

    # --- Main Content ---

    st.subheader("De doorstroom 3-jaar vooruit")

    #st.subheader(f"Hieronder de groep leerlingen uit '{leerfase_start}' van {schooljaar_start}-{schooljaar_eind + 1} en hun doorstroom in de daaropvolgende jaren")

    st.text("Gebruik onderstaande filters om een groep leerlingen te onderzoeken. De filters aan de rechterkant zijn voor de tweede groep om mee te vergelijken.")
    st.button(
        "ℹ️ Uitleg: Hulp bij filters.",
        on_click=filter_helper
    )
    st.button(
        "ℹ️ Uitleg: Vervolg filters.",
        on_click=filter_helper_2
    )
    if True:
        if updated_df is not None:
            with st.spinner("Berekenen en plaatje maken..."):



                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Analyse groep")
                    schooljaar_start = st.selectbox(
                        "Selecteer start schooljaar data (kies bijv. 2022 en 2022 voor schooljaar 2022-2023, of 2022 2023 voor schooljaren 2022 augustus-2024 juli):",
                        options=all_schoolyears,
                        index=5
                    )
                    schooljaar_eind = st.selectbox(
                        "Tot schooljaar:",
                        options=all_schoolyears,
                        index=5
                    )

                    if schooljaar_start > schooljaar_eind:
                        st.sidebar.error("Start Schooljaar cannot be after End Schooljaar.")
                        st.stop()
                    leerfase_start = st.selectbox(
                        "Selecteer de Leerfase (afk):",
                        options=all_leerfases,
                        index=4
                    )

                    # Tekortpunten_Bucket filter

                    selected_tekortpunten_buckets = st.multiselect(
                        "Selecteer de filter op tekortpunten (In het Startjaar):",
                        options=all_tekortpunten_buckets,
                        default=all_tekortpunten_buckets  # Default to all selected
                    )
                    progression_percentages = analyze_next_leerfase(
                        updated_df,
                        schooljaar_start=schooljaar_start,
                        schooljaar_eind=schooljaar_eind,
                        leerfase_start=leerfase_start,
                        tekortpunten_bucket_filter=selected_tekortpunten_buckets

                    )
                    three_year_transition_counts = analyze_three_year_leerfase_transitions(
                        updated_df,
                        schooljaar_start=schooljaar_start,
                        schooljaar_eind=schooljaar_eind,
                        leerfase_start=leerfase_start,
                        tekortpunten_bucket_filter=selected_tekortpunten_buckets
                    )
                    if not three_year_transition_counts.empty:
                        st.write("#### Aantallen en percentages")
                        st.dataframe(progression_percentages)
                        df_three_year = counts_with_percentages(three_year_transition_counts)
                        st.write("#### Stromen in volgende 3 jaar")
                        st.dataframe(df_three_year)

                    else:
                        st.info("No transitions found for the selected criteria.")
                with col2:
                    st.subheader("Vergelijkingsgroep")
                    schooljaar_start_vergelijk = st.selectbox(
                        "Selecteer ook alle filters voor de groep waarmee je wil vergelijken. ________________________________________________",
                        options=all_schoolyears,
                        index=5,
                        key=1
                    )
                    schooljaar_eind_vergelijk = st.selectbox(
                        "Tot schooljaar:",
                        options=all_schoolyears,
                        index=5,
                        key=2
                    )

                    leerfase_vergelijk = st.selectbox(
                        "Selecteer de Leerfase (afk) om mee te vergelijken:",
                        options=all_leerfases,
                        index=5
                    )

                    selected_tekortpunten_buckets_vergelijk = st.multiselect(
                        "Selecteer de filter op tekortpunten (In het Startjaar):",
                        options=all_tekortpunten_buckets,
                        default=all_tekortpunten_buckets,  # Default to all selected
                        key=6
                    )
                    three_year_transition_counts_vergelijk = analyze_three_year_leerfase_transitions(
                        updated_df,
                        schooljaar_start=schooljaar_start_vergelijk,
                        schooljaar_eind=schooljaar_eind_vergelijk,
                        leerfase_start=leerfase_vergelijk,
                        tekortpunten_bucket_filter=selected_tekortpunten_buckets_vergelijk
                    )
                    vergelijk_percentages = analyze_next_leerfase(
                        updated_df,
                        schooljaar_start=schooljaar_start_vergelijk,
                        schooljaar_eind=schooljaar_eind_vergelijk,
                        leerfase_start=leerfase_vergelijk,
                        tekortpunten_bucket_filter=selected_tekortpunten_buckets_vergelijk

                    )
                    if not three_year_transition_counts.empty:
                        st.write("#### Vergelijking")
                        st.dataframe(vergelijk_percentages)

                        df_three_year_vergelijk = counts_with_percentages(
                            three_year_transition_counts_vergelijk
                        )
                        st.write("#### Stromen in volgende 3 jaar")
                        st.dataframe(df_three_year_vergelijk)

                    else:
                        st.info("No transitions found for the selected criteria.")
                url = "Details_voor_groepen"
                st.write(
                    "Toelichting: als er alleen een leerfase met een aantal staat zonder pijltje. Dan zijn deze leerlingen "
                    "in de geselecteerde periode in de geselecteerde leerfase aangekomen, maar nog niet doorgestroomd. "
                    "Bijvoorbeeld als je jaren 2023-2024 selecteerd dan zijn er in 2024 leerlingen in H4 gestart, maar "
                    "zonder data van 2025-2026 zijn deze leerlingen nog niet doorgestroomd. Zie onderaan op de [pagina Details voor groepen](%s) de tabel met leerlingnummers voor meer inzicht." % url)

                # if not three_year_transition_counts.empty:
                #     # Generate Sankey Diagram
                #     labels, source, target, value = prepare_sankey_data(three_year_transition_counts)
                #     if labels and source and target and value:
                #         title_str = f"Student Progression: {leerfase_start} ({schooljaar_start}-{schooljaar_eind})"
                #         if selected_tekortpunten_buckets:
                #             title_str += f" (Tekortpunten: {', '.join(selected_tekortpunten_buckets)})"
                #
                #         fig = plot_sankey_diagram(labels, source, target, value,
                #                                   title=title_str)
                #         st.write("### Sankey Diagram")
                #         st.plotly_chart(fig, use_container_width=True)
                #     else:
                #         st.warning("Not enough data to generate a Sankey diagram for the selected filters.")
                # else:
                #     st.info("No transitions found for the selected criteria.")
        else:
            st.error("Data not loaded. Please check the file path and data content.")
st.markdown("#### Ben je klaar met deze pagina, je kan altijd verder kijken op de andere pagina's.")
col3, col4, col5 = st.columns(3)

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
st.write("   \n")
st.markdown(
        """
        <a class="card-link" href="/" target="_self">
            <div class="card" style="background-color:#F8FAFC;">
                <h3>Terug naar start</h3>
        </a>
        """,
        unsafe_allow_html=True
    )
st.showSidebarNavigation = False