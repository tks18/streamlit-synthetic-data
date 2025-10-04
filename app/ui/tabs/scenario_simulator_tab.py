import streamlit as st
from streamlit import delta_generator
import json


def render_scenario_simulator_tab(tab_obj: delta_generator.DeltaGenerator, DATASET_OPTIONS, seed):
    with tab_obj:
        st.header('Scenarios')
        st.info('Scenarios are applied in order during data generation.')

        st.subheader('Manage Scenarios')
        if not st.session_state.key_scenarios:
            st.write(
                'No scenarios configured. Add one below or load a profile from the sidebar.')

        for i, s in enumerate(st.session_state.key_scenarios):
            expander_title = f"**{i+1}. {s.get('name', 'Untitled')}** (`{s.get('type')}` on `{s.get('target_dataset')}.{s.get('target_column')}`)"
            with st.expander(expander_title):
                st.json(s)
                if st.button(f'Delete Scenario {i+1}', key=f'delscn{i}'):
                    st.session_state.key_scenarios.pop(i)
                    st.rerun()

        st.markdown('---')
        st.subheader('Add New Scenario')
        s_type = st.selectbox(
            'Type', ['shock', 'seasonal', 'fraud_outlier', 'correlation'])
        with st.form('add_scenario', border=True):
            s_name = st.text_input('Scenario name')
            s_target_ds = st.selectbox('Target dataset', DATASET_OPTIONS)
            s_target_col = st.text_input('Target column', 'InvoiceAmount')
            s_seed = int(st.number_input('Scenario Seed', value=seed))

            sc_details = {}
            if s_type == 'shock':
                c1, c2 = st.columns(2)
                s_start = c1.date_input('Start date')
                s_end = c2.date_input('End date')
                s_magnitude = st.number_input(
                    'Magnitude', value=0.7, format='%.3f')
                s_mode = st.selectbox('Mode', ['multiplier', 'additive'])
                sc_details = {'start': str(s_start), 'end': str(
                    s_end), 'magnitude': float(s_magnitude), 'mode': s_mode}
            elif s_type == 'seasonal':
                s_month_json = st.text_area(
                    'Month multipliers (JSON)', value='{"12": 1.5, "1": 1.2}')
                try:
                    sc_details = {
                        'month_multipliers': json.loads(s_month_json)}
                except json.JSONDecodeError:
                    st.error("Invalid JSON for month multipliers.")
                    sc_details = None
            elif s_type == 'fraud_outlier':
                c1, c2 = st.columns(2)
                s_pct = c1.number_input(
                    'Fraction of rows (0-1)', 0.0, 1.0, 0.01, 0.001, '%.4f')
                s_mult = c2.number_input(
                    'Outlier multiplier', 1.0, 100.0, 5.0, 0.5)
                sc_details = {'pct': float(s_pct), 'multiplier': float(s_mult)}
            elif s_type == 'correlation':
                c1, c2 = st.columns(2)
                s_source = c1.text_input('Source column', 'ProjectHours')
                s_coef = c2.number_input(
                    'Correlation coefficient (-1 to 1)', -1.0, 1.0, 0.6, 0.1)
                sc_details = {'source_col': s_source, 'coef': float(s_coef)}

            if st.form_submit_button('Add Scenario'):
                if sc_details is not None:
                    sc = {'name': s_name or f'scn_{s_type}', 'type': s_type,
                          'target_dataset': s_target_ds, 'target_column': s_target_col, 'seed': s_seed}
                    sc.update(sc_details)
                    st.session_state.key_scenarios.append(sc)
                    st.success('Scenario added.')
                    st.rerun()
