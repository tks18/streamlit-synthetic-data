from narwhals import col
import streamlit as st
import pandas as pd
import numpy as np
from faker import Faker
import json
import uuid
import io
import zipfile
import ast
import math
import random
import os
from datetime import datetime
from streamlit_sortables import sort_items
SORTABLES_AVAILABLE = True

# ----------------------------
# Config & folders
# ----------------------------
APP_MAIN_TITLE = "Shan's Dataverse"
APP_TITLE = "📈 Enhanced Data Cockpit — Finance + Ops"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(PROFILES_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# ----------------------------
# Default Data Schemas (Added to make the script runnable)
# ----------------------------
DEFAULT_START_DATE = "2020-01-01"
DEFAULT_END_DATE = "2022-12-31"
INDUSTRY_KPIS = {
    "IT Services": {
        "products": ["Cloud Migration", "Managed Services", "Software Dev"],
        "operational": ["TicketsResolved", "ProjectHours", "ServerUptimePct"]
    },
    "Steel": {
        "products": ["TMT Bars", "Steel Coils", "Structural Steel"],
        "operational": ["CoalUsed", "EnergyUsed", "ProductionTons", "FurnaceTemp"]
    },
    "Pharma": {
        "products": ["API-A", "Formulation-X", "Vaccine-Y"],
        "operational": ["BatchYield", "ContaminationEvents", "R&D_Hours"]
    }
}

DEFAULT_REGIONS = {
    "India": ["Karnataka", "Maharashtra", "Delhi", "Tamil Nadu"],
    "USA": ["California", "Texas", "New York"],
    "Germany": ["Bavaria", "Berlin", "Hesse"]
}

# ----------------------------
# Write default templates if not present
# ----------------------------
DEFAULT_TEMPLATES = {
    "it_o2c": {
        "description": "IT Services: Revenue + Debtors + ProjectHours",
        "custom_config": {
            "Revenue_Invoices": {
                "InvoiceType": {"type": "choice", "options": ["Standard", "Credit"]},
                "Currency": {"type": "choice", "options": ["INR", "USD"]},
                "DiscountPct": {"type": "range", "min": 0, "max": 5}
            },
            "IT_Services_Operational": {
                "ProjectHours": {"type": "range", "min": 1, "max": 12},
                "TicketsResolved": {"type": "range", "min": 0, "max": 50}
            }
        },
        "scenarios": []
    },
    "steel_supply_shock": {
        "description": "Steel: Add coal usage KPIs and a supply-shock scenario",
        "custom_config": {
            "Steel_Operational": {
                "CoalUsed": {"type": "range", "min": 1000, "max": 5000},
                "EnergyUsed": {"type": "range", "min": 500, "max": 2000}
            }
        },
        "scenarios": [
            {"name": "Coal supply shock", "type": "shock", "target_dataset": "Operational", "target_column": "CoalUsed", "start": str(
                datetime(2024, 12, 1).date()), "end": str(datetime(2024, 12, 31).date()), "magnitude": 0.6, "mode": "multiplier", "seed": 42}
        ]
    },
    "pharma_seasonal_fraud": {
        "description": "Pharma: Seasonal sales and fraudulent expense claims",
        "custom_config": {
            "Revenue_Invoices": {
                "BatchID": {"type": "choice", "options": ["B01", "B02", "B03"]}
            }
        },
        "scenarios": [
            {
                "name": "Winter Sales Spike",
                "type": "seasonal",
                "target_dataset": "Revenue_Invoices",
                "target_column": "InvoiceAmount",
                "month_multipliers": {"11": 1.3, "12": 1.6, "1": 1.4}
            },
            {
                "name": "Fraudulent Purchases",
                "type": "fraud_outlier",
                "target_dataset": "Purchases",
                "target_column": "PurchaseAmount",
                "pct": 0.02,
                "multiplier": 10.0,
                "seed": 123
            }
        ]
    }
}

for k, v in DEFAULT_TEMPLATES.items():
    p = os.path.join(TEMPLATES_DIR, f"{k}.json")
    if not os.path.exists(p):
        with open(p, "w") as fh:
            json.dump(v, fh, indent=2)

# ----------------------------
# Allowed modules for formulas
# ----------------------------
ALLOWED_MODULES = {
    "np": np,
    "math": math,
    "random": random,
    "pd": pd
}

# ----------------------------
# AST-based validation (restricts constructs)
# ----------------------------


class VectorSafeVisitor(ast.NodeVisitor):
    """Allow arithmetic, calls, names, attributes (only for allowed modules), subscript, tuples, lists."""
    ALLOWED_NODES = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Div, ast.Name, ast.Mult, ast.Add, ast.Sub,
        ast.Load, ast.Call, ast.Attribute, ast.Subscript, ast.Index, ast.Slice,
        ast.Tuple, ast.List, ast.Dict, ast.BoolOp, ast.Compare, ast.IfExp
    )

    def __init__(self, allowed_names):
        self.allowed_names = set(allowed_names) | set(ALLOWED_MODULES.keys())

    def generic_visit(self, node):
        if not isinstance(node, self.ALLOWED_NODES):
            raise ValueError(f"Disallowed AST node: {node.__class__.__name__}")
        super().generic_visit(node)

    def visit_Name(self, node):
        if node.id not in self.allowed_names:
            raise ValueError(
                f"Use of name '{node.id}' is not allowed in formulas.")
        super().generic_visit(node)

    def visit_Attribute(self, node):
        # allow attribute access only when base is allowed module
        base = node
        while isinstance(base, ast.Attribute):
            base = base.value
        if isinstance(base, ast.Name):
            if base.id not in ALLOWED_MODULES:
                raise ValueError(
                    f"Attribute access on '{base.id}' is not allowed.")
        else:
            raise ValueError("Complex attribute expressions not allowed.")
        super().generic_visit(node)


