# FINHUB — Market Intelligence Data Engineering Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-Data%20Engineering-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/AWS-S3-orange?style=for-the-badge&logo=amazonaws" />
  <img src="https://img.shields.io/badge/Apache-Airflow-red?style=for-the-badge&logo=apacheairflow" />
  <img src="https://img.shields.io/badge/Snowflake-Data%20Warehouse-29B5E8?style=for-the-badge&logo=snowflake" />
  <img src="https://img.shields.io/badge/Power-BI-F2C811?style=for-the-badge&logo=powerbi" />
</p>

<p align="center">
  <strong>End-to-End Financial Market Data Engineering & Intelligence Pipeline</strong>
</p>

<p align="center">
  Finnhub API → Python → AWS S3 → Apache Airflow → Snowflake Bronze → Silver → Gold → Power BI
</p>

---

## 🎥 Dashboard Demo

<p align="center">
  <a href="./video/FINHUB-Dashboard-Demo.mp4">
    <strong>▶ Watch the FINHUB Dashboard Demo — 1:16</strong>
  </a>
</p>

The repository includes a 1 minute 16 second walkthrough of the final Power BI market intelligence dashboard.

> **Demo:** [FINHUB Dashboard Demo](./video/FINHUB-Dashboard-Demo.mp4)

---

# 📌 What is FINHUB-Market-intelligence?

**FINHUB-Market-intelligence** is an end-to-end data engineering project that collects financial market data from the **Finnhub API**, stores the raw data in **Amazon S3**, orchestrates the pipeline using **Apache Airflow**, loads the data into **Snowflake**, transforms it through **Bronze, Silver and Gold layers**, and finally exposes analytics through a **Streamlit+plotly dashboard**.

The main purpose of the project is to demonstrate how raw external API data can be converted into structured, analytics-ready business intelligence using a modern cloud data engineering architecture.

---

# 🧠 Project in Simple Terms

The complete system can be understood in 7 stages:

```text
1. Finnhub
   ↓
2. Python Extraction
   ↓
3. AWS S3 Raw Storage
   ↓
4. Apache Airflow Orchestration
   ↓
5. Snowflake Bronze
   ↓
6. Snowflake Silver
   ↓
7. Snowflake Gold
   ↓
8. Power BI Dashboard
```

### In simple words:

**Finnhub** provides the financial data.

**Python** requests that data from the API.

**AWS S3** stores the original JSON responses.

**Airflow** controls when and in what order the pipeline runs.

**Snowflake Bronze** stores the ingested raw data.

**Snowflake Silver** cleans and structures the data.

**Snowflake Gold** prepares business/analytics-ready datasets.

**Power BI** turns the Gold data into an interactive market intelligence dashboard.

---

# 🏗️ Complete Architecture

```text
                         ┌─────────────────────┐
                         │     FINNHUB API     │
                         │  Financial Market   │
                         │        Data         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Python Extractor  │
                         │                     │
                         │ API Client          │
                         │ Retry Handling      │
                         │ Request Hashing     │
                         │ JSON Generation     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      AWS S3         │
                         │                     │
                         │    RAW DATA LAKE    │
                         │                     │
                         │ raw/YYYY/MM/DD/...  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                     ┌─────────────────────────────┐
                     │       APACHE AIRFLOW        │
                     │                             │
                     │     Pipeline Orchestration  │
                     │     Scheduling              │
                     │     Task Dependencies       │
                     └──────────────┬──────────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │          SNOWFLAKE            │
                    │                              │
                    │  ┌────────────────────────┐  │
                    │  │       BRONZE            │  │
                    │  │   Raw / Ingested Data   │  │
                    │  └───────────┬────────────┘  │
                    │              │               │
                    │              ▼               │
                    │  ┌────────────────────────┐  │
                    │  │        SILVER           │  │
                    │  │ Cleaned / Structured    │  │
                    │  │ Analytical Tables       │  │
                    │  └───────────┬────────────┘  │
                    │              │               │
                    │              ▼               │
                    │  ┌────────────────────────┐  │
                    │  │         GOLD            │  │
                    │  │ Analytics-Ready Data   │  │
                    │  └───────────┬────────────┘  │
                    └──────────────┼───────────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │      POWER BI       │
                         │                     │
                         │ Market Intelligence │
                         │     Dashboard       │
                         └─────────────────────┘
```

