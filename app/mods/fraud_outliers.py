import pandas as pd
import numpy as np


def inject_fraud_outliers(df: pd.DataFrame, column: str, pct: float, multiplier: float, seed=None):
    df = df.copy()
    if seed is not None:
        np.random.seed(seed)
    n = len(df)
    k = max(1, int(np.floor(pct * n)))
    if column not in df.columns or n == 0:
        return df
    idx = np.random.choice(df.index, size=k, replace=False)
    df.loc[idx, column] = df.loc[idx, column] * multiplier
    return df
