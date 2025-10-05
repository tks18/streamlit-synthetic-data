from typing import Dict
from faker import Faker
import pandas as pd
import numpy as np
import uuid

from app.helpers.config import INDUSTRY_KPIS
from app.helpers.general import set_seed
from app.types import TAppStateConfig


def generate_vendor_master(state_config: TAppStateConfig, faker: Faker = Faker(), generated: Dict[str, pd.DataFrame] = {}):
    countries = state_config["countries"]
    default_regions = state_config["country_config"]
    total_vendors = state_config["total_vendors"]
    rows = []
    for _ in range(total_vendors):
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
