import pandas as pd
import numpy as np
import uuid

from app.helpers.general import date_range, set_seed


def generate_purchases(vendors_df, products, start, end, freq, industry, faker=None, seed=42, purchases_per_period=3):
    faker = faker or set_seed(seed)
    dates = date_range(start, end, freq)
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
                "PurchaseInvoiceID": uuid.uuid4().hex[:12], "VendorID": vend.VendorID,
                "VendorType": vend.VendorType, "Country": vend.Country, "Region": vend.Region,
                "PurchaseAmount": float(np.random.randint(2000, 250000))
            })
    return pd.DataFrame(rows)