---

# 📥 1. Data Source — Finnhub API

The pipeline starts with the **Finnhub financial market API**.

Instead of manually entering financial information, FINHUB programmatically requests market data from Finnhub.

The extraction layer covers multiple endpoint groups for:

| Category          | Data                               |
| ----------------- | ---------------------------------- |
| Stock Symbols     | US-listed stock symbol universe    |
| Stock Quotes      | Current/market quote information   |
| Company Profiles  | Company information                |
| Company Peers     | Comparable companies               |
| Company News      | Company-specific news              |
| Earnings          | Historical earnings information    |
| Earnings Calendar | Upcoming/available earnings events |
| IPO Calendar      | IPO information                    |
| Dividends         | Dividend information               |
| Stock Splits      | Stock split information            |
| Market Status     | Exchange market status             |
| Market Holidays   | Exchange holidays                  |
| Forex             | Forex symbols/rates                |
| Cryptocurrency    | Crypto symbols/exchanges           |
| General News      | Broad market news                  |

The extraction layer therefore works with **15 endpoint/data groups**, with some Finnhub resources such as Forex and Crypto represented as related endpoint pairs.

---

# 🐍 2. Python Extraction Layer

Python is responsible for communicating with Finnhub and preparing the API responses for cloud storage.

The project contains separate extraction modules instead of putting everything into one large script.

Example structure:

```text
extractor/
│
├── api_client.py
├── common.py
├── s3_manager.py
│
├── stock_symbol.py
├── stock_quote.py
├── stock_profile.py
├── stock_peers.py
├── company_news.py
├── stock_earnings.py
├── earnings_calendar.py
├── ipo_calendar.py
├── dividend.py
├── splits.py
├── market_status.py
├── market_holiday.py
├── forex_symbols.py
├── crypto_symbols.py
├── crypto_exchanges.py
└── general_news.py
```

### API Client

The centralized API client handles:

* HTTP requests
* Response validation
* JSON parsing
* Retry handling
* Request timeouts
* API errors
* Request parameters

This prevents every extractor from implementing its own HTTP logic.

---

# 🔐 Request Hashing & Metadata

Each extracted JSON file contains metadata alongside the actual API response.

Example structure:

```json
{
  "endpoint": "stock_quote",
  "request_parameters": {
    "symbol": "AAPL"
  },
  "request_hash": "SHA256_HASH",
  "extracted_at": "2026-10-06T..."
}
```

This provides traceability for each extraction.

The request hash can be used to identify the request that generated a particular raw object.

---

# ☁️ 3. AWS S3 — Raw Data Lake

After extraction, the JSON response is uploaded to **Amazon S3**.

S3 acts as the raw cloud storage/data lake layer.

The raw data follows a date-partitioned structure:

```text
finhub-stock-data/
│
└── raw/
    └── YYYY/
        └── MM/
            └── DD/
                ├── stock_quote/
                │   └── AAPL/
                │
                ├── stock_profile/
                │   └── AAPL/
                │
                ├── company_news/
                │   └── AAPL/
                │
                └── ...
```

For example:

```text
raw/2026/10/05/stock_quote/AAPL/stock_quote_AAPL_....json
```

### Why S3?

S3 provides:

* Durable cloud storage
* Scalable object storage
* Separation between extraction and warehouse processing
* Historical raw data preservation
* Easy integration with Snowflake
* Date-based organization

---

# ⏱️ 4. Apache Airflow — Orchestration

Apache Airflow is responsible for orchestrating the entire pipeline.

The main DAG is:

```text
finhub_daily_pipeline
```

The pipeline is designed as a **daily scheduled workflow**.

The high-level dependency is:

```text
Finnhub Extraction
        │
        ▼
   Bronze Load
        │
        ▼
 Silver Transformations
        │
        ▼
   Gold Layer
```

