import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from credit_reports import create_country_report_tab
from report_utils import create_fund_report_tab

# Set page configuration
st.set_page_config(layout="wide")

# Custom CSS for background and text colors
st.markdown(
    """
    <style>
    .stApp {
        background-color: #1f1f1f;
        color: #ffffff;
        max-width: 2000px;
        margin: auto;
        padding-left: 4rem;
        padding-right: 4rem;
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    .reportColumn {
        width: 60% !important;
    }
    .chartColumn {
        width: 40% !important;
    }
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
        margin-top: 10px;
        margin-bottom: 30px.
    }
    .data-table th, .data-table td {
        border: 1px solid #ddd;
        padding: 4px;
        text-align: center.
    }
    .data-table th {
        background-color: #1f1f1f;
        color: white.
    }
    .data-table td {
        background-color: white.
        color: black.
    }
    .reportText {
        color: white.
        word-wrap: break-word.
        white-space: normal.
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Set up color palette
color_palette = [
    "#FFA500",  # Bright Orange
    "#007FFF",  # Azure Blue
    "#DC143C",  # Cherry Red
    "#39FF14",  # Electric Lime Green
    "#00FFFF",  # Cyan
    "#DA70D6"   # Vivid Purple
]

# Available reports
available_reports = {
    "Israel": "Israel",
    "Qatar": "Qatar",
    "Mexico": "Mexico",
    "Saudi Arabia": "Saudi Arabia",
    "Shin Kong Emerging Wealthy Nations Bond Fund": "SKEWNBF",
    "Shin Kong Environmental Sustainability Bond Fund": "SKESBF"
}

# Initialize session state to manage selected reports
if "selected_reports" not in st.session_state:
    st.session_state.selected_reports = []

if "dropdown_reports" not in st.session_state:
    st.session_state.dropdown_reports = []

if "last_selected" not in st.session_state:
    st.session_state.last_selected = None

# Function to display the chatbot on the right side and handle report selection
def display_chatbot():
    with st.sidebar.expander("Chatbot", expanded=True):
        user_input = st.text_input("Ask me anything:", "")
        
        if user_input:
            for report_name, tab_name in available_reports.items():
                if report_name.lower() in user_input.lower():
                    if tab_name not in st.session_state.selected_reports:
                        st.session_state.selected_reports.append(tab_name)
                    if tab_name not in st.session_state.dropdown_reports:
                        st.session_state.dropdown_reports.insert(0, tab_name)
                    st.session_state.last_selected = tab_name
                    break
            else:
                st.write("Sorry, I don't recognize that request.")

# Display the chatbot on the right side
display_chatbot()

# Show checkboxes only if reports have been requested
if st.session_state.selected_reports:
    with st.sidebar.expander("Select Reports to Display", expanded=True):
        updated_dropdown_reports = []
        for report_name, tab_name in available_reports.items():
            if tab_name in st.session_state.selected_reports:
                checked = st.checkbox(report_name, value=tab_name in st.session_state.dropdown_reports)
                if checked:
                    updated_dropdown_reports.append(tab_name)

        # Update dropdown reports after processing all checkboxes
        st.session_state.dropdown_reports = updated_dropdown_reports

        # Ensure the last_selected is still valid
        if st.session_state.dropdown_reports:
            if st.session_state.last_selected not in st.session_state.dropdown_reports:
                st.session_state.last_selected = st.session_state.dropdown_reports[0]

# If there are reports selected for the dropdown, show the dropdown
if st.session_state.dropdown_reports:
    selected_report = st.selectbox(
        "Select a report to view:",
        st.session_state.dropdown_reports,
        index=st.session_state.dropdown_reports.index(st.session_state.last_selected)  # Automatically select the last requested report
    )

    # Display the content of the selected report
    if selected_report == "Israel":
        create_country_report_tab("Israel", color_palette)

    elif selected_report == "Qatar":
        create_country_report_tab("Qatar", color_palette)

    elif selected_report == "Mexico":
        create_country_report_tab("Mexico", color_palette)

    elif selected_report == "Saudi Arabia":
        create_country_report_tab("Saudi Arabia", color_palette)

    elif selected_report == "SKEWNBF":
        create_fund_report_tab("Shin Kong Emerging Wealthy Nations Bond Fund", color_palette)

    elif selected_report == "SKESBF":
        create_fund_report_tab("Shin Kong Environmental Sustainability Bond Fund", color_palette)


