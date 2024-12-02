from fuzzywuzzy import process
from collections import Counter
import pandas as pd
import streamlit as st


def auto_match_fields(field_names, target_schema, method="fuzzy", api_key=None):
    """
    Matches column names to a target schema using fuzzy matching or AI.

    Args:
        field_names (list): List of column names to be matched.
        target_schema (list): List of standard schema fields to match against.
        method (str): Matching method, either "fuzzy" or "ai".
        api_key (str, optional): OpenAI API key (required for AI matching).

    Returns:
        dict: A dictionary mapping each field name to the best-matched schema field.
    """
    if method == "fuzzy":
        return fuzzy_match_fields(field_names, target_schema)
    # TODO: Make the AI work
    elif method == "ai":
        if not api_key:
            raise ValueError("API key is required for AI-based matching.")
        return ai_match_fields(field_names, target_schema, api_key)
    else:
        raise ValueError("Invalid method. Choose 'fuzzy' or 'ai'.")


def fuzzy_match_fields(field_names, target_schema):
    """
    Matches field names to the target schema using fuzzy matching, ensuring 
    that each target schema field is only matched to one field name.

    Args:
        field_names (list): List of column names to be matched.
        target_schema (list): List of standard schema fields to match against.

    Returns:
        dict: A dictionary mapping each field name to the best-matched schema field.
        list: A list of unused field names that could not be matched.
    """
    matches = {}
    unused_field_names = []  # To store any unused field names

    for field in field_names:
        # TODO: change this so it's not dependent on order. Maximise across scores.
        best_match = process.extractOne(field, target_schema)
        best_match_field = best_match[0]

        # Check if the best match has already been used
        if best_match_field not in matches.keys():
            matches[best_match_field] = field
        else:
            unused_field_names.append(field)

    return matches, unused_field_names


def ai_match_fields(field_names, target_schema, api_key):
    """
    Matches field names to the target schema using AI.

    Args:
        field_names (list): List of column names to be matched.
        target_schema (list): List of standard schema fields to match against.
        api_key (str): OpenAI API key.

    Returns:
        dict: A dictionary mapping each field name to the best-matched schema field.
    """
    import openai

    openai.api_key = api_key
    system_message = (
        "You are an assistant that helps map column names to a standard schema. "
        "Given a list of column names and a target schema, match each column to the most relevant schema field."
    )
    user_message = (
        f"Columns: {field_names}\n"
        f"Target Schema: {target_schema}\n\n"
        "Provide the result as a JSON object where each column name is a key, "
        "and the value is the most relevant field from the schema."
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            max_tokens=3000,
            temperature=0.3,
        )
        # Extract and evaluate the JSON response
        matches = eval(response['choices'][0]['message']['content'].strip())
        return matches
    except Exception as e:
        raise RuntimeError(f"AI matching failed: {e}")


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
