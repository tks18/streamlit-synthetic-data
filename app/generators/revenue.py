import pandas as pd
import numpy as np
import uuid

from app.helpers.general import date_range, set_seed


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
