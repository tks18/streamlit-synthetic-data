import numpy as np


def inject_outliers_vectorized(df, cols, freq=0.01, mag=3.0, method="multiplier", seed=None):
    if seed is not None:
        np.random.seed(seed)
    df = df.copy()
    n = len(df)
    if n == 0 or len(cols) == 0:
        return df

    # number of outliers
    k = max(1, int(np.floor(freq * n)))
    idx = np.random.choice(df.index, size=k, replace=False)

    for col in cols:
        if col not in df.columns:
            continue
        series = df[col]

        # skip non-numeric columns
        if not np.issubdtype(series.dtype, np.number):
            continue

        # Generate outlier factors
        factors = np.random.uniform(mag, mag * 1.5, size=k)
        # Randomly decide positive or negative outliers
        signs = np.random.choice([-1, 1], size=k)

        if method == "multiplier":
            outliers = series.loc[idx] * (1 + signs * (factors - 1))
            # Prevent negative values if original data is non-negative
            if (series >= 0).all():
                outliers = outliers.clip(lower=0)
        else:  # additive
            mean_abs = series.abs().mean()
            outliers = series.loc[idx] + signs * factors * mean_abs
            if (series >= 0).all():
                outliers = outliers.clip(lower=0)

        # Preserve integer type if original column is int
        if np.issubdtype(series.dtype, np.integer):
            outliers = outliers.round().astype(series.dtype)

        df.loc[idx, col] = outliers

    return df