def validate_formula_ast(expr, allowed_names):
    node = ast.parse(expr, mode="eval")
    visitor = VectorSafeVisitor(allowed_names)
    visitor.visit(node)
    return True

# ----------------------------
# Vectorized formula evaluation
# ----------------------------


def vectorized_eval(expr: str, df: pd.DataFrame):
    """
    Try to evaluate expr in a vectorized manner by providing numpy arrays for columns.
    If it fails (due to uses of Python-only constructs), raise an Exception so caller can fallback.
    """
    allowed_names = list(df.columns)
    validate_formula_ast(expr, allowed_names)

    # FIX: Use dictionary merge `|` (Python 3.9+) to avoid type checker errors.
    local_vars = {c: df[c].to_numpy() for c in df.columns} | ALLOWED_MODULES

    try:
        # Evaluate safely (no builtins)
        result = eval(compile(ast.parse(expr, mode="eval"), '<vec_expr>', 'eval'), {
                      "__builtins__": None}, local_vars)
    except Exception as e:
        raise

    if hasattr(result, '__len__') and not isinstance(result, (str, bytes)) and len(result) == len(df):
        return pd.Series(result)
    else:  # Handle scalar result
        return pd.Series([result] * len(df))

# ----------------------------
# Safe fallback row-wise evaluator
# ----------------------------


def rowwise_safe_eval(expr: str, row: dict):
    validate_formula_ast(expr, list(row.keys()))
    local_vars = row | ALLOWED_MODULES
    return eval(compile(ast.parse(expr, mode="eval"), '<row_expr>', 'eval'), {"__builtins__": None}, local_vars)

# ----------------------------
# Utility functions (data generation)
# ----------------------------


def set_seed(seed, locale=None):
    np.random.seed(seed)
    random.seed(seed)
    Faker.seed(seed)
    return Faker(locale) if locale else Faker()


def rand_ids(prefix, n):
    return [f"{prefix}_{uuid.uuid4().hex[:8]}" for _ in range(n)]


def date_range(start, end, freq):
    return pd.date_range(start=start, end=end, freq=freq)


def inject_outliers_vectorized(df, cols, freq=0.01, mag=3.0, method="multiplier", seed=None):
    if seed is not None:
        np.random.seed(seed)
    df = df.copy()
    n = len(df)
    if n == 0:
        return df
    k = max(1, int(np.floor(freq * n)))
    idx = np.random.choice(df.index, size=k, replace=False)
    factors = np.random.uniform(mag, mag * 1.5, size=k)
    for col in cols:
        if col not in df.columns:
            continue
        if method == "multiplier":
            df.loc[idx, col] = df.loc[idx, col] * factors
        else:  # additive
            df.loc[idx, col] = df.loc[idx, col] + \
                (df.loc[idx, col].abs().mean() * factors)
    return df

# --- Restored Data Generators ---


def generate_customer_master(n_customers=200, countries=None, default_regions=None, faker=None, seed=42):
    faker = faker or set_seed(seed)
    countries = countries or ["India"]
    default_regions = default_regions or {"India": ["Karnataka"]}
    rows = []
    for _ in range(n_customers):
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


