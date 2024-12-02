import streamlit as st
import json
import os
from src.data_loader import load_csv
from src.field_matcher import auto_match_fields, check_for_duplicates, interactive_field_mapping, field_mapping_json_to_table
from src.transformer import transform_mhap_info
from src.format_page import render_header

current_directory = os.getcwd()  # Get the current working directory
SAVE_DIR = os.path.join(current_directory, "PMO")
os.makedirs(SAVE_DIR, exist_ok=True)

render_header()
st.subheader("Create Final PMO", divider="gray")

st.subheader("Components")
# PANEL INFO
if "panel_info" in st.session_state:
    panel_info = json.loads(st.session_state["panel_info"])
    panel_id = panel_info["panel_info"].keys()
    st.write("Current Panel Information:", panel_id)
else:
    st.error(
        "No panel information found. Please go to the Panel Information tab before proceeding.")

# MICROHAPLOTYPE DATA
if "mhap_data" in st.session_state:
    mhap_data = json.loads(st.session_state["mhap_data"])
    bioinfo_id = mhap_data["microhaplotypes_detected"].keys()
    st.write("Current Microhaplotype Information from bioinformatics run:", bioinfo_id)
else:
    st.error(
        "No microhaplotype information found. Please go to the Microhaplotype Information tab before proceeding.")

# SPECIMEN INFO
if "specimen_info" in st.session_state:
    st.write("Current specimen info:",)
    st.write(json.loads(st.session_state["mhap_data"])[
             "microhaplotypes_detected"].keys())
else:
    st.error(
        "No specimen information found. Please go to the Specimen Information tab before proceeding.")

# MERGE DATA
st.subheader("Merge Components to Final PMO")
if st.button("Merge Data"):
    with open(os.path.join(SAVE_DIR, f"{panel_id}_{bioinfo_id}.json"), "w") as f:
        json.dump(panel_info, f)
        json.dump(mhap_data, f)
    st.success(f"Your PMO has been saved!")
