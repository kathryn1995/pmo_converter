import streamlit as st
import pandas as pd
import json
import os
from src.data_loader import load_csv
from src.field_matcher import auto_match_fields, check_for_duplicates, interactive_field_mapping, field_mapping_json_to_table
from src.transformer import transform_panel_info
from src.format_page import render_header

# Helper functions for loading and saving JSON
current_directory = os.getcwd()  # Get the current working directory
SAVE_DIR = os.path.join(current_directory, "saved_panels")
os.makedirs(SAVE_DIR, exist_ok=True)  # Ensure the directory exists
# SAVE_DIR = "saved_panels"
# os.makedirs(SAVE_DIR, exist_ok=True)


def save_panel(panel_name, panel_data):
    with open(os.path.join(SAVE_DIR, f"{panel_name}.json"), "w") as f:
        json.dump(panel_data, f)


def load_panel(panel_name):
    with open(os.path.join(SAVE_DIR, f"{panel_name}.json"), "r") as f:
        return json.load(f)


def get_saved_panels():
    return [f.split(".json")[0] for f in os.listdir(SAVE_DIR) if f.endswith(".json")]


render_header()
st.subheader("Panel Information Converter", divider="gray")
# Option to load past versions
use_past = st.checkbox("Use a past version")
if use_past:
    saved_panels = get_saved_panels()
    if saved_panels:
        selected_panel = st.selectbox("Select a saved panel:", saved_panels)
        if st.button("Load Panel"):
            panel_data = load_panel(selected_panel)
            st.session_state["panel_info"] = panel_data
            st.success(f"Loaded panel: {selected_panel}")
    else:
        st.warning("No saved panels found.")
else:
    # Panel ID
    st.subheader("Panel ID")
    panel_ID = st.text_input(
        "Enter panel ID:", help='Identifier for the panel.')
    # Upload CSV
    st.subheader("Upload File")
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    if uploaded_file:
        df = load_csv(uploaded_file)
        interactive_preview = st.toggle("Preview File")
        if interactive_preview:
            st.write("Uploaded File Preview:")
            st.dataframe(df)

        # AI / Fuzzy Field Matching
        st.subheader("Match Fields")
        target_schema = ["target_id", "forward_primers", "reverse_primers"]
        method = st.selectbox("Select Matching Method:", ["Fuzzy", "AI"])
        api_key = None
        if method == "AI":
            api_key = st.text_input(
                "Enter OpenAI API Key:", type="password")

        df_columns = df.columns.tolist()
        field_mapping, unused_field_names = auto_match_fields(
            df.columns.tolist(),
            target_schema,
            method=method.lower(),
            api_key=api_key
        )
        st.write("Suggested Field Mapping:")
        st.dataframe(field_mapping_json_to_table(field_mapping))
        # TODO: ADD OPTIONAL FIELDS
        # forward_primers_start_col, forward_primers_end_col, reverse_primers_start_col, reverse_primers_end_col, insert_start_col, insert_end_col, chrom_col, strand_col, gene_id_col, target_type_col
        # Interactive Mapping
        interactive_field_mapping_on = st.toggle(
            "Manually Alter Field Mapping")
        if interactive_field_mapping_on:
            updated_mapping = interactive_field_mapping(
                field_mapping, df_columns)
            # Display the updated mapping after user interaction
            st.write("Updated Field Mapping:")
            st.dataframe(field_mapping_json_to_table(updated_mapping))

            check_for_duplicates(updated_mapping)

        # Add additional fields
        st.subheader("Add Additional Fields")
        selected_additional_fields = None
        if unused_field_names:
            optional_additional_fields = st.toggle("Add additional fields")
            if optional_additional_fields:
                # Dictionary to store checkbox states
                checkbox_states = {}
                st.write(
                    "Select the extra columns you would like to include:")
                # Dynamically create a checkbox for each item in the list
                for item in unused_field_names:
                    # Add checkbox and store its state in the dictionary
                    checkbox_states[item] = st.checkbox(label=item)

                # Display selected items
                selected_additional_fields = [key for key,
                                              value in checkbox_states.items() if value]
                st.write("You selected:", selected_additional_fields)

        # Add genome information
        st.subheader("Add Genome Information")
        genome_name = taxon_id = version = genome_url = gff_url = None
        st.write("Add Reference Genome Information")
        genome_name = st.text_input(
            "Name:", help='Name of the genome.')
        taxon_id = st.text_input(
            "Taxon ID:", help='The NCBI taxonomy number.')
        version = st.text_input(
            "Version:", help='The genome version.')
        genome_url = st.text_input(
            "URL:", help='A link to the where this genome file could be downloaded')
        gff_url = st.text_input(
            "GFF URL (Optional):", help='A link to the where this genome’s annotation file could be downloaded')

        # Data Transformation
        if panel_ID:
            if all([genome_name, taxon_id, version, genome_url]):
                st.subheader("Transform Data")
                if st.button("Transform Data"):
                    genome_info = {
                        "name": genome_name,
                        "taxon_id": taxon_id,
                        "url": genome_url,
                        "version": version,
                    }
                    if gff_url:
                        genome_info["gff_url"] = gff_url
                    transformed_df = transform_panel_info(
                        df, panel_ID, field_mapping, genome_info, selected_additional_fields)

                    # Convert the dictionary to a JSON string
                    json_data = json.dumps(transformed_df, indent=4)
                    # if st.button("Save Panel"):
                    st.session_state["panel_info"] = transformed_df
                    try:
                        save_panel(panel_ID, transformed_df)
                        st.success(f"Panel '{panel_ID}' has been saved!")
                    except Exception as e:
                        st.error(f"Error saving panel: {e}")

# Display the current panel information
if "panel_info" in st.session_state:
    st.write("Current Panel Information:",)
    st.json(st.session_state["panel_info"])