def generate_revenue_invoices(products, start, end, freq, customers_df, industry, faker=None, seed=42, invoice_per_product_per_period=5):
    faker = faker or set_seed(seed)
    dates = date_range(start, end, freq)
    rows = []
    if customers_df.empty:
        return pd.DataFrame()
    for product in products:
        for d in dates:
            n_sample = min(len(customers_df), invoice_per_product_per_period)
            period_customers = customers_df.sample(
                n=n_sample, replace=False, random_state=seed)
            amounts = np.random.randint(
                5000, 200000, size=len(period_customers))
            for cust, amt in zip(period_customers.itertuples(index=False), amounts):
                invoice_date = d + \
                    pd.Timedelta(days=int(np.random.randint(0, 5)))
                credit_days = int(np.random.choice(
                    [30, 45, 60, 90], p=[0.6, 0.2, 0.15, 0.05]))
                due_date = invoice_date + pd.Timedelta(days=credit_days)
                pay_flag = np.random.choice(
                    ["Paid", "PartiallyPaid", "Unpaid"], p=[0.7, 0.15, 0.15])
                if pay_flag == "Paid":
                    payment_date = due_date + \
                        pd.Timedelta(days=int(np.random.poisson(lam=5)))
                    paid_amount = amt
                elif pay_flag == "PartiallyPaid":
                    payment_date = due_date + \
                        pd.Timedelta(days=int(np.random.randint(1, 60)))
                    paid_amount = amt * np.random.uniform(0.3, 0.9)
                else:  # Unpaid
                    payment_date, paid_amount = pd.NaT, 0.0
                rows.append({
                    "Industry": industry, "Product": product, "Date": invoice_date.date(),
                    "InvoiceID": uuid.uuid4().hex[:12], "CustomerID": cust.CustomerID,
                    "CustomerSegment": cust.CustomerSegment, "Country": cust.Country, "Region": cust.Region,
                    "InvoiceAmount": float(amt), "DueDate": due_date.date(),
                    "PaymentDate": (payment_date.date() if pd.notna(payment_date) else pd.NaT),
                    "PaidAmount": float(round(paid_amount, 2)), "PaymentStatus": pay_flag
                })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["Outstanding"] = df["InvoiceAmount"] - df["PaidAmount"]
    return df


def generate_debtors_from_invoices(invoices_df, freq='M'):
    if invoices_df.empty:
        return pd.DataFrame()
    df = invoices_df.copy()
    df["Period"] = pd.to_datetime(df["Date"]).dt.to_period(freq)
    agg = df.groupby(["Period", "CustomerID", "CustomerSegment", "Country", "Region"]).agg(
        OpeningBalance=("Outstanding", lambda x: 0.0),  # Simplified
        Credit=("InvoiceAmount", "sum"),
        Collections=("PaidAmount", "sum"),
    ).reset_index()
    agg["ClosingBalance"] = agg["Credit"] - agg["Collections"]
    agg["DSO_Est"] = np.where(
        agg["Credit"] > 0, (agg["ClosingBalance"] / agg["Credit"]) * 30, 0)
    agg["PeriodEnd"] = agg["Period"].dt.to_timestamp(how='end').dt.date
    cols = ["PeriodEnd", "CustomerID", "CustomerSegment", "Country", "Region",
            "OpeningBalance", "Credit", "Collections", "ClosingBalance", "DSO_Est"]
    return agg[cols]


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


def generate_purchases(vendors_df, products, start, end, freq, industry, faker=None, seed=42, purchases_per_period=3):
    faker = faker or set_seed(seed)
    dates = date_range(start, end, freq)
    rows = []
    if vendors_df.empty:
        return pd.DataFrame()
    for d in dates:
        period_vendors = vendors_df.sample(
            n=min(len(vendors_df), purchases_per_period), random_state=seed)
        for vend in period_vendors.itertuples(index=False):
            invoice_date = d + pd.Timedelta(days=int(np.random.randint(0, 5)))
            rows.append({
                "Industry": industry, "Product": np.random.choice(products), "Date": invoice_date.date(),
                "PurchaseInvoiceID": uuid.uuid4().hex[:12], "VendorID": vend.VendorID,
                "VendorType": vend.VendorType, "Country": vend.Country, "Region": vend.Region,
                "PurchaseAmount": float(np.random.randint(2000, 250000))
            })
    return pd.DataFrame(rows)


def generate_inventory_snapshots(products, start, end, freq, seed=42):
    dates = date_range(start, end, freq)
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
    return pd.DataFrame(rows)


def generate_operational_dataset(industry, start, end, freq, kpi_template=None, faker=None, seed=42, rows_per_period=50):
    faker = faker or set_seed(seed)
    dates = date_range(start, end, freq)
    rows = []
    if not kpi_template:
        kpi_template = {}
        ops_kpis = INDUSTRY_KPIS.get(industry, {}).get("operational", [])
        for kpi in ops_kpis:
            kpi_template[kpi] = {"type": "range", "min": 1, "max": 100}

    for d in dates:
        for _ in range(rows_per_period):
            row = {"Industry": industry, "Date": d.date(), "Region": np.random.choice([
                "North", "South", "West", "East"])}
            for k, cfg in kpi_template.items():
                ctype = cfg.get("type", "range")
                if ctype == "choice":
                    row[k] = np.random.choice(cfg.get("options", ["unknown"]))
                elif ctype == "range":
                    row[k] = float(np.random.uniform(
                        cfg.get("min", 0), cfg.get("max", 1)))
                else:
                    row[k] = np.nan
            rows.append(row)
    return pd.DataFrame(rows)

# ----------------------------
# Custom column storage helpers (ordered)
# ----------------------------


def get_dataset_config(ds):
    return st.session_state.custom_config_ordered.get(ds, [])


def set_dataset_config(ds, ordered_list):
    st.session_state.custom_config_ordered[ds] = ordered_list


def add_or_update_column(ds, col_name, col_cfg):
    lst = get_dataset_config(ds)
    for i, (c, _) in enumerate(lst):
        if c == col_name:
            lst[i] = (col_name, col_cfg)
            set_dataset_config(ds, lst)
            return
    lst.append((col_name, col_cfg))
    set_dataset_config(ds, lst)


