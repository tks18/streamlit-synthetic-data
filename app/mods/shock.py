import pandas as pd


def apply_shock(df: pd.DataFrame, column: str, start_date: str, end_date: str, magnitude: float, mode='multiplier', date_col='Date'):
    df = df.copy()
    if date_col not in df.columns or column not in df.columns:
        return df
    tmp_date = pd.to_datetime(df[date_col], errors='coerce')
    mask = (tmp_date >= pd.to_datetime(start_date)) & (
        tmp_date <= pd.to_datetime(end_date))
    if mode == 'multiplier':
        df.loc[mask, column] *= magnitude
    else:  # additive
        df.loc[mask, column] += magnitude
    return df
