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
    np.random.seed(seed)
    start_date = pd.to_datetime(state_config["start_date"])
    end_date = pd.to_datetime(state_config["end_date"])
    total_assets = state_config["total_assets"]
    countries = state_config["countries"]
    default_regions = state_config["country_config"]
    outlier_freq = state_config["outlier_frequency"]
    outlier_mag = state_config["outlier_magnitude"]

    asset_types = ["Building", "Plant & Machinery", "Office Equipment",
                   "Furniture", "Vehicles", "Computers", "Leasehold Improvements"]
    ownership_types = ["Owned", "Leased",
                       "Joint Venture Asset", "Under Construction"]
    condition_status = ["Good", "Needs Maintenance", "Damaged", "Disposed"]
    depreciation_methods = ["SLM", "WDV", "Usage-based"]
    capex_sources = ["Internal Funds", "Bank Loan",
                     "Parent Funding", "Lease Liability"]
    departments = ["Finance", "Ops", "Sales", "R&D", "HR", "IT"]

    rows = []
    for _ in range(total_assets):
        acq_date = faker.date_between(start_date=start_date, end_date=end_date) if start_date and end_date else faker.date_between(
            start_date=DEFAULT_START_DATE, end_date=DEFAULT_END_DATE)
        cost = float(round(np.random.randint(50000, 5000000), 2))
        useful_life = np.random.choice([3, 5, 7, 10, 15, 20])
        years_used = max(0, (pd.to_datetime(end_date) -
                         pd.to_datetime(acq_date)).days / 365.25)
        acc_dep = min(cost, cost / useful_life * years_used)
        carrying_val = max(cost - acc_dep, 0)

        country = np.random.choice(countries)
        region = np.random.choice(default_regions.get(country, ["Unknown"]))
        department = np.random.choice(departments)

        # 🔹 Region-based cost center
        cc_number = np.random.randint(1, 11)  # 1 to 10
        cost_center = f"{region.replace(' ', '')[:10]}-CC-{cc_number:02d}"

        # Extended numerical features
        salvage_value = round(cost * np.random.uniform(0.01, 0.15), 2)
        insurance_value = round(cost * np.random.uniform(0.8, 1.2), 2)
        reval_increase = round(np.random.uniform(
            0, 0.3) * cost if np.random.rand() < 0.2 else 0, 2)
        impairment_loss = round(np.random.uniform(
            0, 0.2) * carrying_val if np.random.rand() < 0.1 else 0, 2)
        repair_cost = round(np.random.uniform(0, 0.05) *
                            cost if np.random.rand() < 0.3 else 0, 2)
        maintenance_cost_ytd = round(np.random.uniform(0, 0.03) * cost, 2)

        dep_rate = round(acc_dep / cost if cost else 0, 4)
        book_to_insurance_ratio = round(
            carrying_val / insurance_value if insurance_value else 0, 4)

        rows.append({
            "AssetID": f"ASSET_{str(uuid.uuid4().int)[:8]}",
            "AssetDesc": faker.word().capitalize(),
            "AssetType": np.random.choice(asset_types),
            "Department": department,
            "CostCenter": cost_center,
            "OwnershipType": np.random.choice(ownership_types),
            "ConditionStatus": np.random.choice(condition_status),
            "DepreciationMethod": np.random.choice(depreciation_methods),
            "CapexSource": np.random.choice(capex_sources),
            "Country": country,
            "State": region,

            "AcquisitionDate": acq_date,
            "UsefulLifeYears": useful_life,
            "YearsUsed": round(years_used, 2),
            "Cost": cost,
            "AccumulatedDepreciation": round(acc_dep, 2),
            "CarryingValue": round(carrying_val, 2),
            "SalvageValue": salvage_value,
            "InsuranceValue": insurance_value,
            "RevaluationIncrease": reval_increase,
            "ImpairmentLoss": impairment_loss,
            "RepairCost": repair_cost,
            "MaintenanceCostYTD": maintenance_cost_ytd,
            "DepreciationRate": dep_rate,
            "BookToInsuranceRatio": book_to_insurance_ratio,
            "IsImpaired": int(impairment_loss > 0),
            "IsRevalued": int(reval_increase > 0),
            "IsDisposed": int(np.random.rand() < 0.05),
        })

    df = pd.DataFrame(rows)
    df = inject_outliers_vectorized(
        df, ['Cost', 'CarryingValue', 'AccumulatedDepreciation'], freq=outlier_freq, mag=outlier_mag, seed=seed + 2)
    return df
