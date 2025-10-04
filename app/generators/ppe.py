import pandas as pd
import numpy as np
import uuid

from app.helpers.config import DEFAULT_START_DATE, DEFAULT_END_DATE
from app.helpers.general import set_seed


def generate_ppe_register(n_assets=200, start_date=None, end_date=None, countries=None, default_regions=None, faker=None, seed=42):
    faker = faker or set_seed(seed)
    countries = countries or ["India"]
    default_regions = default_regions or {"India": ["Karnataka"]}
    rows = []
    for _ in range(n_assets):
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
            "Country": country, "Region": region,
            "Department": np.random.choice(["Finance", "Ops", "Sales", "R&D"])
        })
    return pd.DataFrame(rows)
