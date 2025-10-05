from typing import Dict
from faker import Faker
import pandas as pd
import numpy as np

from app.mods import inject_outliers_vectorized
from app.types import TAppStateConfig


def generate_debtors_from_invoices(state_config: TAppStateConfig, faker: Faker = Faker(), generated: Dict[str, pd.DataFrame] = {}):
    seed = state_config["seed"]
    outlier_freq = state_config["outlier_frequency"]
    outlier_mag = state_config["outlier_magnitude"]
    invoices_df = generated.get("Revenue_Invoices", pd.DataFrame())
    if invoices_df.empty:
        return pd.DataFrame()
    df = invoices_df.copy()
    df["Period"] = pd.to_datetime(df["Date"]).dt.to_period("M")
    agg = df.groupby(["Period", "CustomerID", "CustomerSegment", "Country", "Region"]).agg(
        OpeningBalance=("Outstanding", lambda x: 0.0),  # Simplified
        Credit=("InvoiceAmount", "sum"),
        Collections=("PaidAmount", "sum"),
    ).reset_index()
    agg["ClosingBalance"] = agg["Credit"] - agg["Collections"]
    agg["DSO_Est"] = np.where(
        agg["Credit"] > 0, (agg["ClosingBalance"] / agg["Credit"]) * 30, 0)
    agg["PeriodEnd"] = agg["Period"].dt.to_timestamp(how='end').dt.date
    cols = ["PeriodEnd", "CustomerID", "CustomerSegment", "Country", "Region",
            "OpeningBalance", "Credit", "Collections", "ClosingBalance", "DSO_Est"]
    final_df = agg[cols]
    final_df = inject_outliers_vectorized(
        final_df, ['ClosingBalance'], freq=outlier_freq, mag=outlier_mag, seed=seed)
    return final_df