def delete_column(ds, col_name):
    lst = [x for x in get_dataset_config(ds) if x[0] != col_name]
    set_dataset_config(ds, lst)


def move_column(ds, col_name, direction):
    lst = get_dataset_config(ds)
    for i, (c, _) in enumerate(lst):
        if c == col_name:
            if direction == 'up' and i > 0:
                lst[i-1], lst[i] = lst[i], lst[i-1]
            elif direction == 'down' and i < len(lst)-1:
                lst[i+1], lst[i] = lst[i], lst[i+1]
            break
    set_dataset_config(ds, lst)


def apply_custom_columns_vectorized(df: pd.DataFrame, ds_name: str):
    """Applies custom columns from session state to a dataframe."""
    cfg_list = get_dataset_config(ds_name)
    if not cfg_list or df.empty:
        return df

    df = df.copy().reset_index(drop=True)
    for col, col_cfg in cfg_list:
        ctype = col_cfg.get('type')
        if ctype == 'choice':
            opts = col_cfg.get('options', [])
            df[col] = np.random.choice(opts, size=len(df)) if opts else np.nan
        elif ctype == 'range':
            mn, mx = float(col_cfg.get('min', 0)), float(col_cfg.get('max', 1))
            df[col] = np.random.uniform(mn, mx, size=len(df))
        elif ctype == 'formula':
            expr = col_cfg.get('expr', '')
            if not expr:
                df[col] = np.nan
                continue
            try:  # Attempt vectorized evaluation
                df[col] = vectorized_eval(expr, df)
            except Exception as e:  # Fallback to slower row-wise evaluation
                st.warning(
                    f"Formula for '{col}' failed vectorized eval: {e}. Falling back to row-wise.")
                vals = [rowwise_safe_eval(
                    expr, r) if expr else np.nan for r in df.to_dict(orient='records')]
                df[col] = vals
        else:
            df[col] = np.nan
    return df

# ----------------------------
# Scenarios
# ----------------------------


def apply_shock(df: pd.DataFrame, column: str, start_date: str, end_date: str, magnitude: float, mode='multiplier', date_col='Date'):
    df = df.copy()
    if date_col not in df.columns or column not in df.columns:
        return df
    tmp_date = pd.to_datetime(df[date_col], errors='coerce')
    mask = (tmp_date >= pd.to_datetime(start_date)) & (
        tmp_date <= pd.to_datetime(end_date))
    if mode == 'multiplier':
        df.loc[mask, column] *= magnitude
    else:  # additive
        df.loc[mask, column] += magnitude
    return df


def apply_seasonal(df: pd.DataFrame, column: str, month_multipliers: dict, date_col='Date'):
    df = df.copy()
    if date_col not in df.columns or column not in df.columns:
        return df
    tmp_date = pd.to_datetime(df[date_col], errors='coerce')
    if pd.api.types.is_datetime64_any_dtype(tmp_date):
        # Ensure keys in month_multipliers are strings for reliable lookup
        month_multipliers_str_keys = {
            str(k): v for k, v in month_multipliers.items()}
        multipliers = tmp_date.dt.month.astype(str).map(
            month_multipliers_str_keys).fillna(1.0).astype(float)
        df[column] = df[column] * multipliers
    return df


def inject_fraud_outliers(df: pd.DataFrame, column: str, pct: float, multiplier: float, seed=None):
    df = df.copy()
    if seed is not None:
        np.random.seed(seed)
    n = len(df)
    k = max(1, int(np.floor(pct * n)))
    if column not in df.columns or n == 0:
        return df
    idx = np.random.choice(df.index, size=k, replace=False)
    df.loc[idx, column] = df.loc[idx, column] * multiplier
    return df


def apply_correlation(df: pd.DataFrame, source_col: str, target_col: str, coef: float, noise_factor=0.1):
    df = df.copy()
    if source_col not in df.columns or target_col not in df.columns:
        return df
    # Normalize source to prevent scale issues and add some noise for realism
    source_norm = (df[source_col] - df[source_col].mean()) / \
        df[source_col].std()
    noise = np.random.normal(0, df[target_col].std() * noise_factor, len(df))
    df[target_col] = df[target_col] + \
        (coef * source_norm * df[target_col].std()) + noise
    return df

# ----------------------------
# Profile persistence
# ----------------------------


# Default Choices
DEF_INDUSTRY = list(INDUSTRY_KPIS.keys())[0]
DEF_PRODUCTS = INDUSTRY_KPIS[DEF_INDUSTRY]['products']
DEF_FREQ = 'ME'
DEF_FAKER_LOCALE = 'en_IN'
DEF_OUTLIER_FREQ = 0.05
DEF_OUTLIER_MAG = 2
DEF_START_DATE = pd.to_datetime(DEFAULT_START_DATE).date()
DEF_END_DATE = pd.to_datetime(DEFAULT_END_DATE).date()

