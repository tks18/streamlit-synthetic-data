import streamlit as st
from streamlit import delta_generator
import zipfile
import pandas as pd
import io

from app.helpers.general import set_seed
from app.helpers.config import DEFAULT_REGIONS
from app.helpers.pd import apply_custom_columns_vectorized
from app.generators import generator_config
from app.helpers.state import get_state_config
import app.mods as scenarios


def render_generate_download_tab(tab_obj: delta_generator.DeltaGenerator):
    with tab_obj:
        state_config = get_state_config()

        seed = state_config["seed"]
        faker_locale = state_config["faker_locale"]

        st.header('Generate & Download')
        st.sidebar.markdown('---')
        st.sidebar.header('Generate Datasets')
        datasets_to_gen = st.sidebar.multiselect(
            'Datasets to generate', list(generator_config.keys()), default=list(generator_config.keys()))

        if st.sidebar.button('🚀 Generate Data Now', use_container_width=True, type="primary"):
            with st.spinner('Generating datasets... this may take a moment.'):
                faker = set_seed(seed, locale=faker_locale)
                generated = {}

                for dskey, ds_generator in generator_config.items():
                    if dskey in datasets_to_gen:
                        df = ds_generator(
                            state_config, faker, generated)
                        generated[dskey] = df
                        generated[dskey] = apply_custom_columns_vectorized(
                            df, dskey)

                # Apply scenarios
                for sc in st.session_state.key_scenarios:
                    target_ds = sc.get('target_dataset')
                    if target_ds in generated:
                        df = generated[target_ds]
                        if sc['type'] == 'shock':
                            df = scenarios.apply_shock(
                                df, sc['target_column'], sc['start'], sc['end'], sc['magnitude'], sc['mode'])
                        elif sc['type'] == 'seasonal':
                            df = scenarios.apply_seasonal(
                                df, sc['target_column'], sc['month_multipliers'])
                        elif sc['type'] == 'fraud_outlier':
                            df = scenarios.inject_fraud_outliers(df, sc['target_column'], sc.get(
                                'pct', 0.01), sc.get('multiplier', 5.0), seed=sc.get('seed'))
                        elif sc['type'] == 'correlation':
                            df = scenarios.apply_correlation(
                                df, sc['source_col'], sc['target_column'], sc.get('coef', 0.0))
                        generated[target_ds] = df
                    else:
                        st.warning(
                            f"Scenario '{sc.get('name')}' targets '{target_ds}', which was not generated. Skipping.")

                st.session_state.generated_data = generated
                st.success(
                    'Data generation complete! View previews and download below.')
                st.rerun()

        if 'generated_data' in st.session_state and st.session_state.generated_data:
            st.markdown('### Previews & Downloads')
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                for name, df in st.session_state.generated_data.items():
                    st.subheader(f"`{name}` — {len(df):,} rows")
                    st.dataframe(df.head(50))
                    st.download_button(f'⬇️ Download {name}', df.to_csv(index=False).encode(
                        'utf-8'), file_name=f"{name}.csv", use_container_width=True)
                    csv = df.to_csv(index=False).encode('utf-8')
                    zf.writestr(f"{name}.csv", csv)

            zip_buffer.seek(0)
            st.download_button('⬇️ Download ALL as ZIP', zip_buffer.getvalue(
            ), file_name='synthetic_datasets.zip', use_container_width=True)
