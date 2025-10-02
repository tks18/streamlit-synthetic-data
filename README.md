[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/) [![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)
---

# 🌌 Shan's Dataverse


> **Synthetic Finance & Operational Data Factory**
> Generate robust, configurable, and industry-ready synthetic datasets for finance, analytics, and operations — with drag-and-drop column design, formula engines, and reusable profiles.

---
App Link - [Shan's Dataverse](https://shan-dataverse.streamlit.app/)

## ✨ What is Shan’s Dataverse?

Shan’s Dataverse is a **Streamlit-powered synthetic data generator** built for **finance and operations use cases**.

Think of it as a **sandboxed ERP system** — spin up fake but **realistic-looking datasets** (revenue, debtors, PPE, O2C, inventory, vendor master, etc.) in seconds.
Perfect for:

* 🔍 **Creating New POCs** (no real client data needed)
* 🧪 **Testing analytics dashboards**
* 📊 **Experimenting with models** (without regulatory risk)
* ⚙️ **Rapid prototyping for finance & operations**

---

## 🚀 Features

### 🎛️ Data Factory

* **Multiple datasets**: Revenue, Debtors, PPE Register, Purchases, Inventory, Customer/Vendor Masters, and Operational logs.
* Industry-specific **scenarios** (finance, IT services, manufacturing — extensible).
* Define **date ranges, products, and business logic**.

### 🪄 Drag & Drop Column Builder

* True drag-and-drop UI for custom dataset design (`streamlit-sortables`).
* Define custom column **types**:

  * `choice` → pick from a set of categories
  * `range` → bounded random values
  * `formula` → vectorized Python expressions (safe AST sandbox)

### 🔢 Vectorized Formula Engine

* Supports `np`, `math`, `random`, `pd` for efficient expressions.
* Auto-fallback to row-wise evaluation if vectorization fails.
* Example:

  ```python
  Revenue * np.random.uniform(0.9, 1.1)
  ```

### 🗂️ Profiles & Templates

* Save column configs & scenarios as **profiles**.
* Reload from disk for consistent test data across projects.
* Future-proof template store (`profiles/` + `templates/` folders).

### 🔒 Safety by Design

* **AST-based formula validation** → prevents arbitrary code execution.
* Strict module whitelist (`np`, `math`, `random`, `pd`).

---

## ⚡ Installation

```bash
git clone https://github.com/tks18/streamlit-synthetic-data
cd streamlit-synthetic-data
uv sync
```

### Requirements

* `Python 3.9+`
* `Streamlit`
* `Faker`
* `Pandas / NumPy`
* `streamlit-sortables`

---

## ▶️ Usage

```bash
streamlit run app.py
```

Then head to Streamlit Link which comes in the terminal 🚀

---

## 📂 Project Structure

```
Shans-Dataverse/
│── main.py               # Main Streamlit app
│── profiles/            # Saved user profiles (JSON)
│── templates/           # Predefined scenario templates
│── pyproject.toml     # Python dependencies
└── README.md            # This file
```

---

## 🛠️ Example: Adding a Custom Column

1. Select your dataset (`Revenue_Invoices`, `Debtors_Aggregated`, etc.)
2. Add a new column:

   * Name: `Discount_Rate`
   * Type: `range`
   * Min: `0.05`, Max: `0.15`
3. Drag & drop columns into desired order.
4. Generate dataset → preview & download.

---

## 📈 Roadmap

* [ ] Scenario templates for common industries
* [ ] Export to SQL / Parquet
* [ ] Integration with Power BI & Tableau for instant dashboards
* [ ] Time-series realism (seasonality, trends)
* [ ] Multi-user collaborative configs

---

## 🤝 Contributing

PRs and feature requests are welcome! 🚀

---

## 📜 License

GPL-3.0 License — free to use, hack, and extend.

---

Shan’s Dataverse = **insightful, industry-ready synthetic data at your fingertips** ✨

---

Sudharshan TK © 2025 — Built for simplicity & privacy. ❤️

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/tks18/streamlit-synthetic-data)

---