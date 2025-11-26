import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import os


# Mount Google Drive (if running in Colab, this will prompt authentication)
# In a local Streamlit environment, ensure the file path is accessible.
# drive.mount('/content/drive')

# --- Functions (copied from notebook) ---
st.set_page_config(page_title="Met tekortpunten", page_icon="📈")
def analyze_three_year_leerfase_transitions(df, schooljaar_start, schooljaar_eind, leerfase_start,
                                            leerlingnummer_filter=None, tekortpunten_bucket_filter=None):
    """
    Analyzes 'Leerfase (afk)' transitions for students over three consecutive school years.
    Shows up to three transitions, even if fewer are available consecutively.

    Args:
        df (pd.DataFrame): The input DataFrame, expected to be sorted by 'Leerlingnummer' and 'Schooljaar'.
                           It must contain 'Leerlingnummer', 'Schooljaar', and 'Leerfase (afk)' columns.
        schooljaar_start (int): The starting school year (inclusive) for the analysis.
        schooljaar_eind (int): The ending school year (inclusive) for the analysis.
        leerfase_start (str): The specific 'Leerfase (afk)' from which to track transitions.
        leerlingnummer_filter (int or list, optional): A single 'Leerlingnummer' or a list of 'Leerlingnummer's
                                                       to filter the analysis. Defaults to None (all students).
        tekortpunten_bucket_filter (list, optional): A list of 'Tekortpunten_Bucket' categories to filter.
                                                   Defaults to None (all buckets).

    Returns:
        pd.Series: A Series with three-year transition strings as index and counts as values.
                   (e.g., "v5 -> v6", "v5 -> v6 -> h1", or "v5 -> v6 -> h1 -> h2").
    """
    # Filter students who were in the leerfase_start within the specified year range.
    initial_phase_students_df = df[
        (df['Schooljaar'] >= schooljaar_start) &
        (df['Schooljaar'] <= schooljaar_eind) &
        (df['Leerfase (afk)'] == leerfase_start)
        ].copy()  # Use .copy() to avoid SettingWithCopyWarning

    if leerlingnummer_filter is not None:
        if isinstance(leerlingnummer_filter, int):
            leerlingnummer_filter = [leerlingnummer_filter]
        initial_phase_students_df = initial_phase_students_df[
            initial_phase_students_df['Leerlingnummer'].isin(leerlingnummer_filter)
        ]

    if tekortpunten_bucket_filter is not None and len(tekortpunten_bucket_filter) > 0:
        initial_phase_students_df = initial_phase_students_df[
            initial_phase_students_df['Tekortpunten_Bucket'].isin(tekortpunten_bucket_filter)
        ]

    # Get unique Leerlingnummer's from the filtered initial phase students
    relevant_leerlingnummers = initial_phase_students_df['Leerlingnummer'].unique()

    if len(relevant_leerlingnummers) == 0:
        # st.warning(f"No students found in '{leerfase_start}' between {schooljaar_start}-{schooljaar_eind} (or matching filter).")
        return pd.Series([], dtype=int)

    # Get ALL records for these relevant students.
    student_records = df[df['Leerlingnummer'].isin(relevant_leerlingnummers)].copy()
    student_records = student_records.sort_values(by=['Leerlingnummer', 'Schooljaar'])

    # Calculate the next two 'Leerfase (afk)' and 'Schooljaar' for each student
    student_records['next_leerfase_1'] = student_records.groupby('Leerlingnummer')['Leerfase (afk)'].shift(-1)
    student_records['next_schooljaar_1'] = student_records.groupby('Leerlingnummer')['Schooljaar'].shift(-1)
    student_records['next_leerfase_2'] = student_records.groupby('Leerlingnummer')['Leerfase (afk)'].shift(-2)
    student_records['next_schooljaar_2'] = student_records.groupby('Leerlingnummer')['Schooljaar'].shift(-2)
    student_records['next_leerfase_3'] = student_records.groupby('Leerlingnummer')['Leerfase (afk)'].shift(-3)
    student_records['next_schooljaar_3'] = student_records.groupby('Leerlingnummer')['Schooljaar'].shift(-3)

    # Filter for starting points within the specified range
    transitions_df = student_records[
        (student_records['Leerfase (afk)'] == leerfase_start) &
        (student_records['Schooljaar'] >= schooljaar_start) &
        (student_records['Schooljaar'] <= schooljaar_eind)
        ].copy()

    # Apply tekortpunten_bucket_filter to the starting points again if specified
    if tekortpunten_bucket_filter is not None and len(tekortpunten_bucket_filter) > 0:
        transitions_df = transitions_df[
            transitions_df['Tekortpunten_Bucket'].isin(tekortpunten_bucket_filter)
        ]

    if transitions_df.empty:
        # st.warning(f"No starting points found from '{leerfase_start}' between {schooljaar_start}-{schooljaar_eind} (or matching filter).")
        return pd.Series([], dtype=int)

    # Initialize the transition string with the starting phase and its bucket
    transitions_df['Transition'] = transitions_df['Leerfase (afk)'] + ' [' + transitions_df[
        'Tekortpunten_Bucket'].astype(str) + ']'

    # Conditionally add the first transition
    transitions_df['Transition'] = np.where(
        (transitions_df['next_schooljaar_1'] == transitions_df['Schooljaar'] + 1) & (
            transitions_df['next_leerfase_1'].notna()),
        transitions_df['Transition'] + ' -> ' + transitions_df['next_leerfase_1'],
        transitions_df['Transition']
    )

    # Conditionally add the second transition
    transitions_df['Transition'] = np.where(
        (transitions_df['next_schooljaar_1'] == transitions_df['Schooljaar'] + 1) &
        (transitions_df['next_schooljaar_2'] == transitions_df['Schooljaar'] + 2) &
        (transitions_df['next_leerfase_2'].notna()),
        transitions_df['Transition'] + ' -> ' + transitions_df['next_leerfase_2'],
        transitions_df['Transition']
    )

    # Conditionally add the third transition
    transitions_df['Transition'] = np.where(
        (transitions_df['next_schooljaar_1'] == transitions_df['Schooljaar'] + 1) &
        (transitions_df['next_schooljaar_2'] == transitions_df['Schooljaar'] + 2) &
        (transitions_df['next_schooljaar_3'] == transitions_df['Schooljaar'] + 3) &
        (transitions_df['next_leerfase_3'].notna()),
        transitions_df['Transition'] + ' -> ' + transitions_df['next_leerfase_3'],
        transitions_df['Transition']
    )

    # Aantal the occurrences of each unique transition
    transition_counts = transitions_df['Transition'].value_counts()

    return transition_counts


