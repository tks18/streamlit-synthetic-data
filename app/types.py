from typing import TypedDict, Literal, List, Dict, Tuple
from datetime import date


class TIndustryOpRangeConfig(TypedDict):
    name: str
    type: Literal["range"]
    min: float | int
    max: float | int
    float: bool


class TIndustryOpChoiceConfig(TypedDict):
    name: str
    type: Literal["choice"]
    options: List[str]


class TIndustryConfig(TypedDict):
    products: List[str]
    operational: List[TIndustryOpChoiceConfig | TIndustryOpRangeConfig]


class TCustomColumnFormulaConfig(TypedDict):
    type: Literal["formula"]
    expr: str


class TCustomColumnRangeConfig(TypedDict):
    type: Literal["range"]
    min: float
    max: float


class TCustomColumnChoiceConfig(TypedDict):
    type: Literal["choice"]
    options: List[str]


TCustomColumnEntry = Tuple[str, TCustomColumnFormulaConfig |
                           TCustomColumnRangeConfig | TCustomColumnChoiceConfig]


class TAppStateConfig(TypedDict):
    industry: str
    industry_kpi: Dict[str, TIndustryConfig]
    products: List[str]
    countries: List[str]
    country_config: Dict[str, List[str]]
    start_date: date
    end_date: date
    frequency: str
    seed: int
    faker_locale: str
    outlier_frequency: float
    outlier_magnitude: float
    custom_columns: Dict[str, List[TCustomColumnEntry]]
    scenarios: list
    total_customers: int
    total_vendors: int
    total_assets: int


class TProfileConfig(TypedDict):
    industry: str
    products: List[str]
    countries: List[str]
    start_date: date
    end_date: date
    frequency: str
    seed: int
    faker_locale: str
    outlier_frequency: float
    outlier_magnitude: float
    custom_columns: Dict[str, List[TCustomColumnEntry]]
    scenarios: list
    total_customers: int
    total_vendors: int
    total_assets: int
