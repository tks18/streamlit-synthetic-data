import streamlit as st
import os
import json

from app.helpers.config import INDUSTRY_KPIS, DEFAULT_REGIONS
from app.helpers.profile import save_profile, list_profiles, prepare_profile


def render_sidebar():
    # --- Sidebar ---
    with st.sidebar:
        st.header('Core Settings')
        industry = st.selectbox('Industry', list(
            INDUSTRY_KPIS.keys()), key='key_industry')
        products_str = INDUSTRY_KPIS.get(industry, {}).get(
            "products", ["Product A", "Product B"])
        st.session_state.key_products = products_str
        products = st.multiselect(
            'Products', options=products_str, accept_new_options=True, key='key_products')

        country_choices = st.multiselect('Country choices', options=list(
            DEFAULT_REGIONS.keys()), accept_new_options=True, key='key_countries')
        start_date = st.date_input(
            'Start Date', key='key_start_date')
        end_date = st.date_input(
            'End Date', key='key_end_date')
        freq = st.selectbox(
            'Frequency', ['ME', 'W', 'D'], help="ME=Month-end, W=Week-end, D=Day", key='key_freq')
        seed = int(st.number_input('Seed', step=1, key='key_seed'))
        faker_locale = st.selectbox(
            'Faker locale', ['en_US', 'en_IN', 'en_GB', 'fr_FR'], key='key_faker_locale')
        st.markdown("---")
        st.header('Outliers')
        outlier_freq = st.slider('Outlier Frequency', 0.0,
                                 0.2, key='key_outlier_freq')
        outlier_mag = st.slider('Outlier Magnitude', 1.5,
                                8.0, key='key_outlier_mag')
        st.markdown('---')
        st.header('Profiles')
        new_profile_name = st.text_input('Save current config as profile', '')
        if st.button('Save Profile'):
            if new_profile_name.strip():
                p = save_profile(new_profile_name.strip())
                st.success(f'Saved profile -> {os.path.basename(p)}')
                st.session_state.profiles_cache = list_profiles()
                st.rerun()
            else:
                st.error('Enter a profile name')

        prof_sel = st.selectbox('Load profile from disk', options=[
                                ''] + st.session_state.profiles_cache)
        if st.button('Load Profile'):
            if prof_sel:
                st.session_state["load_profile"] = prof_sel
                st.success(f'Loaded {prof_sel}')
                st.rerun()
            else:
                st.error('Select a profile file')

        if st.button('Prepare Profile for Download'):
            profile_dump = prepare_profile()
            st.download_button('Download Profile',
                               json.dumps(profile_dump), 'profile_dump.json', 'application/json')

        st.markdown('---')
        st.header('Other Customizations')
        total_customers = int(st.number_input(
            'Total Customers', step=1, key='key_total_customers'))
        total_vendors = int(st.number_input(
            'Total Vendors', step=1, key='key_total_vendors'))
        total_assets = int(st.number_input(
            'Total Assets', step=1, key='key_total_assets'))

        return {
            'industry': industry,
            'products': products,
            'country_choices': country_choices,
            'start_date': start_date,
            'end_date': end_date,
            'freq': freq,
            'seed': seed,
            'faker_locale': faker_locale,
            'outlier_freq': outlier_freq,
            'outlier_mag': outlier_mag,
            'total_customers': total_customers,
            'total_vendors': total_vendors,
            'total_assets': total_assets
        }