def prepare_sankey_data(transition_counts):
    """
    Processes transition counts to prepare data for a Sankey diagram.

    Args:
        transition_counts (pd.Series): A Series where the index contains transition strings
                                       (e.g., 'h3 -> h4 -> Geslaagd') and values are the counts.

    Returns:
        tuple: A tuple containing four lists: (labels, source, target, value)
               - labels (list): Unique node labels.
               - source (list): Source node indices for links.
               - target (list): Target node indices for links.
               - value (list): Values (counts) for links.
    """
    all_labels = []
    for transition_string in transition_counts.index:
        # Split on ' -> ' to get individual nodes
        steps = transition_string.split(' -> ')
        all_labels.extend(steps)

    # Remove duplicates and sort for consistent node ordering
    labels = sorted(list(set(all_labels)))

    # Create a mapping from label to its index
    label_to_index = {label: i for i, label in enumerate(labels)}

    source = []
    target = []
    value = []

    for transition_string, Aantal in transition_counts.items():
        steps = transition_string.split(' -> ')
        for i in range(len(steps) - 1):
            step_current = steps[i]
            step_next = steps[i + 1]

            # Get indices for source and target
            source_index = label_to_index[step_current]
            target_index = label_to_index[step_next]

            source.append(source_index)
            target.append(target_index)
            value.append(Aantal)

    # Aggregate values for identical source-target links
    sankey_links_df = pd.DataFrame({
        'source': source,
        'target': target,
        'value': value
    })

    # Group by source and target and sum the values
    aggregated_links = sankey_links_df.groupby(['source', 'target'])['value'].sum().reset_index()

    return labels, aggregated_links['source'].tolist(), aggregated_links['target'].tolist(), aggregated_links[
        'value'].tolist()


def plot_sankey_diagram(labels, source, target, value, title="Doorstroom leerlingen (3-jaar vooruit)"):
    """
    Generates an interactive Sankey diagram.

    Args:
        labels (list): Unique node labels.
        source (list): Source node indices for links.
        target (list): Target node indices for links.
        value (list): Values (counts) for links.
        title (str): Title for the Sankey diagram.

    Returns:
        go.Figure: A Plotly Figure object representing the Sankey diagram.
    """
    fig = go.Figure(data=[
        go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                # color=["blue", "blue", "red", "red", ...] # Example: assign colors to nodes
            ),
            link=dict(
                source=source,  # indices correspond to labels, e.g. 0 = 'A', 1 = 'B', 2 = 'C'
                target=target,
                value=value,
                # color=["rgba(0,0,255,0.2)", ...] # Example: assign colors to links
            )
        )
    ])

    fig.update_layout(title_text=title, font_size=10)
    # fig.show() # In Streamlit, use st.plotly_chart(fig)
    return fig


