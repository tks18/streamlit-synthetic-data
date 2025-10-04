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

    # --- Main Layout: Tabs ---
    DATASET_OPTIONS = ['Revenue_Invoices', 'Debtors_Aggregated', 'PPE_Register',
                       'Purchases', 'Inventory', 'Customer_Master', 'Vendor_Master', 'Operational']

    tab1, tab2, tab3 = st.tabs(
        ['Custom Columns', 'Scenarios', 'Generate & Download'])

    render_custom_columns_tab(tab1, DATASET_OPTIONS)
    render_scenario_simulator_tab(tab2, DATASET_OPTIONS, config['seed'])
    render_generate_download_tab(tab3, DATASET_OPTIONS, config['seed'], config['faker_locale'], config['country_choices'], config['products'],
                                 config['start_date'], config['end_date'], config['freq'], config['industry'], config['outlier_freq'], config['outlier_mag'])
