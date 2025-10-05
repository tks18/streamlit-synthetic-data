import streamlit as st
from streamlit import delta_generator
import json
from streamlit_sortables import sort_items

from app.helpers.pd import add_or_update_column, delete_column, get_dataset_config, set_dataset_config
from app.generators import generator_config


def render_custom_columns_tab(tab_obj: delta_generator.DeltaGenerator):
    with tab_obj:
        st.header('Custom Columns')
        ds_to_edit = st.selectbox('Dataset to customize',
                                  options=list(generator_config.keys()), key="ds_selector")

        lst = get_dataset_config(ds_to_edit)
        st.subheader(f'Custom Columns for `{ds_to_edit}`')

        if not lst:
            st.info(
                'No custom columns yet. Add one below or load a template from the sidebar.')
        else:
            st.info('Drag and drop the columns to reorder them.', icon="↕️")

            display_items = [
                f"{cname} || `{ccfg.get('type')}`" for cname, ccfg in lst]
            new_order_display = sort_items(display_items, direction='vertical')

            original_map = {f"{cname} || `{ccfg.get('type')}`": (
                cname, ccfg) for cname, ccfg in lst}
            new_ordered_list = [original_map[item]
                                for item in new_order_display]

            if new_ordered_list != lst:
                set_dataset_config(ds_to_edit, new_ordered_list)
                st.rerun()

            for i, (cname, ccfg) in enumerate(new_ordered_list):
                with st.container(border=True):
                    cols = st.columns([4, 1])
                    cols[0].markdown(
                        f"**{i+1}. {cname}** (`{ccfg.get('type')}`)")
                    cols[0].caption(json.dumps(ccfg))
                    if cols[1].button('Delete', key=f'del_{ds_to_edit}_{cname}', use_container_width=True):
                        delete_column(ds_to_edit, cname)
                        st.rerun()

        # --- ADD/UPDATE FORM ---
        st.markdown('---')
        st.subheader('Add / Update Column')
        col_type = st.selectbox(
            'Type', ['formula', 'range', 'choice'], key='new_col_type')
        with st.form('addcol', border=True):
            col_name = st.text_input('Column name')

            if col_type == 'formula':
                st.markdown(
                    'Use column names directly. Allowed modules: `np`, `math`, `random`, `pd`.')
                expr = st.text_area('Expression', 'np.log1p(InvoiceAmount)')
                col_config = {'type': 'formula', 'expr': expr}
            elif col_type == 'range':
                rmin, rmax = st.columns(2)
                min_val = rmin.number_input('Min', value=0.0)
                max_val = rmax.number_input('Max', value=1.0)
                col_config = {'type': 'range', 'min': float(
                    min_val), 'max': float(max_val)}
            else:  # choice
                options = st.text_area('Options (comma separated)', 'A, B, C')
                opts = [o.strip() for o in options.split(',') if o.strip()]
                col_config = {'type': 'choice', 'options': opts}

            if st.form_submit_button('Save Column'):
                if not col_name.strip():
                    st.error('Enter a column name')
                else:
                    add_or_update_column(
                        ds_to_edit, col_name.strip(), col_config)
                    st.success(
                        f"Saved column '{col_name}' to `{ds_to_edit}` config.")
                    st.rerun()
