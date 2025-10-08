from typing import Dict
from faker import Faker
import pandas as pd
import numpy as np
import uuid

from app.helpers.general import date_range
from app.mods import inject_outliers_vectorized
from app.types import TAppStateConfig


def generate_purchases(state_config: TAppStateConfig, faker: Faker = Faker(), generated: Dict[str, pd.DataFrame] = {}):
    seed = state_config["seed"]
    industry = state_config["industry"]
    products = state_config["products"]
    start_date = state_config["start_date"]
    end_date = state_config["end_date"]
    freq = state_config["frequency"]
    outlier_freq = state_config["outlier_frequency"]
    outlier_mag = state_config["outlier_magnitude"]
    dates = date_range(start_date, end_date, freq)
    vendors_df = generated.get("Vendor_Master", pd.DataFrame())
    purchases_per_period = np.random.randint(10, 20)
    rows = []
    if vendors_df.empty:
        return pd.DataFrame()
    for d in dates:
        period_vendors = vendors_df.sample(
            n=min(len(vendors_df), purchases_per_period), random_state=seed)
        for vend in period_vendors.itertuples(index=False):
            invoice_date = d + pd.Timedelta(days=int(np.random.randint(0, 5)))
            rows.append({
                "Industry": industry, "Product": np.random.choice(products), "Date": invoice_date.date(),
                "PurchaseInvoiceID": str(uuid.uuid4().int)[:12], "VendorID": vend.VendorID,
                "VendorType": vend.VendorType, "Country": vend.Country, "State": vend.State,
                "PurchaseAmount": float(np.random.randint(2000, 250000))
            })
    df = pd.DataFrame(rows)
    df = inject_outliers_vectorized(
        df, ['PurchaseAmount'], freq=outlier_freq, mag=outlier_mag, seed=seed+3)
    return df
