from typing import Dict
from faker import Faker
import pandas as pd
import numpy as np
import random
import uuid
from datetime import datetime, date

from app.types import TAppStateConfig


def _pan():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5)) + \
        ''.join(random.choices('0123456789', k=4)) + \
        random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')


def _gstin(pan, state_code):
    return f"{state_code:02d}{pan}{random.randint(10, 99)}A1Z{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"


def _cin(listing_char: str, region: str, business_type: str, reg_date: date) -> str:
    industry_code = f"{random.randint(10000, 99999)}"
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


def generate_vendor_master(state_config: TAppStateConfig, faker: Faker = Faker(), generated: Dict[str, pd.DataFrame] = {}):
    seed = state_config["seed"]
    np.random.seed(seed)
    random.seed(seed)
    faker.seed_instance(seed)

    countries = state_config["countries"]
    default_regions = state_config["country_config"]
    total_vendors = state_config["total_vendors"]
    end_date = pd.to_datetime(state_config.get("end_date"))

    rows = []

    for _ in range(total_vendors):
        country = np.random.choice(countries)
        region = np.random.choice(default_regions.get(country, ["Unknown"]))
        supplier_category = np.random.choice(
            ["Raw Material", "Services", "Consulting",
                "Logistics", "Technology", "Facilities"]
        )

        company_name = faker.company()
        contact_name = faker.name()
        domain = company_name.replace(
            " ", "").replace(",", "").lower() + ".com"
        email = f"{contact_name.split()[0].lower()}@{domain}"
        phone = faker.phone_number()

        is_indian = str(country).strip().lower() in ("india", "in")

        # --- Listing, business type & identifiers ---
        listing_status = np.random.choice(
            ["Listed", "Unlisted"], p=[0.15, 0.85])
        listing_char = "L" if listing_status == "Listed" else "U"
        listed_flag = "Yes" if listing_status == "Listed" else "No"

        business_type = np.random.choice(
            ["Private Limited", "LLP", "Proprietor",
                "Public Limited", "Government", "NGO"]
        )

        first_purchase_date = faker.date_between(
            start_date=datetime(2010, 1, 1).date(), end_date=end_date)

        pan = _pan() if is_indian else None
        gstin = _gstin(pan, random.randint(1, 38)) if is_indian else None
        cin = _cin(listing_char, region, business_type,
                   first_purchase_date) if is_indian else None

        lei = _lei()

        # --- Vendor metrics ---
        payment_terms = np.random.choice(
            ["Immediate", "15 Days", "30 Days", "45 Days", "60 Days"], p=[0.05, 0.25, 0.4, 0.2, 0.1]
        )
        avg_lead_time = int(abs(np.random.normal(20, 10)))  # days
        on_time_delivery = round(np.random.uniform(85, 100), 2)

        reliability_score = round(np.random.uniform(60, 100), 2)
        compliance_score = round(np.random.uniform(70, 100), 2)

        last_txn_date = faker.date_between(
            start_date=first_purchase_date, end_date=end_date)
        blacklisted_flag = (datetime.now().date() - last_txn_date).days < 180
        tenure_days = (datetime.now().date() - first_purchase_date).days

        is_preferred = np.random.choice(["Yes", "No"], p=[0.3, 0.7])
        tax_category = np.random.choice(
            ["Regular", "Composition", "Exempt"], p=[0.7, 0.2, 0.1]
        ) if is_indian else None
        vendor_origin = "India" if is_indian else "Outside India"

        rows.append({
            "VendorID": f"VEND_{uuid.uuid4().hex[:8]}",
            "VendorName": company_name,
            "ContactPerson": contact_name,
            "Email": email,
            "Phone": phone,
            "Website": f"www.{domain}",
            "Country": country,
            "State": region,
            "SupplierCategory": supplier_category,
            "BusinessType": business_type,
            "ListedFlag": listed_flag,
            "ListingStatus": listing_status,
            "VendorOrigin": vendor_origin,
            "PAN": pan,
            "GSTIN": gstin,
            "CIN": cin,
            "LEI": lei,
            "TaxCategory": tax_category,
            "PaymentTerms": payment_terms,
            "AvgLeadTimeDays": avg_lead_time,
            "OnTimeDeliveryPct": on_time_delivery,
            "ReliabilityScore": reliability_score,
            "ComplianceScore": compliance_score,
            "OnboardedDate": first_purchase_date,
            "IsPreferredVendor": is_preferred,
            "IsBlacklisted": blacklisted_flag,
            "VendorTenureDays": tenure_days,
        })

    df = pd.DataFrame(rows)
    return df