# --- Streamlit App Layout ---

st.title("Analyse van doorstroom (3-jaar vooruit), met tekortpunten groepering")

# --- Passcode Authentication ---
CORRECT_PASSCODE = "BovenbouwSuc6"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

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
            bins = [-1, 2, 5, 8, np.inf]
            labels = ['0-2', '3-5', '6-8', '9+']
            df['Tekortpunten_Bucket'] = pd.cut(df['Tekortpunten'], bins=bins, labels=labels, right=True,
                                               include_lowest=True)

            return df
        except Exception as e:
            st.error(f"Error loading or processing data: {e}")
            st.stop()


    updated_df = load_data()

    # --- Sidebar for Filters ---
    st.sidebar.header("Analysis Filters")

    # Schooljaar_start and Schooljaar_eind
    all_schoolyears = sorted(updated_df['Schooljaar'].unique().tolist())
    if len(all_schoolyears) > 1:
        default_schooljaar_start_idx = 0  # First year
        default_schooljaar_end_idx = min(2, len(all_schoolyears) - 1)  # Third year, or last if fewer than 3
    else:
        default_schooljaar_start_idx = 0
        default_schooljaar_end_idx = 0

    schooljaar_start = st.sidebar.selectbox(
        "Selecteer start schooljaar data (kies bijv. 2022 voor schooljaar 2022-2023):",
        options=all_schoolyears,
        index=default_schooljaar_start_idx
    )
    schooljaar_eind = st.sidebar.selectbox(
        "Select eind schooljaar:",
        options=all_schoolyears,
        index=default_schooljaar_end_idx
    )

    if schooljaar_start > schooljaar_eind:
        st.sidebar.error("Start Schooljaar cannot be after End Schooljaar.")
        st.stop()

    # Leerfase_start
    all_leerfases = sorted(updated_df['Leerfase (afk)'].dropna().unique().tolist())
    all_leerfases.pop(0)
    leerfase_start = st.sidebar.selectbox(
        "Selecteer de Leerfase (afk):",
        options=all_leerfases,
        index=5
    )

    # Tekortpunten_Bucket filter
    all_tekortpunten_buckets = sorted(updated_df['Tekortpunten_Bucket'].dropna().unique().tolist())
    selected_tekortpunten_buckets = st.sidebar.multiselect(
        "Selecteer de filter op tekortpunten (In het Startjaar):",
        options=all_tekortpunten_buckets,
        default=all_tekortpunten_buckets  # Default to all selected
    )

    leerfase_vergelijk = st.sidebar.selectbox(
        "Selecteer de Leerfase (afk) om mee te vergelijken:",
        options=all_leerfases,
        index=5
    )

    # --- Main Content ---


    st.subheader(f"Hieronder de groep leerlingen uit '{leerfase_start}' van {schooljaar_start}-{schooljaar_eind + 1} en hun doorstroom in de daaropvolgende jaren")
    st.text("Toelichting")
    if st.button("Run Analysis"):
        if updated_df is not None:
            with st.spinner("Berekenen en plaatje maken..."):
                three_year_transition_counts = analyze_three_year_leerfase_transitions(
                    updated_df,
                    schooljaar_start=schooljaar_start,
                    schooljaar_eind=schooljaar_eind,
                    leerfase_start=leerfase_start,
                    tekortpunten_bucket_filter=selected_tekortpunten_buckets
                )
                three_year_transition_counts_vergelijk = analyze_three_year_leerfase_transitions(
                    updated_df,
                    schooljaar_start=schooljaar_start,
                    schooljaar_eind=schooljaar_eind,
                    leerfase_start=leerfase_vergelijk
                )

                col1, col2 = st.columns(2)
                with col1:
                    if not three_year_transition_counts.empty:
                        st.write("### Aantallen")

                        st.dataframe(three_year_transition_counts)

                    else:
                        st.info("No transitions found for the selected criteria.")
                with col2:
                    if not three_year_transition_counts.empty:
                        st.write("### Vergelijking")

                        st.dataframe(three_year_transition_counts_vergelijk)
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