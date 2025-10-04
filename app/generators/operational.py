import pandas as pd
import numpy as np

from app.helpers.config import INDUSTRY_KPIS
from app.helpers.general import date_range, set_seed


def generate_operational_dataset(industry, start, end, freq, kpi_template=None, countries=None, default_regions=None, faker=None, seed=42, rows_per_period=50):
    faker = faker or set_seed(seed)
    dates = date_range(start, end, freq)
    countries = countries or ["India"]
    default_regions = default_regions or {"India": ["Karnataka"]}
    rows = []
    if not kpi_template:
        kpi_template = INDUSTRY_KPIS.get(industry, {}).get("operational", [])

    for d in dates:
        for _ in range(rows_per_period):
            country = np.random.choice(countries)
            region = np.random.choice(
                default_regions.get(country, ["Unknown"]))
            row = {"Industry": industry, "Date": d.date(
            ), "Country": country, "Region": region}
            for cfg in kpi_template:
                cname = cfg.get("name", "Unknown")
                ctype = cfg.get("type", "range")
                if ctype == "choice":
                    row[cname] = np.random.choice(
                        cfg.get("options", ["unknown"]))
                elif ctype == "range":
                    allow_float = cfg.get("float", True)
                    row[cname] = float(np.random.uniform(
                        cfg.get("min", 0), cfg.get("max", 1))) if allow_float else int(np.random.randint(
                            cfg.get("min", 0), cfg.get("max", 100)
                        ))
                else:
                    row[cname] = np.nan
            rows.append(row)
    return pd.DataFrame(rows)
