import streamlit as st
import pandas as pd
import numpy as np

from app.helpers.safe_eval import vectorized_eval, rowwise_safe_eval


def get_dataset_config(ds):
    return st.session_state.key_custom_columns.get(ds, [])


def set_dataset_config(ds, ordered_list):
    st.session_state.key_custom_columns[ds] = ordered_list


def add_or_update_column(ds, col_name, col_cfg):
    lst = get_dataset_config(ds)
    for i, (c, _) in enumerate(lst):
        if c == col_name:
            lst[i] = (col_name, col_cfg)
            set_dataset_config(ds, lst)
            return
    lst.append((col_name, col_cfg))
    set_dataset_config(ds, lst)


def delete_column(ds, col_name):
    lst = [x for x in get_dataset_config(ds) if x[0] != col_name]
    set_dataset_config(ds, lst)


def move_column(ds, col_name, direction):
    lst = get_dataset_config(ds)
    for i, (c, _) in enumerate(lst):
        if c == col_name:
            if direction == 'up' and i > 0:
                lst[i-1], lst[i] = lst[i], lst[i-1]
            elif direction == 'down' and i < len(lst)-1:
                lst[i+1], lst[i] = lst[i], lst[i+1]
            break
    set_dataset_config(ds, lst)


def apply_custom_columns_vectorized(df: pd.DataFrame, ds_name: str):
    """Applies custom columns from session state to a dataframe."""
    cfg_list = get_dataset_config(ds_name)
    if not cfg_list or df.empty:
        return df

    df = df.copy().reset_index(drop=True)
    for col, col_cfg in cfg_list:
        ctype = col_cfg.get('type')
        if ctype == 'choice':
            opts = col_cfg.get('options', [])
            df[col] = np.random.choice(opts, size=len(df)) if opts else np.nan
        elif ctype == 'range':
            mn, mx = float(col_cfg.get('min', 0)), float(col_cfg.get('max', 1))
            df[col] = np.random.uniform(mn, mx, size=len(df))
        elif ctype == 'formula':
            expr = col_cfg.get('expr', '')
            if not expr:
                df[col] = np.nan
                continue
            try:  # Attempt vectorized evaluation
                df[col] = vectorized_eval(expr, df)
            except Exception as e:  # Fallback to slower row-wise evaluation
                st.warning(
                    f"Formula for '{col}' failed vectorized eval: {e}. Falling back to row-wise.")
                vals = [rowwise_safe_eval(
                    expr, r) if expr else np.nan for r in df.to_dict(orient='records')]
                df[col] = vals
        else:
            df[col] = np.nan
    return df
