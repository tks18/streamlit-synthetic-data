import pandas as pd
import numpy as np

from app.helpers.general import date_range


def generate_inventory_snapshots(products, start, end, freq, seed=42):
    dates = date_range(start, end, freq)
    rows = []
    for product in products:
        base_stock = np.random.randint(100, 5000)
        for d in dates:
            opening = base_stock + int(np.random.normal(0, base_stock * 0.05))
            receipts = max(0, int(np.random.poisson(lam=base_stock*0.2)))
            sales = max(0, int(np.random.poisson(lam=base_stock*0.18)))
            closing = opening + receipts - sales
            rows.append({
                "Product": product, "Date": d.date(), "OpeningStock": opening,
                "Receipts": receipts, "Sales": sales, "ClosingStock": closing,
                "InventoryValue": round(closing * np.random.uniform(10, 200), 2),
                "Region": np.random.choice(["North", "South", "West", "East"])
            })
    return pd.DataFrame(rows)