profile_keys = [
    ('key_industry', 'industry', DEF_INDUSTRY),
    ('key_products', 'products', DEF_PRODUCTS),
    ('key_countries', 'countries', DEFAULT_REGION_CHOICE),
    ('key_start_date', 'start_date', DEF_START_DATE),
    ('key_end_date', 'end_date', DEF_END_DATE),
    ('key_freq', 'frequency', DEF_FREQ),
    ('key_faker_locale', 'faker_locale', DEF_FAKER_LOCALE),
    ('key_outlier_freq', 'outlier_frequency', DEF_OUTLIER_FREQ),
    ('key_outlier_mag', 'outlier_magnitude', DEF_OUTLIER_MAG),
    ('key_custom_columns', 'custom_columns', {}),
    ('key_scenarios', 'scenarios', [])
]


def prepare_profile_paylod():
    payload = {}
    for prof_item in profile_keys:
        state_key, json_key, alt_result = prof_item
        if state_key in ['key_start_date', 'key_end_date']:
            payload[json_key] = st.session_state.get(
                state_key, alt_result).strftime('%Y-%m-%d')
        else:
            payload[json_key] = st.session_state.get(state_key, alt_result)
    return payload

def save_profile_to_disk(name):
    payload = {
        'custom_config_ordered': st.session_state.get('custom_config_ordered', {}),
        'scenarios': st.session_state.get('scenarios', [])
    }
    safe_name = ''.join(ch for ch in name if ch.isalnum()
                        or ch in (' ', '_', '-')).rstrip()
    path = os.path.join(PROFILES_DIR, f"{safe_name}.json")
    with open(path, 'w') as fh:
        json.dump(payload, fh, default=str, indent=2)
    return path


def list_profiles_on_disk():
    return [f for f in os.listdir(PROFILES_DIR) if f.endswith('.json')]


def load_profile_from_disk(fname):
    path = os.path.join(PROFILES_DIR, fname)
    with open(path) as fh:
        payload = json.load(fh)
    st.session_state.custom_config_ordered = payload.get(
        'custom_config_ordered', {})
    st.session_state.scenarios = payload.get('scenarios', [])

# ----------------------------
# Templates
# ----------------------------


def list_templates():
    return [f for f in os.listdir(TEMPLATES_DIR) if f.endswith('.json')]


def load_template(fname):
    path = os.path.join(TEMPLATES_DIR, fname)
    with open(path) as fh:
        payload = json.load(fh)
    # Convert dict config to ordered list format and merge
    for ds, cfg_dict in payload.get('custom_config', {}).items():
        st.session_state.custom_config_ordered[ds] = list(cfg_dict.items())
    # Add scenarios
    st.session_state.scenarios.extend(payload.get('scenarios', []))


# ----------------------------
# Initialize session state
# ----------------------------
if 'custom_config_ordered' not in st.session_state:
    st.session_state.custom_config_ordered = {}
if 'scenarios' not in st.session_state:
    st.session_state.scenarios = []
if 'profiles_cache' not in st.session_state:
    st.session_state.profiles_cache = list_profiles_on_disk()

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title=APP_MAIN_TITLE,
                   layout='wide', page_icon=':sparkles:')
st.title(APP_MAIN_TITLE)
st.subheader(APP_TITLE, divider=True)

# --- Sidebar ---
with st.sidebar:
    st.header('Core Settings')
    industry = st.selectbox('Industry', list(INDUSTRY_KPIS.keys()))
    products_str = INDUSTRY_KPIS.get(industry, {}).get(
        "products", ["Product A", "Product B"])
    products = st.multiselect(
        'Products', options=products_str, default=products_str, accept_new_options=True)

    country_choices = st.multiselect('Country choices', options=list(
        DEFAULT_REGIONS.keys()), default=list(DEFAULT_REGIONS.keys()), accept_new_options=True)
    start_date = st.date_input(
        'Start Date', value=pd.to_datetime('2024-04-01').date())
    end_date = st.date_input(
        'End Date', value=pd.to_datetime('2025-03-31').date())
    freq = st.selectbox(
        'Frequency', ['ME', 'W', 'D'], help="ME=Month-end, W=Week-end, D=Day")
    seed = int(st.number_input('Seed', value=42))
    faker_locale = st.selectbox(
        'Faker locale', ['en_US', 'en_IN', 'hi_IN', 'ta_IN', 'en_GB', 'fr_FR'])
    st.markdown("---")
    st.header('Outliers')
    outlier_freq = st.slider('Outlier Frequency', 0.0, 0.2, 0.02)
    outlier_mag = st.slider('Outlier Magnitude', 1.5, 8.0, 3.0)
    st.markdown('---')
    st.header('Profiles & Templates')
    new_profile_name = st.text_input('Save current config as profile', '')
    if st.button('Save Profile'):
        if new_profile_name.strip():
            p = save_profile_to_disk(new_profile_name.strip())
            st.success(f'Saved profile -> {os.path.basename(p)}')
            st.session_state.profiles_cache = list_profiles_on_disk()
            st.rerun()
        else:
            st.error('Enter a profile name')

    prof_sel = st.selectbox('Load profile from disk', options=[
                            ''] + st.session_state.profiles_cache)
    if st.button('Load Profile'):
        if prof_sel:
            load_profile_from_disk(prof_sel)
            st.success(f'Loaded {prof_sel}')
            st.rerun()
        else:
            st.error('Select a profile file')

    templ_sel = st.selectbox('Load template', [''] + list_templates())
    if st.button('Load Template'):
        if templ_sel:
            load_template(templ_sel)
            st.success(f'Loaded template {templ_sel}')
            st.rerun()
        else:
            st.error('Select a template')

