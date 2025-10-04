import pandas as pd
import numpy as np


def apply_correlation(df: pd.DataFrame, source_col: str, target_col: str, coef: float, noise_factor=0.1):
    df = df.copy()
    if source_col not in df.columns or target_col not in df.columns:
        return df
    # Normalize source to prevent scale issues and add some noise for realism
    source_norm = (df[source_col] - df[source_col].mean()) / \
        df[source_col].std()
    noise = np.random.normal(0, df[target_col].std() * noise_factor, len(df))
    df[target_col] = df[target_col] + \
        (coef * source_norm * df[target_col].std()) + noise
    return df
