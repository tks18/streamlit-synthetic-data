import pandas as pd


def apply_seasonal(df: pd.DataFrame, column: str, month_multipliers: dict, date_col='Date'):
    df = df.copy()
    if date_col not in df.columns or column not in df.columns:
        return df
    tmp_date = pd.to_datetime(df[date_col], errors='coerce')
    if pd.api.types.is_datetime64_any_dtype(tmp_date):
        # Ensure keys in month_multipliers are strings for reliable lookup
        month_multipliers_str_keys = {
            str(k): v for k, v in month_multipliers.items()}
        multipliers = tmp_date.dt.month.astype(str).map(
            month_multipliers_str_keys).fillna(1.0).astype(float)
        df[column] = df[column] * multipliers
    return df
