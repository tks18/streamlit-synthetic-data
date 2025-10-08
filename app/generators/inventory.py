from typing import Dict
from faker import Faker
import pandas as pd
import numpy as np

from app.helpers.general import date_range
from app.mods import inject_outliers_vectorized
from app.types import TAppStateConfig


def generate_inventory_snapshots(state_config: TAppStateConfig, faker: Faker = Faker(), generated: Dict[str, pd.DataFrame] = {}):
    seed = state_config["seed"]
    countries = state_config["countries"]
    products = state_config["products"]
    default_regions = state_config["country_config"]
    start_date = state_config["start_date"]
    end_date = state_config["end_date"]
    freq = state_config["frequency"]
    outlier_freq = state_config["outlier_frequency"]
    outlier_mag = state_config["outlier_magnitude"]

    np.random.seed(seed)
    dates = date_range(start_date, end_date, freq)

    warehouse_types = ["Central", "Regional",
                       "Transit", "3PL", "Vendor Managed"]
    storage_conditions = ["Ambient", "Cold Storage",
                          "Hazardous", "Dry", "Climate Controlled"]
    inventory_status = ["Available", "Reserved",
                        "In Transit", "Damaged", "Blocked"]
    categories = ["Raw Material", "WIP", "Finished Goods", "Consumables"]

    rows = []

    for product in products:
        base_stock = np.random.randint(100, 5000)
        category = np.random.choice(categories)

        for d in dates:
            country = np.random.choice(countries)
            region = np.random.choice(
                default_regions.get(country, ["Unknown"]))
            cost_center = f"{region[:3].upper()}-{np.random.randint(1, 11):02d}"
            warehouse_id = f"WH-{np.random.randint(1, 11):02d}"
            warehouse_type = np.random.choice(warehouse_types)
            storage_cond = np.random.choice(storage_conditions)
            inv_status = np.random.choice(inventory_status)

            opening = base_stock + int(np.random.normal(0, base_stock * 0.05))
            receipts = max(0, int(np.random.poisson(lam=base_stock * 0.2)))
            sales = max(0, int(np.random.poisson(lam=base_stock * 0.18)))
            adjustments = int(np.random.normal(0, base_stock * 0.01))
            closing = opening + receipts - sales + adjustments
            closing = max(0, closing)

            unit_cost = round(np.random.uniform(10, 200), 2)
            inventory_value = round(closing * unit_cost, 2)
            carrying_cost = round(
                inventory_value * np.random.uniform(0.005, 0.02), 2)
            reorder_level = int(base_stock * np.random.uniform(0.2, 0.5))
            safety_stock = int(base_stock * np.random.uniform(0.1, 0.3))
            aging_days = int(np.random.normal(45, 15))
            holding_days = max(1, int(np.random.normal(30, 10)))
            stock_turnover = round(sales / ((opening + closing) / 2 + 1), 2)

            rows.append({
                "Date": d.date(),
                "Product": product,
                "Category": category,
                "Country": country,
                "State": region,
                "CostCenter": cost_center,
                "WarehouseID": warehouse_id,
                "WarehouseType": warehouse_type,
                "StorageCondition": storage_cond,
                "InventoryStatus": inv_status,
                "OpeningStock": opening,
                "Receipts": receipts,
                "Sales": sales,
                "Adjustments": adjustments,
                "ClosingStock": closing,
                "UnitCost": unit_cost,
                "InventoryValue": inventory_value,
                "CarryingCost": carrying_cost,
                "ReorderLevel": reorder_level,
                "SafetyStock": safety_stock,
                "AgingDays": aging_days,
                "HoldingDays": holding_days,
                "StockTurnoverRatio": stock_turnover,
            })

    df = pd.DataFrame(rows)

    # inject outliers into InventoryValue for realism
    df = inject_outliers_vectorized(
        df, ['InventoryValue'], freq=outlier_freq, mag=outlier_mag, seed=seed + 4
    )

    # Add derived classification - Inventory Health
    df["InventoryHealth"] = np.select(
        [
            df["ClosingStock"] < df["ReorderLevel"],
            df["ClosingStock"].between(
                df["ReorderLevel"], df["SafetyStock"] * 2),
            df["ClosingStock"] > df["SafetyStock"] * 2,
        ],
        ["Critical", "Optimal", "Excess"],
        default="Unknown"
    )

    return df
