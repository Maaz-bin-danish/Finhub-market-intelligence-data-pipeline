import os
from pathlib import Path

from dotenv import load_dotenv


# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env from main project folder
load_dotenv(PROJECT_ROOT / ".env")


# Snowflake configuration
SNOWFLAKE_CONFIG = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    "database": os.getenv("SNOWFLAKE_DATABASE", "FINHUB_DB"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA", "GOLD"),
    "role": os.getenv("SNOWFLAKE_ROLE"),
}


# Dashboard settings
APP_TITLE = "FINHUB — Market Intelligence"
PAGE_ICON = "📊"

DEFAULT_DATABASE = "FINHUB_DB"
DEFAULT_SCHEMA = "GOLD"