Airflow provides:

* Scheduling
* Task dependency management
* Execution monitoring
* Retry handling
* Logs
* Failure visibility
* Pipeline orchestration

Instead of manually running every Python script, Airflow controls the workflow.

---

# ❄️ 5. Snowflake Data Warehouse

Snowflake is the central analytical warehouse for FINHUB.

The project uses a layered architecture:

```text
FINHUB_DB
│
├── BRONZE
│
├── SILVER
│
└── GOLD
```

This separates raw ingestion from transformed analytical data.

---

# 🥉 Bronze Layer

The Bronze layer is the first Snowflake layer after S3 ingestion.

Main object:

```text
FINHUB_DB.BRONZE.FINHUB_RAW
```

The Bronze layer is intentionally close to the source data.

Its purpose is to:

* Preserve incoming data
* Maintain ingestion history
* Keep raw payloads available
* Provide a reliable source for downstream transformations

The S3 stage is used to bring the JSON data into Snowflake.

```text
AWS S3
   │
   ▼
Snowflake External Stage
   │
   ▼
FINHUB_DB.BRONZE.FINHUB_RAW
```

---

# 🥈 Silver Layer

The Silver layer converts the raw Bronze data into structured relational tables.

The project contains analytical tables for areas such as:

```text
STOCK_SYMBOLS
STOCK_QUOTE
STOCK_PROFILE
STOCK_PEERS
STOCK_EARNINGS
COMPANY_NEWS
EARNINGS_CALENDAR
IPO_CALENDAR
MARKET_STATUS
MARKET_HOLIDAY
FOREX_SYMBOLS
CRYPTO_SYMBOLS
CRYPTO_EXCHANGES
GENERAL_NEWS
```

### Silver Layer Responsibilities

The Silver layer is where raw JSON becomes usable structured data.

Typical operations include:

* JSON parsing
* Column extraction
* Data type conversion
* Null handling
* Normalization
* Deduplication
* Data quality handling
* Business-friendly column structures

Conceptually:

```text
Raw JSON
   ↓
Parse
   ↓
Clean
   ↓
Validate
   ↓
Structure
   ↓
Silver Table
```

---

# 🥇 Gold Layer

The Gold layer is the final analytical layer.

Its purpose is to provide datasets that are easier for BI/reporting tools to consume.

```text
Silver Tables
      │
      ▼
Business / Analytical Transformations
      │
      ▼
Gold Layer
      │
      ▼
Power BI
```

The Gold layer avoids forcing Power BI to perform heavy raw-data transformations.

---

# 📊 6. Power BI — Market Intelligence Dashboard

The final layer of FINHUB is the Power BI dashboard.

Power BI consumes analytics-ready data from the warehouse and presents it visually.

The dashboard is designed to provide a high-level market intelligence view of the data collected through the pipeline.

The complete data journey is therefore:

```text
API Data
   ↓
Raw JSON
   ↓
S3
   ↓
Snowflake Bronze
   ↓
Snowflake Silver
   ↓
Snowflake Gold
   ↓
Power BI
   ↓
Market Intelligence
```

---

# 🔄 Complete ETL / ELT Flow

```text
EXTRACT
──────────────
Finnhub API
     ↓
Python Extractors


LOAD
──────────────
AWS S3
     ↓
Snowflake Bronze


TRANSFORM
──────────────
Bronze
  ↓
Silver
  ↓
Gold


VISUALIZE
──────────────
Gold
  ↓
Power BI
  ↓
Dashboard
```

The architecture combines **ETL-style extraction and loading** with a warehouse-oriented **ELT transformation approach**.

---

# 🧰 Technology Stack

| Technology     | Purpose                                   |
| -------------- | ----------------------------------------- |
| Python         | API extraction and pipeline logic         |
| Finnhub API    | Financial market data source              |
| AWS S3         | Raw cloud data lake                       |
| Apache Airflow | Workflow orchestration                    |
| Snowflake      | Cloud data warehouse                      |
| SQL            | Data transformation and analysis          |
| dbt Concepts   | Layered transformation/modeling approach  |
| Power BI       | Business intelligence and visualization   |
| Docker         | Containerized data engineering components |
| Git            | Version control                           |
| GitHub         | Source control and portfolio hosting      |

