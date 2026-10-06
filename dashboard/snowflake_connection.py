import snowflake.connector
import streamlit as st

from config import SNOWFLAKE_CONFIG


@st.cache_resource
def get_connection():
    config = SNOWFLAKE_CONFIG

    required = ["account", "user", "password"]
    missing = [key for key in required if not config.get(key)]

    if missing:
        raise RuntimeError(
            f"Missing Snowflake configuration: {', '.join(missing)}"
        )

    return snowflake.connector.connect(
        account=config["account"],
        user=config["user"],
        password=config["password"],
        warehouse=config["warehouse"],
        database=config["database"],
        schema=config["schema"],
        role=config["role"],
    )


def run_query(query: str, params=None):
    connection = get_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        if params:
            result = cursor.execute(query, params)
        else:
            result = cursor.execute(query)

        return result.fetch_pandas_all()

    except Exception:
        raise

    finally:
        if cursor is not None:
            cursor.close()