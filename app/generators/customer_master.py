from typing import Dict
from faker import Faker
import pandas as pd
import numpy as np
import uuid

from app.helpers.config import INDUSTRY_KPIS
from app.types import TAppStateConfig


def generate_customer_master(state_config: TAppStateConfig, faker: Faker = Faker(), generated: Dict[str, pd.DataFrame] = {}):
    countries = state_config["countries"]
    default_regions = state_config["country_config"]
    total_customers = state_config["total_customers"]
    rows = []
    for _ in range(total_customers):
        country = np.random.choice(countries)
        region = np.random.choice(default_regions.get(country, ["Unknown"]))
        rows.append({
            "CustomerID": f"CUST_{uuid.uuid4().hex[:8]}",
            "CustomerName": faker.company(),
            "Country": country,
            "Region": region,
            "CustomerSegment": np.random.choice(["SME", "Enterprise", "Startup"]),
            "Industry": np.random.choice(list(INDUSTRY_KPIS.keys()))
        })
    return pd.DataFrame(rows)
