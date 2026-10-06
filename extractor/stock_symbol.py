from datetime import date

from .common import save_json
from .s3_manager import upload_file
from config import STOCK_SYMBOLS


ENDPOINT_NAME = "stock_symbol"


def extract_stock_symbols():

    # ==========================================
    # 1. USE FIXED 200 SYMBOLS FROM CONFIG
    # ==========================================

    data = [
        {
            "symbol": symbol
        }
        for symbol in STOCK_SYMBOLS
    ]

    if not data:
        return [], []

    # ==========================================
    # 2. SAVE SYMBOL LIST TO S3
    # ==========================================

    params = {
        "source": "config.py",
        "symbol_count": len(data)
    }

    local_file = save_json(
        ENDPOINT_NAME,
        data,
        params
    )

    today = date.today()

    s3_key = (
        f"raw/{today:%Y}/{today:%m}/{today:%d}/"
        f"{ENDPOINT_NAME}/"
        f"{ENDPOINT_NAME}_{today:%Y%m%d}.json"
    )

    upload_file(
        local_file,
        s3_key
    )

    # Delete local temporary file
    local_file.unlink(
        missing_ok=True
    )

    # ==========================================
    # 3. RETURN SYMBOLS
    # ==========================================

    return data, STOCK_SYMBOLS


if __name__ == "__main__":
    data, symbols = extract_stock_symbols()
    print(f"Total symbols: {len(symbols)}")