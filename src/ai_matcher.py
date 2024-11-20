from fuzzywuzzy import process
# from rapidfuzz import process


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
    # elif method == "ai":
    #     if not api_key:
    #         raise ValueError("API key is required for AI-based matching.")
    #     return ai_match_fields(field_names, target_schema, api_key)
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
    # used_target_fields = set()  # To track which target schema fields have been used
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


# def ai_match_fields(field_names, target_schema, api_key):
#     """
#     Matches field names to the target schema using AI.

#     Args:
#         field_names (list): List of column names to be matched.
#         target_schema (list): List of standard schema fields to match against.
#         api_key (str): OpenAI API key.

#     Returns:
#         dict: A dictionary mapping each field name to the best-matched schema field.
#     """
#     import openai

#     openai.api_key = api_key
#     system_message = (
#         "You are an assistant that helps map column names to a standard schema. "
#         "Given a list of column names and a target schema, match each column to the most relevant schema field."
#     )
#     user_message = (
#         f"Columns: {field_names}\n"
#         f"Target Schema: {target_schema}\n\n"
#         "Provide the result as a JSON object where each column name is a key, "
#         "and the value is the most relevant field from the schema."
#     )

#     try:
#         response = openai.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": system_message},
#                 {"role": "user", "content": user_message},
#             ],
#             max_tokens=3000,
#             temperature=0.3,
#         )
#         # Extract and evaluate the JSON response
#         matches = eval(response['choices'][0]['message']['content'].strip())
#         return matches
#     except Exception as e:
#         raise RuntimeError(f"AI matching failed: {e}")

# def fuzzy_match_fields(field_names, target_schema):
#     """
#     Matches field names to the target schema using fuzzy matching.

#     Args:
#         field_names (list): List of column names to be matched.
#         target_schema (list): List of standard schema fields to match against.

#     Returns:
#         dict: A dictionary mapping each field name to the best-matched schema field.
#     """
#     matches = {}
#     for field in field_names:
#         best_match = process.extractOne(field, target_schema)
#         matches[field] = best_match[0]  # Get the best matching schema field
#     return matches
