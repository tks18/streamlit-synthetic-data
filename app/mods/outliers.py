import numpy as np


def inject_outliers_vectorized(df, cols, freq=0.01, mag=3.0, method="multiplier", seed=None):
    if seed is not None:
        np.random.seed(seed)
    df = df.copy()
    n = len(df)
    if n == 0:
        return df
    k = max(1, int(np.floor(freq * n)))
    idx = np.random.choice(df.index, size=k, replace=False)
    factors = np.random.uniform(mag, mag * 1.5, size=k)
    for col in cols:
        if col not in df.columns:
            continue
        if method == "multiplier":
            df.loc[idx, col] = df.loc[idx, col] * factors
        else:  # additive
            df.loc[idx, col] = df.loc[idx, col] + \
                (df.loc[idx, col].abs().mean() * factors)
    return df
