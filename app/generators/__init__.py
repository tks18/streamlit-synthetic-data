from typing import Callable, Dict

from faker import Faker
import pandas as pd

from app.generators.customer_master import generate_customer_master
from app.generators.vendor_master import generate_vendor_master
from app.generators.revenue import generate_revenue_invoices
from app.generators.purchases import generate_purchases
from app.generators.debtors import generate_debtors_from_invoices
from app.generators.ppe import generate_ppe_register
from app.generators.inventory import generate_inventory_snapshots
from app.generators.operational import generate_operational_dataset

from app.types import TAppStateConfig


TGeneratorFunction = Callable[[TAppStateConfig,
                               Faker, Dict[str, pd.DataFrame]], pd.DataFrame]


generator_config: Dict[str, TGeneratorFunction] = {
    "Customer_Master": generate_customer_master,
    "Vendor_Master": generate_vendor_master,
    "PPE_Register": generate_ppe_register,
    "Revenue_Invoices": generate_revenue_invoices,
    "Purchases": generate_purchases,
    "Debtors": generate_debtors_from_invoices,
    "Inventory_Snapshots": generate_inventory_snapshots,
    "Operational_Dataset": generate_operational_dataset,
}
