import streamlit as st
import pandas as pd
import json
from src.data_loader import load_csv
from src.field_matcher import auto_match_fields, check_for_duplicates, interactive_field_mapping, field_mapping_json_to_table
from src.transformer import transform_panel_info
from src.format_page import render_header

render_header()
st.subheader("Panel Information Converter", divider="gray")

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
        api_key = st.text_input("Enter OpenAI API Key:", type="password")

    df_columns = df.columns.tolist()
    field_mapping, unused_field_names = auto_match_fields(
        df.columns.tolist(),
        target_schema,
        method=method.lower(),
        api_key=api_key
    )
    st.write("Suggested Field Mapping:")
    st.dataframe(field_mapping_json_to_table(field_mapping))
    #              genome_info: dict,
    #              forward_primers_start_col: int | None = None,
    #              forward_primers_end_col: int | None = None,
    #              reverse_primers_start_col: int | None = None,
    #              reverse_primers_end_col: int | None = None,
    #              insert_start_col: int | None = None,
    #              insert_end_col: int | None = None,
    #              chrom_col: str | None = None,
    #              strand_col: str | None = None,
    #              gene_id_col: str | None = None,
    #              target_type_col: str | None = None,
    # Interactive Mapping
    interactive_field_mapping_on = st.toggle("Manually Alter Field Mapping")
    if interactive_field_mapping_on:
        updated_mapping = interactive_field_mapping(field_mapping, df_columns)
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
            st.write("Select the extra columns you would like to include:")
            # Dynamically create a checkbox for each item in the list
            for item in unused_field_names:
                # Add checkbox and store its state in the dictionary
                checkbox_states[item] = st.checkbox(label=item)

            # Display selected items
            selected_additional_fields = [key for key,
                                          value in checkbox_states.items() if value]
            st.write("You selected:", selected_additional_fields)

    st.subheader("Panel ID")
    panel_ID = st.text_input(
        "Enter panel ID:", help='Identifier for the panel.')

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

                st.write("Transformed Data:")
                # Convert the dictionary to a JSON string
                json_data = json.dumps(transformed_df, indent=4)

                # Add a download button for JSON
                st.download_button(
                    "Download Converted Data",
                    json_data,
                    "/Users/kmurie/Documents/git_projects/pmo_converter/data/panel_info.json",
                    "application/json"
                )

# TODO: use pmotools instead of copying code
