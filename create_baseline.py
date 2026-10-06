import json
from pathlib import Path

from extractor.s3_manager import save_json


LOCAL_FILE = Path(
    r"C:\Users\Maaz\Downloads\stock_symbol_20260919.json"
)

with LOCAL_FILE.open("r", encoding="utf-8") as f:
    snapshot = json.load(f)

symbols = sorted({
    item["symbol"]
    for item in snapshot["data"]
    if item.get("symbol")
})

print(f"Symbols found: {len(symbols)}")

registry = {
    "exchange": "US",
    "updated_at": "2026-09-19",
    "symbol_count": len(symbols),
    "symbols": symbols
}

save_json(
    registry,
    "checkpoints/stock_symbol/US.json"
)

print(
    f"Baseline registry created: {len(symbols)} symbols"
)