from typing import Dict
from faker import Faker
import pandas as pd
import numpy as np

from app.helpers.general import date_range
from app.mods import inject_outliers_vectorized
from app.types import TAppStateConfig


def generate_inventory_snapshots(state_config: TAppStateConfig, faker: Faker = Faker(), generated: Dict[str, pd.DataFrame] = {}):
    seed = state_config["seed"]
    products = state_config["products"]
    start_date = state_config["start_date"]
    end_date = state_config["end_date"]
    freq = state_config["frequency"]
    outlier_freq = state_config["outlier_frequency"]
    outlier_mag = state_config["outlier_magnitude"]
    dates = date_range(start_date, end_date, freq)
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
    df = pd.DataFrame(rows)
    df = inject_outliers_vectorized(
        df, ['InventoryValue'], freq=outlier_freq, mag=outlier_mag, seed=seed+4)
    return df
