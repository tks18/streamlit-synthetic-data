import pandas as pd
import numpy as np


def apply_correlation(df: pd.DataFrame, source_col: str, target_col: str, coef: float, noise_factor=0.1, seed=None):
    if seed is not None:
        np.random.seed(seed)

    df = df.copy()
    if source_col not in df.columns or target_col not in df.columns:
        return df

    # skip non-numeric columns
    if not (np.issubdtype(np.array(df[source_col]).dtype, np.number) and np.issubdtype(np.array(df[target_col]).dtype, np.number)):
        return df

    # normalize source
    source = df[source_col]
    target = df[target_col]

    source_std = source.std()
    target_std = target.std()
    if source_std == 0 or target_std == 0:
        return df  # can't correlate constant series

    source_norm = (source - source.mean()) / source_std

    # noise scaled by target std
    noise = np.random.normal(0, target_std * noise_factor, len(df))

    # apply correlation
    correlated = target + coef * source_norm * target_std + noise

    # preserve integer type if original column is int
    if np.issubdtype(np.array(target).dtype, np.integer):
        correlated = correlated.round().astype(target.dtype)

    df[target_col] = correlated

    return df
