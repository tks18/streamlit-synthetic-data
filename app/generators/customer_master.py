import random
from typing import Dict
from faker import Faker
import pandas as pd
import numpy as np
import uuid
from datetime import datetime, date

from app.types import TAppStateConfig


def _pan():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5)) + \
        ''.join(random.choices('0123456789', k=4)) + \
        random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')


def _gstin(pan, state_code):
    # Simple synthetic GSTIN pattern: <2-digit-state><PAN><2-digit><A1Z><char>
    return f"{state_code:02d}{pan}{random.randint(10, 99)}A1Z{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"


def _cin(listing_char: str, region: str, business_type: str, reg_date: date) -> str:
    """
    Simple synthetic CIN generator following the pattern:
    <L/U><5-digit-industry><2-char-region-approx><4-digit-year><3-char-ownership><6-digit-regno>
    - Not validating against MCA; just following the pattern for synthetic realism.
    """
    industry_code = f"{random.randint(10000, 99999)}"
    # Take first two alpha chars of region (fallback 'XX')
    region_alpha = "".join(
        [c for c in (region or "") if c.isalpha()][:2]).upper()
    region_code = region_alpha if len(region_alpha) == 2 else "XX"
    year = reg_date.year if hasattr(reg_date, "year") else datetime.now().year
    ownership_map = {
        "Private Limited": "PTC",
        "Public Limited": "PLC",
        "LLP": "LLP",
        "Proprietor": "PRT",
        "Government": "GOV",
        "NGO": "NGO"
    }
    ownership = ownership_map.get(business_type, "PTC")
    reg_number = f"{random.randint(1, 999999):06d}"
    return f"{listing_char}{industry_code}{region_code}{year}{ownership}{reg_number}"


def _lei():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=20))


def generate_customer_master(state_config: TAppStateConfig, faker: Faker = Faker(), generated: Dict[str, pd.DataFrame] = {}) -> pd.DataFrame:
    np.random.seed(state_config.get("seed", 42))
    random.seed(state_config.get("seed", 42))
    faker.seed_instance(state_config.get("seed", 42))

    countries = state_config["countries"]
    default_regions = state_config["country_config"]
    total_customers = state_config["total_customers"]
    end_date = pd.to_datetime(state_config.get("end_date"))

    rows = []

    for _ in range(total_customers):
        country = np.random.choice(countries)
        region = np.random.choice(default_regions.get(country, ["Unknown"]))
        industry = np.random.choice(
            list(state_config["industry_kpi"].keys()) or ["General"])
        segment = np.random.choice(
            ["SME", "Enterprise", "Startup", "Government", "NGO"])

        company_name = faker.company()
        domain = company_name.replace(
            " ", "").replace(",", "").lower() + ".com"
        contact_name = faker.name()
        email = f"{contact_name.split()[0].lower()}@{domain}"
        phone = faker.phone_number()

        is_indian = str(country).strip().lower() in ("india", "in")

        listing_status = np.random.choice(["Listed", "Unlisted"], p=[0.2, 0.8])
        listed_flag = "Yes" if listing_status == "Listed" else "No"
        listing_char = "L" if listing_status == "Listed" else "U"

        pan = _pan() if is_indian else None
        gstin = _gstin(pan, random.randint(1, 38)) if is_indian else None

        reg_date = faker.date_between(
            start_date=datetime(2010, 1, 1).date(), end_date=end_date)
        business_type = np.random.choice(
            ["Private Limited", "LLP", "Proprietor", "Public Limited", "Government", "NGO"])
        cin = _cin(listing_char, region, business_type,
                   reg_date) if is_indian else None

        lei = _lei()

        payment_terms = np.random.choice(
            ["Immediate", "15 Days", "30 Days", "45 Days", "60 Days"],
            p=[0.05, 0.25, 0.4, 0.2, 0.1]
        )

        credit_rating = np.clip(np.random.normal(700, 80), 300, 900)

        risk_score = round(np.random.uniform(0, 1) *
                           (900 - credit_rating) / 9, 2)
        compliance_score = round(np.random.uniform(60, 100), 2)
        default_prob = round((900 - credit_rating) / 1000, 3)

        last_purchase_date = faker.date_between(
            start_date=reg_date, end_date=end_date)
        is_active = (datetime.now().date() - last_purchase_date).days < 180
        tenure_days = (datetime.now().date() - reg_date).days

        emp_count = int(abs(np.random.normal(150, 75)))

        is_related_party = np.random.choice(["Yes", "No"], p=[0.1, 0.9])
        tax_category = np.random.choice(
            ["Regular", "Composition", "Exempt"], p=[0.7, 0.2, 0.1]) if is_indian else None
        entity_category = np.random.choice(
            ["Corporate", "Individual", "Partnership", "Trust"], p=[0.6, 0.2, 0.15, 0.05])
        account_status = np.random.choice(
            ["Active", "Suspended", "Dormant", "Blacklisted"], p=[0.85, 0.05, 0.08, 0.02])

        customer_origin = "India" if is_indian else "Outside India"

        rows.append({
            "CustomerID": f"CUST_{uuid.uuid4().hex[:8]}",
            "CustomerName": company_name,
            "ContactPerson": contact_name,
            "Email": email,
            "Phone": phone,
            "Website": f"www.{domain}",
            "Country": country,
            "State": region,
            "CustomerSegment": segment,
            "Industry": industry,
            "BusinessType": business_type,
            "EmployeeCount": emp_count,
            "ListedFlag": listed_flag,           # Yes/No
            "ListingStatus": listing_status,
            "CustomerOrigin": customer_origin,   # India / Outside India
            "PAN": pan,
            "GSTIN": gstin,
            "CIN": cin,
            "LEI": lei,
            "TaxCategory": tax_category,
            "EntityCategory": entity_category,
            "IsRelatedParty": is_related_party,
            "AccountStatus": account_status,
            "CreditRating": int(credit_rating),
            "PaymentTerms": payment_terms,
            "RiskScore": risk_score,
            "ComplianceScore": compliance_score,
            "DefaultProbability": default_prob,
            "RegistrationDate": reg_date,
            "IsActiveCustomer": is_active,
            "CustomerTenureDays": tenure_days,
        })

    df = pd.DataFrame(rows)
    return df
