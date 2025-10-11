from typing import Dict
from faker import Faker
import pandas as pd
import numpy as np
import uuid

from app.helpers.general import date_range
from app.mods import inject_outliers_vectorized
from app.types import TAppStateConfig


def generate_purchases(state_config: TAppStateConfig, faker: Faker = Faker(), generated: Dict[str, pd.DataFrame] = {}):
    seed = state_config["seed"]
    np.random.seed(seed)
    industry = state_config["industry"]
    products = state_config["products"]
    start_date = state_config["start_date"]
    end_date = state_config["end_date"]
    freq = state_config["frequency"]
    outlier_freq = state_config["outlier_frequency"]
    outlier_mag = state_config["outlier_magnitude"]
    dates = date_range(start_date, end_date, freq)
    vendors_df = generated.get("Vendor_Master", pd.DataFrame())
    purchases_per_period = np.random.randint(10, 20)
    rows = []

    if vendors_df.empty:
        return pd.DataFrame()

    for d in dates:
        period_vendors = vendors_df.sample(
            n=min(len(vendors_df), purchases_per_period), random_state=seed)

        vendor_choices = np.random.choice(products, size=len(period_vendors))
        base_amounts = np.random.randint(
            2000, 250000, size=len(period_vendors))

        # Categorical enhancements
        purchase_types = np.random.choice(
            ["Standard", "Return", "CreditNote", "Adjustment"], size=len(period_vendors), p=[0.7, 0.1, 0.1, 0.1])
        procurement_channels = np.random.choice(
            ["Direct", "Distributor", "Online", "Auction"], size=len(period_vendors), p=[0.5, 0.3, 0.15, 0.05])
        priority_levels = np.random.choice(
            ["High", "Medium", "Low"], size=len(period_vendors), p=[0.2, 0.6, 0.2])
        payment_modes = np.random.choice(
            ["BankTransfer", "Cheque", "CreditCard", "UPI", "Cash"], size=len(period_vendors), p=[0.5, 0.2, 0.15, 0.1, 0.05])
        contract_terms = np.random.choice(
            ["One-Time", "Annual", "Quarterly", "Project-Based"], size=len(period_vendors), p=[0.5, 0.2, 0.2, 0.1])

        # Numerical enhancements
        unit_count = np.random.randint(1, 100, size=len(period_vendors))
        unit_price = base_amounts / unit_count
        discounts = np.round(np.random.uniform(
            0, 0.25, size=len(period_vendors)), 3)
        tax_rates = np.random.choice(
            [0.05, 0.12, 0.18], size=len(period_vendors), p=[0.2, 0.3, 0.5])
        freight_charges = np.random.randint(
            200, 5000, size=len(period_vendors))
        service_fees = np.random.randint(100, 2000, size=len(period_vendors))
        cost_amounts = (base_amounts * (1 - discounts) *
                        (1 + tax_rates)) + freight_charges + service_fees
        margin_pct = np.round(np.random.normal(
            0.15, 0.05, len(period_vendors)), 3).clip(0.01, 0.3)
        margin_amount = cost_amounts * margin_pct
        invoice_weight = np.round(np.random.uniform(
            0.5, 100.0, len(period_vendors)), 2)

        for i, vend in enumerate(period_vendors.itertuples(index=False)):
            invoice_date = d + pd.Timedelta(days=int(np.random.randint(0, 5)))
            rows.append({
                "Industry": industry,
                "Product": vendor_choices[i],
                "Date": invoice_date.date(),
                "PurchaseInvoiceID": str(uuid.uuid4().int)[:12],
                "VendorID": vend.VendorID,
                "VendorType": vend.VendorType,
                "Country": vend.Country,
                "State": vend.State,
                "PurchaseType": purchase_types[i],
                "ProcurementChannel": procurement_channels[i],
                "PriorityLevel": priority_levels[i],
                "PaymentMode": payment_modes[i],
                "ContractTerm": contract_terms[i],
                "UnitCount": unit_count[i],
                "UnitPrice": float(round(unit_price[i], 2)),
                "DiscountRate": discounts[i],
                "TaxRate": tax_rates[i],
                "FreightCharge": float(freight_charges[i]),
                "ServiceFee": float(service_fees[i]),
                "CostAmount": float(round(cost_amounts[i], 2)),
                "MarginAmount": float(round(margin_amount[i], 2)),
                "MarginPct": margin_pct[i],
                "InvoiceWeight": invoice_weight[i],
                "PurchaseAmount": float(round(cost_amounts[i] + margin_amount[i], 2))
            })

    df = pd.DataFrame(rows)
    df = inject_outliers_vectorized(
        df, ['PurchaseAmount'], freq=outlier_freq, mag=outlier_mag, seed=seed+7)
    return df
