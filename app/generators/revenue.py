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
                    "InvoiceID": str(uuid.uuid4().int)[:12], "CustomerID": cust.CustomerID,
                    "CustomerSegment": cust.CustomerSegment, "Country": cust.Country, "State": cust.State,
                    "InvoiceAmount": float(amt), "DueDate": due_date.date(),
                    "PaymentDate": (payment_date.date() if pd.notna(payment_date) else pd.NaT),
                    "PaidAmount": float(round(paid_amount, 2)), "PaymentStatus": pay_flag
                })
    df = pd.DataFrame(rows)
    df = inject_outliers_vectorized(
        df, ['InvoiceAmount'], freq=outlier_freq, mag=outlier_mag, seed=seed)
    if not df.empty:
        df["Outstanding"] = df["InvoiceAmount"] - df["PaidAmount"]
    return df
