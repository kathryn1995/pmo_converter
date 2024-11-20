import streamlit as st
import pandas as pd
import json
from collections import Counter
from src.data_loader import load_csv
from src.ai_matcher import auto_match_fields
from src.transformer import transform_data
from src.format_page import render_header

render_header()
st.subheader("Microhaplotype Information Converter", divider="gray")


def check_for_duplicates(field_mapping):
    """
    Checks if there are any duplicate values in the dictionary.

    Args:
        field_mapping (dict): A dictionary mapping input field names to target schema fields.

    Returns:
        bool: True if no duplicates are found. Raises a ValueError if duplicates exist.
    """
    # Extract the values (target schema fields) from the dictionary
    counts = Counter(list(field_mapping.values()))
    duplicates = {item for item, count in counts.items() if count > 1}
    # Check for duplicates by comparing the length of the list to the length of the set
    if duplicates:
        raise ValueError(
            f"Duplicate target schema fields found: {duplicates}")

    return True


def interactive_field_mapping(field_mapping, df_columns):
    updated_mapping = {}

    for field, suggested_match in field_mapping.items():
        # Use streamlit widgets to allow the user to select a match from df columns
        if isinstance(suggested_match, list):  # For multiple possible matches
            updated_mapping[field] = st.selectbox(
                f"Select match for {field}",
                options=df_columns,
                index=df_columns.index(
                    suggested_match[0]) if suggested_match else 0
            )
        else:
            updated_mapping[field] = st.selectbox(
                f"Modify match for {field}",
                options=df_columns,
                index=df_columns.index(
                    suggested_match) if suggested_match else 0
            )

    return updated_mapping


def field_mapping_json_to_table(mapping):
    data = [{"PMO Field": key, "Input Field": value}
            for key, value in mapping.items()]
    df = pd.DataFrame(data)
    return df


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
    target_schema = ["sampleID", "locus", "asv", "reads"]
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

    # Interactive Mapping
    interactive_field_mapping_on = st.toggle("Manually Alter Field Mapping")
    if interactive_field_mapping_on:
        updated_mapping = interactive_field_mapping(field_mapping, df_columns)
        # Display the updated mapping after user interaction
        st.write("Updated Field Mapping:")
        st.dataframe(field_mapping_json_to_table(updated_mapping))

        check_for_duplicates(updated_mapping)
    # TODO: Add in optional fields
    # TODO: Add in option to select their own fields to add in
    # TODO: Add in bioinfo ID
    # Data Transformation
    st.subheader("Transform Data")
    if st.button("Transform Data"):
        transformed_df = transform_data(df, 'bioinfo', field_mapping)
        st.write("Transformed Data:")
        # st.write(transformed_df)
        # Convert the dictionary to a JSON string
        json_data = json.dumps(transformed_df, indent=4)

        # Add a download button for JSON
        st.download_button(
            "Download Converted Data",
            json_data,
            "panel_info_bioinfoid.json",
            "application/json"
        )

# TODO: use pmotools instead of copying code
