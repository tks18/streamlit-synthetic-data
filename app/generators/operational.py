from typing import Dict
from faker import Faker
import pandas as pd
import numpy as np

from app.helpers.general import date_range
from app.types import TAppStateConfig


def generate_operational_dataset(state_config: TAppStateConfig, faker: Faker, generated: Dict[str, pd.DataFrame] = {}):
    industry = state_config["industry"]
    start_date = state_config["start_date"]
    end_date = state_config["end_date"]
    freq = state_config["frequency"]
    dates = date_range(start_date, end_date, freq)
    countries = state_config["countries"]
    default_regions = state_config["country_config"]
    industry_config = state_config["industry_kpi"].get(industry)
    rows = []
    if industry_config is None:
        return pd.DataFrame()
    kpi_template = industry_config.get("operational")
    if kpi_template is None:
        return pd.DataFrame()
    for d in dates:
        country = np.random.choice(countries)
        region = np.random.choice(
            default_regions.get(country, ["Unknown"]))
        row = {"Industry": industry, "Date": d.date(
        ), "Country": country, "State": region}
        for cfg in kpi_template:
            cname = cfg.get("name", "Unknown")
            ctype = cfg.get("type", "range")
            if cfg.get("type") is None:
                row[cname] = np.nan
            if ctype == "choice":
                row[cname] = np.random.choice(
                    cfg.get("options", ["unknown"]))
            elif ctype == "range":
                allow_float = cfg.get("float", True)
                row[cname] = float(np.random.uniform(
                    cfg.get("min", 0), cfg.get("max", 1))) if allow_float else int(np.random.randint(
                        int(cfg.get("min", 0)), int(cfg.get("max", 100))
                    ))
            else:
                row[cname] = np.nan
        rows.append(row)
    return pd.DataFrame(rows)
