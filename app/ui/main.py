import streamlit as st

from app.helpers.config import APP_MAIN_TITLE, APP_TITLE
from app.helpers.profile import initialize_state_or_profile

from app.ui.sidebar import render_sidebar
from app.ui.tabs import render_custom_columns_tab, render_scenario_simulator_tab, render_generate_download_tab


def render_ui():
    initialize_state_or_profile()
    st.set_page_config(page_title=APP_MAIN_TITLE,
                       layout='wide', page_icon=':sparkles:')
    st.title(APP_MAIN_TITLE)
    st.subheader(APP_TITLE, divider=True)
    config = render_sidebar()

    tab1, tab2, tab3 = st.tabs(
        ['Custom Columns', 'Scenarios', 'Generate & Download'])

    render_custom_columns_tab(tab1)
    render_scenario_simulator_tab(tab2)
    render_generate_download_tab(tab3)