# --- Main Layout: Tabs ---
DATASET_OPTIONS = ['Revenue_Invoices', 'Debtors_Aggregated', 'PPE_Register',
                   'Purchases', 'Inventory', 'Customer_Master', 'Vendor_Master', 'Operational']
DATASET_COL_KEYS = DEFAULT_SCHEMAS = {
    "Customer_Master": {
        "CustomerID": "str",
        "CustomerName": "str",
        "Country": "str",
        "Region": "str",
        "CustomerSegment": "str",
        "Industry": "str"
    },
    "Vendor_Master": {
        "VendorID": "str",
        "VendorName": "str",
        "Country": "str",
        "Region": "str",
        "VendorType": "str",
        "Industry": "str"
    },
    "Revenue_Invoices": {
        "Industry": "str",
        "Product": "str",
        "Date": "date",
        "InvoiceID": "str",
        "CustomerID": "str",
        "CustomerSegment": "str",
        "Country": "str",
        "Region": "str",
        "InvoiceAmount": "float",
        "DueDate": "date",
        "PaymentDate": "date",
        "PaidAmount": "float",
        "PaymentStatus": "str",
        "Outstanding": "float"
    },
    "Debtors_Aggregated": {
        "PeriodEnd": "date",
        "CustomerID": "str",
        "CustomerSegment": "str",
        "Country": "str",
        "Region": "str",
        "OpeningBalance": "float",
        "Credit": "float",
        "Collections": "float",
        "ClosingBalance": "float",
        "DSO_Est": "float"
    },
    "PPE_Register": {
        "AssetID": "str",
        "AssetDesc": "str",
        "AcquisitionDate": "date",
        "Cost": "float",
        "UsefulLifeYears": "int",
        "AccumulatedDepreciation": "float",
        "CarryingValue": "float",
        "Country": "str",
        "Region": "str",
        "Department": "str"
    },
    "Purchases": {
        "Industry": "str",
        "Product": "str",
        "Date": "date",
        "PurchaseInvoiceID": "str",
        "VendorID": "str",
        "VendorType": "str",
        "Country": "str",
        "Region": "str",
        "PurchaseAmount": "float"
    },
    "Inventory": {
        "Product": "str",
        "Date": "date",
        "OpeningStock": "int",
        "Receipts": "int",
        "Sales": "int",
        "ClosingStock": "int",
        "InventoryValue": "float",
        "Region": "str"
    },
    "Operational": {
        "Industry": "str",
        "Date": "date",
        "Region": "str",
    }
}
tab1, tab2, tab3 = st.tabs(
    ['Custom Columns', 'Scenarios', 'Generate & Download'])

# ----------------------------
# Tab 1: Custom Columns GUI (with Drag-and-Drop)
# ----------------------------
with tab1:
    st.header('Custom Columns')
    ds_to_edit = st.selectbox('Dataset to customize',
                              options=DATASET_OPTIONS, key="ds_selector")

    lst = get_dataset_config(ds_to_edit)
    st.subheader(f'Default Columns for `{ds_to_edit}`')
    col_info = pd.DataFrame([DEFAULT_SCHEMAS[ds_to_edit]])
    st.dataframe(col_info, hide_index=True)
    st.subheader(f'Custom Columns for `{ds_to_edit}`')

    if not lst:
        st.info(
            'No custom columns yet. Add one below or load a template from the sidebar.')
    else:
        st.info('Drag and drop the columns to reorder them.', icon="↕️")

        display_items = [
            f"{cname} || `{ccfg.get('type')}`" for cname, ccfg in lst]
        new_order_display = sort_items(display_items, direction='vertical')

        original_map = {f"{cname} || `{ccfg.get('type')}`": (
            cname, ccfg) for cname, ccfg in lst}
        new_ordered_list = [original_map[item]
                            for item in new_order_display]

        if new_ordered_list != lst:
            set_dataset_config(ds_to_edit, new_ordered_list)
            st.rerun()

        for i, (cname, ccfg) in enumerate(new_ordered_list):
            with st.container(border=True):
                cols = st.columns([4, 1])
                cols[0].markdown(
                    f"**{i+1}. {cname}** (`{ccfg.get('type')}`)")
                cols[0].caption(json.dumps(ccfg))
                if cols[1].button('Delete', key=f'del_{ds_to_edit}_{cname}', use_container_width=True):
                    delete_column(ds_to_edit, cname)
                    st.rerun()

    # --- ADD/UPDATE FORM ---
    st.markdown('---')
    st.subheader('Add / Update Column')
    col_type = st.selectbox(
        'Type', ['formula', 'range', 'choice'], key='new_col_type')
    with st.form('addcol', border=True):
        col_name = st.text_input('Column name')

        if col_type == 'formula':
            st.markdown(
                'Use column names directly. Allowed modules: `np`, `math`, `random`, `pd`.')
            expr = st.text_area('Expression', 'np.log1p(InvoiceAmount)')
            col_config = {'type': 'formula', 'expr': expr}
        elif col_type == 'range':
            rmin, rmax = st.columns(2)
            min_val = rmin.number_input('Min', value=0.0)
            max_val = rmax.number_input('Max', value=1.0)
            col_config = {'type': 'range', 'min': float(
                min_val), 'max': float(max_val)}
        else:  # choice
            options = st.text_area('Options (comma separated)', 'A, B, C')
            opts = [o.strip() for o in options.split(',') if o.strip()]
            col_config = {'type': 'choice', 'options': opts}

        if st.form_submit_button('Save Column'):
            if not col_name.strip():
                st.error('Enter a column name')
            else:
                add_or_update_column(ds_to_edit, col_name.strip(), col_config)
                st.success(
                    f"Saved column '{col_name}' to `{ds_to_edit}` config.")
                st.rerun()

