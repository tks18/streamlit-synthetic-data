import pandas as pd
import numpy as np

from app.helpers.general import set_seed


def generate_debtors_from_invoices(invoices_df, freq='M'):
    if invoices_df.empty:
        return pd.DataFrame()
    df = invoices_df.copy()
    df["Period"] = pd.to_datetime(df["Date"]).dt.to_period(freq)
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
    return agg[cols]
