import pandas as pd
import numpy as np
import uuid

from app.helpers.config import INDUSTRY_KPIS
from app.helpers.general import set_seed


def generate_vendor_master(n_vendors=100, countries=None, default_regions=None, faker=None, seed=42):
    faker = faker or set_seed(seed)
    countries = countries or ["India"]
    default_regions = default_regions or {"India": ["Karnataka"]}
    rows = []
    for _ in range(n_vendors):
        country = np.random.choice(countries)
        region = np.random.choice(default_regions.get(country, ["Unknown"]))
        rows.append({
            "VendorID": f"VEND_{uuid.uuid4().hex[:8]}",
            "VendorName": faker.company(),
            "Country": country,
            "Region": region,
            "VendorType": np.random.choice(["Local", "International", "Partner"]),
            "Industry": np.random.choice(list(INDUSTRY_KPIS.keys()))
        })
    return pd.DataFrame(rows)