---

# 📁 Project Structure

```text
finhub-pipeline/
│
├── extractor/
│   ├── api_client.py
│   ├── common.py
│   ├── s3_manager.py
│   └── endpoint extractors
│
├── Airflow/
│
├── dashboard/
│
├── data/
│
├── config.py
├── create_baseline.py
├── delta_manager.py
├── finhub_daily_pipeline.py
├── run_extraction.py
│
├── snowflake_bronze.py
├── snowflake_silver.py
├── snowflake_gold.py
│
├── scan_s3_json.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

# 📈 Data Engineering Features

FINHUB demonstrates several real-world data engineering concepts:

### API Engineering

* Centralized API client
* Parameterized requests
* Error handling
* Retry logic
* Timeout handling
* Response validation

### Data Lake Engineering

* AWS S3 object storage
* Date-based partitioning
* Endpoint-based organization
* Raw JSON preservation

### Pipeline Engineering

* Apache Airflow DAG
* Scheduled execution
* Task dependencies
* Retry/failure handling
* Pipeline logging

### Data Warehouse Engineering

* Snowflake
* External S3 stage
* Bronze/Silver/Gold architecture
* JSON ingestion
* Structured analytical tables

### Data Quality

* JSON validation
* Request hashing
* Null handling
* Deduplication
* Raw-data validation
* S3 object scanning

### Business Intelligence

* Analytics-ready Gold layer
* Power BI integration
* Market intelligence dashboard

---

# 🔒 Security

No credentials should be committed to this repository.

Sensitive information such as:

```text
FINNHUB_API_KEY
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
SNOWFLAKE_PASSWORD
```

is stored outside the Git repository.

The `.env` file is excluded through `.gitignore`.

Example configuration:

```text
FINNHUB_API_KEY=your_api_key
AWS_REGION=your_region
S3_BUCKET=your_bucket
```

**Never commit real credentials to GitHub.**

---

# 🚀 Running the Project

Clone the repository:

```bash
git clone https://github.com/Maaz-bin-danish/Finhub-market-intelligence-data-pipeline.git

cd Finhub-market-intelligence-data-pipeline
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Configure the required environment variables locally.

Then the extraction pipeline can be executed through the project's Python/Airflow workflow.

For production-style execution, Airflow is responsible for scheduling and orchestrating the pipeline.

---

# 📅 Pipeline Scheduling

FINHUB is designed around a **daily pipeline schedule**.

The scheduled workflow performs the following sequence:

```text
Daily Trigger
     ↓
Finnhub Extraction
     ↓
S3 Raw Upload
     ↓
Snowflake Bronze Load
     ↓
Silver Transformation
     ↓
Gold Transformation
     ↓
Power BI Consumption
```

This turns the project from a collection of scripts into an automated data pipeline.

---

# 🧩 Why Bronze → Silver → Gold?

The three-layer architecture separates responsibilities.

### Bronze = What did the source give us?

Raw and minimally processed data.

### Silver = What does the data actually mean?

Cleaned, structured and normalized data.

### Gold = What does the business need?

Analytics-ready data optimized for reporting and decision-making.

This separation makes the system easier to:

* Debug
* Maintain
* Reprocess
* Scale
* Monitor
* Consume from BI tools

---

# 🎯 Project Objective

The main objective of FINHUB is to demonstrate the complete lifecycle of financial market data:

> **From external API → cloud storage → orchestration → data warehouse → transformation → business intelligence.**

The project focuses on building the engineering infrastructure required to make raw financial data useful for analytical decision-making.

---

# 👨‍💻 Author

**Maaz bin Danish**

BS Business Computing
Data Engineering | Cloud Data | Analytics

---

<p align="center">
  <strong>FINHUB — From Market Data to Market Intelligence.</strong>
</p>
