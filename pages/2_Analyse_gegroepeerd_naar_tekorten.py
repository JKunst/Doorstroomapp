import pandas as pd
import plotly.graph_objects as go
from components.doorstroom_functions import *
import streamlit as st
import numpy as np
import os



# Mount Google Drive (if running in Colab, this will prompt authentication)
# In a local Streamlit environment, ensure the file path is accessible.
# drive.mount('/content/drive')

# --- Functions (copied from notebook) ---
st.set_page_config(layout="wide")
st.set_page_config(page_title="Met tekortpunten", page_icon="📈")


# --- Streamlit App Layout ---


# --- Passcode Authentication ---
CORRECT_PASSCODE = "BovenbouwSuc6"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False #Aanpassen

if not st.session_state.logged_in:
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

    all_tekortpunten_buckets = sorted(updated_df['Tekortpunten_Bucket'].dropna().unique().tolist())

    # --- Main Content ---

    st.subheader("Analyse van doorstroom (3-jaar vooruit), met tekortpunten groepering")

    #st.subheader(f"Hieronder de groep leerlingen uit '{leerfase_start}' van {schooljaar_start}-{schooljaar_eind + 1} en hun doorstroom in de daaropvolgende jaren")
    st.text("Toelichting")
    if True:
        if updated_df is not None:
            with st.spinner("Berekenen en plaatje maken..."):



                col1, col2 = st.columns(2)
                with col1:
                    schooljaar_start = st.selectbox(
                        "Selecteer start schooljaar data (kies bijv. 2022 en 2022 voor schooljaar 2022-2023, of 2022 2023 voor schooljaren 2022 augustus-2024 juli):",
                        options=all_schoolyears,
                        index=default_schooljaar_start_idx
                    )
                    schooljaar_eind = st.selectbox(
                        "Tot schooljaar:",
                        options=all_schoolyears,
                        index=default_schooljaar_end_idx
                    )

                    if schooljaar_start > schooljaar_eind:
                        st.sidebar.error("Start Schooljaar cannot be after End Schooljaar.")
                        st.stop()
                    leerfase_start = st.selectbox(
                        "Selecteer de Leerfase (afk):",
                        options=all_leerfases,
                        index=5
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
                        st.write("### Aantallen en percentages")
                        st.dataframe(progression_percentages)
                        df_three_year = counts_with_percentages(three_year_transition_counts)

                        st.dataframe(df_three_year)

                    else:
                        st.info("No transitions found for the selected criteria.")
                with col2:

                    schooljaar_start_vergelijk = st.selectbox(
                        "Selecteer ook alle filters voor de groep waarmee je wil vergelijken. ________________________________________________",
                        options=all_schoolyears,
                        index=default_schooljaar_start_idx,
                        key=1
                    )
                    schooljaar_eind_vergelijk = st.selectbox(
                        "Tot schooljaar:",
                        options=all_schoolyears,
                        index=default_schooljaar_end_idx,
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
                        st.write("### Vergelijking")
                        st.dataframe(vergelijk_percentages)
                        df_three_year_vergelijk = counts_with_percentages(
                            three_year_transition_counts_vergelijk
                        )

                        st.dataframe(df_three_year_vergelijk)
                        st.write(
                            "Toelichting: als er alleen een leerfase met een aantal staat zonder pijltje. Dan zijn deze leerlingen "
                            "in de geselecteerde periode in de geselecteerde leerfase aangekomen, maar nog niet doorgestroomd. Bijvoorbeeld als je jaren 2023-2024 selecteerd dan zijn er in 2024 leerlingen in H4 gestart, maar zonder data van 2025-2026 zijn deze leerlingen nog niet doorgestroomd. Zie onderaan op de Analyse per leerfase pagina de tabel met leerlingnummers voor meer inzicht.")
                    else:
                        st.info("No transitions found for the selected criteria.")
                if not three_year_transition_counts.empty:
                    # Generate Sankey Diagram
                    labels, source, target, value = prepare_sankey_data(three_year_transition_counts)
                    if labels and source and target and value:
                        title_str = f"Student Progression: {leerfase_start} ({schooljaar_start}-{schooljaar_eind})"
                        if selected_tekortpunten_buckets:
                            title_str += f" (Tekortpunten: {', '.join(selected_tekortpunten_buckets)})"

                        fig = plot_sankey_diagram(labels, source, target, value,
                                                  title=title_str)
                        st.write("### Sankey Diagram")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Not enough data to generate a Sankey diagram for the selected filters.")
                else:
                    st.info("No transitions found for the selected criteria.")
        else:
            st.error("Data not loaded. Please check the file path and data content.")

st.showSidebarNavigation = False