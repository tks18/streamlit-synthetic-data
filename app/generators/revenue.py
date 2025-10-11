from typing import Dict
from faker import Faker
import pandas as pd
import numpy as np
import uuid

from app.mods import inject_outliers_vectorized
from app.helpers.general import date_range
from app.types import TAppStateConfig


def generate_revenue_invoices(state_config: TAppStateConfig, faker: Faker = Faker(), generated: Dict[str, pd.DataFrame] = {}):
    seed = state_config["seed"]
    np.random.seed(seed)
    industry = state_config["industry"]
    products = state_config["products"]
    start_date = state_config["start_date"]
    end_date = state_config["end_date"]
    freq = state_config["frequency"]
    dates = date_range(start_date, end_date, freq)
    customers_df = generated.get("Customer_Master", pd.DataFrame())
    outlier_freq = state_config["outlier_frequency"]
    outlier_mag = state_config["outlier_magnitude"]
    invoice_per_product_per_period = np.random.randint(10, 20)
    rows = []

    if customers_df.empty:
        return pd.DataFrame()

    for product in products:
        for d in dates:
            n_sample = min(len(customers_df), invoice_per_product_per_period)
            period_customers = customers_df.sample(
                n=n_sample, replace=False, random_state=seed)

            base_amounts = np.random.randint(
                5000, 200000, size=len(period_customers))

            # Synthetic categorical dimensions
            sales_channels = np.random.choice(
                ["Online", "Retail", "Distributor", "Direct", "Partner"], size=len(period_customers), p=[0.25, 0.25, 0.2, 0.2, 0.1])
            contract_types = np.random.choice(
                ["Subscription", "One-Time", "Retainer", "Volume-Based"], size=len(period_customers), p=[0.4, 0.3, 0.2, 0.1])
            payment_modes = np.random.choice(
                ["BankTransfer", "CreditCard", "Cheque", "UPI", "Cash"], size=len(period_customers), p=[0.5, 0.25, 0.1, 0.1, 0.05])
            salesperson_tiers = np.random.choice(
                ["Junior", "Mid", "Senior", "KeyAccount"], size=len(period_customers), p=[0.3, 0.4, 0.25, 0.05])
            invoice_types = np.random.choice(
                ["Standard", "CreditNote", "DebitNote", "Adjustment"], size=len(period_customers), p=[0.7, 0.1, 0.1, 0.1])
            promotion_applied = np.random.choice(
                ["None", "Seasonal", "Loyalty", "Referral"], size=len(period_customers), p=[0.6, 0.2, 0.1, 0.1])
            customer_tiers = np.random.choice(
                ["Platinum", "Gold", "Silver", "Bronze"], size=len(period_customers), p=[0.1, 0.3, 0.4, 0.2])
            market_segments = np.random.choice(
                ["B2B", "B2C", "Mixed"], size=len(period_customers), p=[0.5, 0.4, 0.1])

            # Synthetic numerical enrichments
            unit_count = np.random.randint(1, 50, size=len(period_customers))
            unit_price = base_amounts / unit_count
            discounts = np.round(np.random.uniform(
                0, 0.25, size=len(period_customers)), 3)
            tax_rates = np.random.choice([0.05, 0.12, 0.18], size=len(
                period_customers), p=[0.2, 0.3, 0.5])
            freight_charges = np.random.randint(
                200, 5000, size=len(period_customers))
            service_fees = np.random.randint(
                100, 2000, size=len(period_customers))
            profit_margin_pct = np.round(np.random.normal(
                0.25, 0.08, len(period_customers)), 3).clip(0.05, 0.6)
            customer_ltv = np.random.randint(
                10000, 500000, size=len(period_customers))
            invoice_weight = np.round(np.random.uniform(
                0.5, 50.0, len(period_customers)), 2)

            net_amounts = base_amounts * (1 - discounts)
            taxed_amounts = net_amounts * (1 + tax_rates)
            total_amounts = taxed_amounts + freight_charges + service_fees
            costs = total_amounts * (1 - profit_margin_pct)
            margin_amount = total_amounts - costs
            total_discount_amount = base_amounts * discounts
            tax_amount = net_amounts * tax_rates
            net_revenue = net_amounts
            gross_revenue = base_amounts

            for i, cust in enumerate(period_customers.itertuples(index=False)):
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
                    paid_amount = total_amounts[i]
                elif pay_flag == "PartiallyPaid":
                    payment_date = due_date + \
                        pd.Timedelta(days=int(np.random.randint(1, 60)))
                    paid_amount = total_amounts[i] * \
                        np.random.uniform(0.3, 0.9)
                else:
                    payment_date, paid_amount = pd.NaT, 0.0

                rows.append({
                    "Industry": industry,
                    "Product": product,
                    "Date": invoice_date.date(),
                    "InvoiceID": str(uuid.uuid4().int)[:12],
                    "CustomerID": cust.CustomerID,
                    "CustomerSegment": cust.CustomerSegment,
                    "Country": cust.Country,
                    "State": cust.State,
                    "SalesChannel": sales_channels[i],
                    "ContractType": contract_types[i],
                    "PaymentMode": payment_modes[i],
                    "SalespersonTier": salesperson_tiers[i],
                    "InvoiceType": invoice_types[i],
                    "PromotionApplied": promotion_applied[i],
                    "CustomerTier": customer_tiers[i],
                    "MarketSegment": market_segments[i],
                    "UnitCount": unit_count[i],
                    "UnitPrice": float(round(unit_price[i], 2)),
                    "TotalDiscountAmount": float(round(total_discount_amount[i], 2)),
                    "TaxAmount": float(round(tax_amount[i], 2)),
                    "FreightCharge": float(freight_charges[i]),
                    "ServiceFee": float(service_fees[i]),
                    "CostAmount": float(round(costs[i], 2)),
                    "MarginAmount": float(round(margin_amount[i], 2)),
                    "ProfitMarginPct": profit_margin_pct[i],
                    "CustomerLTV": float(customer_ltv[i]),
                    "InvoiceWeight": invoice_weight[i],
                    "InvoiceAmount": float(round(total_amounts[i], 2)),
                    "DueDate": due_date.date(),
                    "PaymentDate": (payment_date.date() if pd.notna(payment_date) else pd.NaT),
                    "PaidAmount": float(round(paid_amount, 2)),
                    "PaymentStatus": pay_flag,
                })

    df = pd.DataFrame(rows)
    df = inject_outliers_vectorized(
        df, ['InvoiceAmount'], freq=outlier_freq, mag=outlier_mag, seed=seed)

    if not df.empty:
        df["Outstanding"] = df["InvoiceAmount"] - df["PaidAmount"]

    return df
