import os
from decimal import Decimal

from dotenv import load_dotenv

load_dotenv()


def require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value

TX_SOURCE = os.environ.get("TX_SOURCE", "csv")
TX_CSV_PATH = os.environ.get("TX_CSV_PATH", "transactions.csv")
LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", "7"))

PLAID_ENV = os.environ.get("PLAID_ENV", "sandbox")

ALPACA_PAPER = os.environ.get("ALPACA_PAPER", "true").lower() == "true"

ROUNDUP_THRESHOLD = Decimal(os.environ.get("ROUNDUP_THRESHOLD", "5.00"))
MAX_INVEST_PER_RUN = Decimal(os.environ.get("MAX_INVEST_PER_RUN", "25.00"))
INVEST_TICKER = os.environ.get("INVEST_TICKER", "VTI")

LEDGER_PATH = os.environ.get("LEDGER_PATH", "ledger.json")