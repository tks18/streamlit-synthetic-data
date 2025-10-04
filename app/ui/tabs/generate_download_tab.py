import streamlit as st
from streamlit import delta_generator
import zipfile
import pandas as pd
import io

from app.helpers.general import set_seed
from app.helpers.config import DEFAULT_REGIONS
from app.helpers.pd import apply_custom_columns_vectorized
import app.generators as generators
import app.mods as scenarios


def render_generate_download_tab(tab_obj: delta_generator.DeltaGenerator, DATASET_OPTIONS, seed, faker_locale, country_choices, products, start_date, end_date, freq, industry, outlier_freq, outlier_mag):
    with tab_obj:
        st.header('Generate & Download')
        st.sidebar.markdown('---')
        st.sidebar.header('Generate Datasets')
        datasets_to_gen = st.sidebar.multiselect(
            'Datasets to generate', DATASET_OPTIONS, default=DATASET_OPTIONS)

        if st.sidebar.button('🚀 Generate Data Now', use_container_width=True, type="primary"):
            with st.spinner('Generating datasets... this may take a moment.'):
                faker = set_seed(seed, locale=faker_locale)
                generated = {}

                # Masters first
                cust_df = generators.generate_customer_master(
                    300, country_choices, DEFAULT_REGIONS, faker, seed)
                if 'Customer_Master' in datasets_to_gen:
                    generated['Customer_Master'] = apply_custom_columns_vectorized(
                        cust_df.copy(), 'Customer_Master')

                vend_df = generators.generate_vendor_master(
                    200, country_choices, DEFAULT_REGIONS, faker, seed+1)
                if 'Vendor_Master' in datasets_to_gen:
                    generated['Vendor_Master'] = apply_custom_columns_vectorized(
                        vend_df.copy(), 'Vendor_Master')

                # Transactions that depend on masters
                if 'Revenue_Invoices' in datasets_to_gen:
                    rev = generators.generate_revenue_invoices(
                        products, start_date, end_date, freq, cust_df, industry, faker, seed)
                    rev = scenarios.inject_outliers_vectorized(
                        rev, ['InvoiceAmount'], freq=outlier_freq, mag=outlier_mag, seed=seed)
                    generated['Revenue_Invoices'] = apply_custom_columns_vectorized(
                        rev, 'Revenue_Invoices')

                if 'Debtors_Aggregated' in datasets_to_gen:
                    inv_src = generated.get('Revenue_Invoices', pd.DataFrame())
                    debt = generators.generate_debtors_from_invoices(
                        inv_src, freq='M')
                    debt = scenarios.inject_outliers_vectorized(
                        debt, ['ClosingBalance'], freq=outlier_freq, mag=outlier_mag, seed=seed)
                    generated['Debtors_Aggregated'] = apply_custom_columns_vectorized(
                        debt, 'Debtors_Aggregated')

                if 'Purchases' in datasets_to_gen:
                    purch = generators.generate_purchases(
                        vend_df, products, start_date, end_date, freq, industry, faker, seed+3)
                    purch = scenarios.inject_outliers_vectorized(
                        purch, ['PurchaseAmount'], freq=outlier_freq, mag=outlier_mag, seed=seed+3)
                    generated['Purchases'] = apply_custom_columns_vectorized(
                        purch, 'Purchases')

                # Other datasets
                if 'PPE_Register' in datasets_to_gen:
                    ppe = generators.generate_ppe_register(
                        300, start_date, end_date, country_choices, DEFAULT_REGIONS, faker, seed+2)
                    ppe = scenarios.inject_outliers_vectorized(
                        ppe, ['Cost'], freq=outlier_freq, mag=outlier_mag, seed=seed+2)
                    generated['PPE_Register'] = apply_custom_columns_vectorized(
                        ppe, 'PPE_Register')

                if 'Inventory' in datasets_to_gen:
                    inv = generators.generate_inventory_snapshots(
                        products, start_date, end_date, freq, seed+4)
                    inv = scenarios.inject_outliers_vectorized(
                        inv, ['InventoryValue'], freq=outlier_freq, mag=outlier_mag, seed=seed+4)
                    generated['Inventory'] = apply_custom_columns_vectorized(
                        inv, 'Inventory')

                if 'Operational' in datasets_to_gen:
                    op = generators.generate_operational_dataset(
                        industry, start_date, end_date, freq, None, country_choices, DEFAULT_REGIONS, faker, seed+10)
                    generated['Operational'] = apply_custom_columns_vectorized(
                        op, 'Operational')

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