# ----------------------------
# Tab 2: Scenario Simulator
# ----------------------------
with tab2:
    st.header('Scenarios')
    st.info('Scenarios are applied in order during data generation.')

    st.subheader('Manage Scenarios')
    if not st.session_state.scenarios:
        st.write(
            'No scenarios configured. Add one below or load a template from the sidebar.')

    for i, s in enumerate(st.session_state.scenarios):
        expander_title = f"**{i+1}. {s.get('name', 'Untitled')}** (`{s.get('type')}` on `{s.get('target_dataset')}.{s.get('target_column')}`)"
        with st.expander(expander_title):
            st.json(s)
            if st.button(f'Delete Scenario {i+1}', key=f'delscn{i}'):
                st.session_state.scenarios.pop(i)
                st.rerun()

    st.markdown('---')
    st.subheader('Add New Scenario')
    with st.form('add_scenario', border=True):
        s_name = st.text_input('Scenario name')
        s_type = st.selectbox(
            'Type', ['shock', 'seasonal', 'fraud_outlier', 'correlation'])
        s_target_ds = st.selectbox('Target dataset', DATASET_OPTIONS)
        s_target_col = st.text_input('Target column', 'InvoiceAmount')
        s_seed = int(st.number_input('Scenario Seed', value=seed))

        sc_details = {}
        if s_type == 'shock':
            c1, c2 = st.columns(2)
            s_start = c1.date_input('Start date')
            s_end = c2.date_input('End date')
            s_magnitude = st.number_input(
                'Magnitude', value=0.7, format='%.3f')
            s_mode = st.selectbox('Mode', ['multiplier', 'additive'])
            sc_details = {'start': str(s_start), 'end': str(
                s_end), 'magnitude': float(s_magnitude), 'mode': s_mode}
        elif s_type == 'seasonal':
            s_month_json = st.text_area(
                'Month multipliers (JSON)', value='{"12": 1.5, "1": 1.2}')
            try:
                sc_details = {'month_multipliers': json.loads(s_month_json)}
            except json.JSONDecodeError:
                st.error("Invalid JSON for month multipliers.")
                sc_details = None
        elif s_type == 'fraud_outlier':
            c1, c2 = st.columns(2)
            s_pct = c1.number_input(
                'Fraction of rows (0-1)', 0.0, 1.0, 0.01, 0.001, '%.4f')
            s_mult = c2.number_input(
                'Outlier multiplier', 1.0, 100.0, 5.0, 0.5)
            sc_details = {'pct': float(s_pct), 'multiplier': float(s_mult)}
        elif s_type == 'correlation':
            c1, c2 = st.columns(2)
            s_source = c1.text_input('Source column', 'ProjectHours')
            s_coef = c2.number_input(
                'Correlation coefficient (-1 to 1)', -1.0, 1.0, 0.6, 0.1)
            sc_details = {'source_col': s_source, 'coef': float(s_coef)}

        if st.form_submit_button('Add Scenario'):
            if sc_details is not None:
                sc = {'name': s_name or f'scn_{s_type}', 'type': s_type,
                      'target_dataset': s_target_ds, 'target_column': s_target_col, 'seed': s_seed}
                sc.update(sc_details)
                st.session_state.scenarios.append(sc)
                st.success('Scenario added.')
                st.rerun()

