from typing import Dict
from faker import Faker
import pandas as pd
import numpy as np

from app.mods import inject_outliers_vectorized
from app.types import TAppStateConfig


def generate_debtors_from_invoices(state_config: TAppStateConfig, faker: Faker = Faker(), generated: Dict[str, pd.DataFrame] = {}):
    seed = state_config["seed"]
    outlier_freq = state_config["outlier_frequency"]
    outlier_mag = state_config["outlier_magnitude"]

    invoices_df = generated.get("Revenue_Invoices", pd.DataFrame())
    cust_master_df = generated.get("Customer_Master", pd.DataFrame())

    if invoices_df.empty or cust_master_df.empty:
        return pd.DataFrame()

    np.random.seed(seed)

    # --- Aggregate base data ---
    df = invoices_df.copy()
    df["Period"] = pd.to_datetime(df["Date"]).dt.to_period("M")

    agg = df.groupby(["Period", "CustomerID", "CustomerSegment", "Country", "State"]).agg(
        Credit=("InvoiceAmount", "sum"),
        Collections=("PaidAmount", "sum"),
    ).reset_index()

    agg["ClosingBalance"] = agg["Credit"] - agg["Collections"]
    agg["DSO_Est"] = np.where(
        agg["Credit"] > 0, (agg["ClosingBalance"] / agg["Credit"]) * 30, 0
    )
    agg["PeriodEnd"] = agg["Period"].dt.to_timestamp(how='end').dt.date

    # --- Merge with Customer Master ---
    merged = agg.merge(
        cust_master_df[
            [
                "CustomerID", "CreditRating", "PaymentTerms", "RiskScore",
                "DefaultProbability", "CustomerOrigin", "Industry",
                "EntityCategory", "IsRelatedParty", "CustomerTenureDays"
            ]
        ],
        on="CustomerID",
        how="left"
    ).sort_values(by=["CustomerID", "Period"])

    # --- Opening Balance Simulation ---
    opening_balances = []
    for cust_id, grp in merged.groupby("CustomerID"):
        grp = grp.sort_values("Period")
        base_opening = np.random.uniform(0.2, 0.8) * grp["Credit"].iloc[0]
        credit_factor = (100 - grp["CreditRating"].iloc[0]) / 100
        risk_factor = grp["RiskScore"].iloc[0] / 100
        adj_opening = base_opening * (0.5 + credit_factor + risk_factor)
        grp.loc[grp.index[0], "OpeningBalance"] = round(adj_opening, 2)
        for i in range(1, len(grp)):
            prev_close = grp.iloc[i - 1]["ClosingBalance"]
            noise = np.random.normal(0, 0.05) * prev_close
            grp.loc[grp.index[i], "OpeningBalance"] = max(
                prev_close + noise, 0)
        opening_balances.append(grp)
    merged = pd.concat(opening_balances, ignore_index=True)

    # --- Derived / Behavioral Metrics ---
    merged["Overdue%"] = np.clip(
        np.random.normal(0.15, 0.05, len(merged)), 0, 1)
    merged["CollectionEfficiency"] = 1 - merged["Overdue%"]
    merged["AgingBucket"] = pd.cut(
        merged["DSO_Est"],
        bins=[-1, 30, 60, 90, 180, np.inf],
        labels=["0-30", "31-60", "61-90", "91-180", "180+"],
    )

    # --- Business / Relationship Attributes ---
    merged["EngagementTenureMonths"] = (
        merged["CustomerTenureDays"] / 30).astype(int)
    merged["BusinessSegment"] = np.random.choice(
        ["Enterprise", "Mid-Market", "SME", "Startup"], len(merged)
    )
    merged["ContractType"] = np.random.choice(
        ["Fixed", "Time & Material", "Retainer", "Ad-hoc"], len(merged)
    )
    merged["ContractRenewalFlag"] = np.where(
        merged["EngagementTenureMonths"] > 24, "Yes", "No"
    )

    # --- Credit / Risk Attributes ---
    merged["CreditLimit"] = np.round(
        np.random.uniform(1.2, 2.5, len(merged)) * merged["Credit"], 2
    )
    merged["CreditUtilization%"] = np.round(
        merged["ClosingBalance"] / merged["CreditLimit"], 3
    ).clip(0, 1)
    merged["RiskCategory"] = pd.cut(
        merged["RiskScore"], bins=[0, 40, 70, 100], labels=["High", "Medium", "Low"]
    )

    merged["Overdue_pct"] = pd.to_numeric(
        merged["Overdue%"], errors="coerce").fillna(0)

    merged["ProvisionStage"] = pd.cut(
        merged["Overdue_pct"],
        bins=[-np.inf, 0.2, 0.5, np.inf],
        labels=["Stage 1", "Stage 2", "Stage 3"]
    )

    # --- Behavior Metrics ---
    merged["AvgPaymentDelayDays"] = np.round(
        merged["DSO_Est"] * np.random.uniform(0.8, 1.2), 0)
    merged["CollectionTrend"] = np.random.choice(
        ["Up", "Stable", "Down"], len(merged))
    merged["BounceCount"] = np.random.poisson(0.3, len(merged))
    merged["AutoDebitEnabled"] = np.random.choice(
        ["Yes", "No"], len(merged), p=[0.6, 0.4])

    # --- Financial Analytics ---
    merged["ReceivablesTurnover"] = np.where(
        merged["ClosingBalance"] > 0,
        merged["Collections"] / merged["ClosingBalance"],
        0
    )
    merged["ExposureRatio"] = (
        merged["ClosingBalance"] / merged["CreditLimit"]).round(2)
    merged["BadDebtEstimate"] = (
        merged["ClosingBalance"] * merged["DefaultProbability"]).round(2)
    merged["LossGivenDefault"] = np.round(
        np.random.uniform(0.2, 0.8, len(merged)), 2)
    merged["ExpectedCreditLoss"] = (
        merged["BadDebtEstimate"] * merged["LossGivenDefault"]).round(2)
    merged["DaysPastDue"] = (merged["Overdue%"] *
                             merged["AvgPaymentDelayDays"]).astype(int)

    # --- Debtor Category Logic ---
    def classify_debtor(row):
        if row["RiskScore"] > 80 and row["Overdue%"] < 0.2:
            return "Prompt Payer"
        elif row["RiskScore"] < 40 or row["Overdue%"] > 0.5:
            return "High Risk"
        else:
            return "Standard"
    merged["DebtorCategory"] = merged.apply(classify_debtor, axis=1)
    merged["DelinquencyFlag"] = np.where(
        merged["AgingBucket"].isin(["91-180", "180+"]), "Yes", "No"
    )

    # --- Reorder Columns ---
    final_cols = [
        "PeriodEnd", "CustomerID", "CustomerSegment", "Country", "State", "Industry",
        "EntityCategory", "CustomerOrigin", "IsRelatedParty",
        "BusinessSegment", "ContractType", "ContractRenewalFlag",
        "OpeningBalance", "Credit", "Collections", "ClosingBalance",
        "CreditLimit", "CreditUtilization%", "ReceivablesTurnover", "ExposureRatio",
        "DSO_Est", "AvgPaymentDelayDays", "DaysPastDue", "Overdue%",
        "CollectionEfficiency", "CollectionTrend", "BounceCount", "AutoDebitEnabled",
        "AgingBucket", "RiskScore", "CreditRating", "RiskCategory", "ProvisionStage",
        "PaymentTerms", "DefaultProbability", "BadDebtEstimate", "LossGivenDefault",
        "ExpectedCreditLoss", "DelinquencyFlag", "DebtorCategory"
    ]
    final_df = merged[final_cols]

    # --- Inject Outliers ---
    final_df = inject_outliers_vectorized(
        final_df, ['ClosingBalance', 'ExpectedCreditLoss'], freq=outlier_freq, mag=outlier_mag, seed=seed + 5
    )

    return final_df
