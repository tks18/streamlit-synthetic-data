from typing import Dict
from faker import Faker
import pandas as pd
import numpy as np
import uuid

from app.helpers.config import DEFAULT_START_DATE, DEFAULT_END_DATE
from app.mods import inject_outliers_vectorized
from app.types import TAppStateConfig


def generate_ppe_register(state_config: TAppStateConfig, faker: Faker = Faker(), generated: Dict[str, pd.DataFrame] = {}):
    seed = state_config["seed"]
    start_date = pd.to_datetime(state_config["start_date"])
    end_date = pd.to_datetime(state_config["end_date"])
    total_assets = state_config["total_assets"]
    countries = state_config["countries"]
    default_regions = state_config["country_config"]
    outlier_freq = state_config["outlier_frequency"]
    outlier_mag = state_config["outlier_magnitude"]
    rows = []
    for _ in range(total_assets):
        acq_date = faker.date_between(start_date=start_date, end_date=end_date) if start_date and end_date else faker.date_between(
            start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE)
        cost = float(round(np.random.randint(50000, 5000000), 2))
        useful_life = np.random.choice([3, 5, 7, 10, 15, 20])
        years_used = max(0, (pd.to_datetime(end_date) -
                         pd.to_datetime(acq_date)).days / 365.25) if end_date else max(0, (pd.to_datetime(DEFAULT_END_DATE) -
                                                                                           pd.to_datetime(acq_date)).days / 365.25)
        acc_dep = min(cost, cost / useful_life * years_used)
        country = np.random.choice(countries)
        region = np.random.choice(default_regions.get(country, ["Unknown"]))
        rows.append({
            "AssetID": f"ASSET_{uuid.uuid4().hex[:8]}", "AssetDesc": faker.word().capitalize(),
            "AcquisitionDate": acq_date, "Cost": cost, "UsefulLifeYears": useful_life,
            "AccumulatedDepreciation": round(acc_dep, 2), "CarryingValue": round(cost - acc_dep, 2),
            "Country": country, "State": region,
            "Department": np.random.choice(["Finance", "Ops", "Sales", "R&D"])
        })
    df = pd.DataFrame(rows)
    df = inject_outliers_vectorized(
        df, ['Cost'], freq=outlier_freq, mag=outlier_mag, seed=seed+2)
    return df