# ----------------------------
# Tab 3: Generate & Download
# ----------------------------
with tab3:
    st.header('Generate & Download')
    st.sidebar.markdown('---')
    st.sidebar.header('Generate Datasets')
    datasets_to_gen = st.sidebar.multiselect(
        'Datasets to generate', DATASET_OPTIONS, default=DATASET_OPTIONS)

    if st.sidebar.button('🚀 Generate Data Now', use_container_width=True, type="primary"):
        with st.spinner('Generating datasets... this may take a moment.'):
            faker = set_seed(seed, locale=faker_locale)
            generated = {}

            # Masters first
            cust_df = generate_customer_master(
                300, country_choices, DEFAULT_REGIONS, faker, seed)
            if 'Customer_Master' in datasets_to_gen:
                generated['Customer_Master'] = apply_custom_columns_vectorized(
                    cust_df.copy(), 'Customer_Master')

            vend_df = generate_vendor_master(
                200, country_choices, DEFAULT_REGIONS, faker, seed+1)
            if 'Vendor_Master' in datasets_to_gen:
                generated['Vendor_Master'] = apply_custom_columns_vectorized(
                    vend_df.copy(), 'Vendor_Master')

            # Transactions that depend on masters
            if 'Revenue_Invoices' in datasets_to_gen:
                rev = generate_revenue_invoices(
                    products, start_date, end_date, freq, cust_df, industry, faker, seed)
                rev = inject_outliers_vectorized(
                    rev, ['InvoiceAmount'], freq=outlier_freq, mag=outlier_mag, seed=seed)
                generated['Revenue_Invoices'] = apply_custom_columns_vectorized(
                    rev, 'Revenue_Invoices')

            if 'Debtors_Aggregated' in datasets_to_gen:
                inv_src = generated.get('Revenue_Invoices', pd.DataFrame())
                debt = generate_debtors_from_invoices(inv_src, freq='M')
                debt = inject_outliers_vectorized(
                    debt, ['ClosingBalance'], freq=outlier_freq, mag=outlier_mag, seed=seed)
                generated['Debtors_Aggregated'] = apply_custom_columns_vectorized(
                    debt, 'Debtors_Aggregated')

            if 'Purchases' in datasets_to_gen:
                purch = generate_purchases(
                    vend_df, products, start_date, end_date, freq, industry, faker, seed+3)
                purch = inject_outliers_vectorized(
                    purch, ['PurchaseAmount'], freq=outlier_freq, mag=outlier_mag, seed=seed+3)
                generated['Purchases'] = apply_custom_columns_vectorized(
                    purch, 'Purchases')

            # Other datasets
            if 'PPE_Register' in datasets_to_gen:
                ppe = generate_ppe_register(
                    300, start_date, end_date, country_choices, DEFAULT_REGIONS, faker, seed+2)
                ppe = inject_outliers_vectorized(
                    ppe, ['Cost'], freq=outlier_freq, mag=outlier_mag, seed=seed+2)
                generated['PPE_Register'] = apply_custom_columns_vectorized(
                    ppe, 'PPE_Register')

            if 'Inventory' in datasets_to_gen:
                inv = generate_inventory_snapshots(
                    products, start_date, end_date, freq, seed+4)
                inv = inject_outliers_vectorized(
                    inv, ['InventoryValue'], freq=outlier_freq, mag=outlier_mag, seed=seed+4)
                generated['Inventory'] = apply_custom_columns_vectorized(
                    inv, 'Inventory')

            if 'Operational' in datasets_to_gen:
                op = generate_operational_dataset(
                    industry, start_date, end_date, freq, None, faker, seed+10)
                config_key = f"{industry}_Operational" if get_dataset_config(
                    f"{industry}_Operational") else 'Operational'
                generated['Operational'] = apply_custom_columns_vectorized(
                    op, config_key)

            # Apply scenarios
            for sc in st.session_state.scenarios:
                target_ds = sc.get('target_dataset')
                if target_ds in generated:
                    df = generated[target_ds]
                    if sc['type'] == 'shock':
                        df = apply_shock(
                            df, sc['target_column'], sc['start'], sc['end'], sc['magnitude'], sc['mode'])
                    elif sc['type'] == 'seasonal':
                        df = apply_seasonal(
                            df, sc['target_column'], sc['month_multipliers'])
                    elif sc['type'] == 'fraud_outlier':
                        df = inject_fraud_outliers(df, sc['target_column'], sc.get(
                            'pct', 0.01), sc.get('multiplier', 5.0), seed=sc.get('seed'))
                    elif sc['type'] == 'correlation':
                        df = apply_correlation(
                            df, sc['source_col'], sc['target_column'], sc.get('coef', 0.0))
                    generated[target_ds] = df
                else:
                    st.warning(
                        f"Scenario '{sc.get('name')}' targets '{target_ds}', which was not generated. Skipping.")

            st.session_state.generated_data = generated
            st.success(
                'Data generation complete! View previews and download below.')
            st.rerun()

    if 'generated_data' in st.session_state and st.session_state.generated_data:
        st.markdown('### Previews & Downloads')
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for name, df in st.session_state.generated_data.items():
                st.subheader(f"`{name}` — {len(df):,} rows")
                st.dataframe(df.head(100))
                csv = df.to_csv(index=False).encode('utf-8')
                zf.writestr(f"{name}.csv", csv)

        zip_buffer.seek(0)
        st.download_button('⬇️ Download ALL as ZIP', zip_buffer.getvalue(
        ), file_name='synthetic_datasets.zip', use_container_width=True)
