import os
import sys
import json
import pandas as pd

from app.helpers.countries import get_country_states_dict

# ----------------------------
# Config & folders
# ----------------------------
APP_MAIN_TITLE = "Shan's Dataverse"
APP_TITLE = "📈 Enhanced Data Cockpit — Finance + Ops"
BASE_DIR = os.path.dirname(os.path.abspath(
    str(sys.modules["__main__"].__file__)))
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
STATIC_DIR = os.path.join(BASE_DIR, "static")
INDUSTRY_KPIS_DIR = os.path.join(STATIC_DIR, "industries.json")

os.makedirs(PROFILES_DIR, exist_ok=True)

# ----------------------------
# Default Data Schemas
# ----------------------------
DEFAULT_START_DATE = "2020-01-01"
DEFAULT_END_DATE = "2022-12-31"

# Load JSON
with open(INDUSTRY_KPIS_DIR, "r", encoding="utf-8") as f:
    INDUSTRY_KPIS = json.load(f)

DEFAULT_REGIONS = get_country_states_dict()

# Default Region Choices
DEFAULT_REGION_CHOICE = {
    "India": DEFAULT_REGIONS["India"], "United States": DEFAULT_REGIONS["United States"], "United Kingdom": DEFAULT_REGIONS["United Kingdom"]}

# Default Choices
DEF_INDUSTRY = list(INDUSTRY_KPIS.keys())[0]
DEF_PRODUCTS = INDUSTRY_KPIS[DEF_INDUSTRY]['products']
DEF_FREQ = 'ME'
DEF_SEED = 42
DEF_FAKER_LOCALE = 'en_IN'
DEF_OUTLIER_FREQ = 0.05
DEF_OUTLIER_MAG = 2
DEF_START_DATE = pd.to_datetime(DEFAULT_START_DATE).date()
DEF_END_DATE = pd.to_datetime(DEFAULT_END_DATE).date()

PROFILE_CONFIG = [
    ('key_industry', 'industry', DEF_INDUSTRY),
    ('key_products', 'products', DEF_PRODUCTS),
    ('key_countries', 'countries', list(DEFAULT_REGION_CHOICE.keys())),
    ('key_start_date', 'start_date', DEF_START_DATE),
    ('key_end_date', 'end_date', DEF_END_DATE),
    ('key_freq', 'frequency', DEF_FREQ),
    ('key_seed', 'seed', DEF_SEED),
    ('key_faker_locale', 'faker_locale', DEF_FAKER_LOCALE),
    ('key_outlier_freq', 'outlier_frequency', DEF_OUTLIER_FREQ),
    ('key_outlier_mag', 'outlier_magnitude', DEF_OUTLIER_MAG),
    ('key_custom_columns', 'custom_columns', {}),
    ('key_scenarios', 'scenarios', [])
]
