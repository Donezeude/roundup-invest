import json
import os 
import tempfile 
from decimal import Decimal, ROUND_CEILING

from .config import LEDGER_PATH

MAX_TRACKED_IDS = 5000


def load() -> dict:
    if not os.path.exists(LEDGER_PATH):
        return {"balance": "0.00", "processed_tx_ids": []}
    with open(LEDGER_PATH) as f:
        return json.load(f)


def save(ledger: dict) -> None:
    """Atomic write: a crash mid-save can't corrupt the ledger."""
    directory = os.path.dirname(os.path.abspath(LEDGER_PATH))
    fd, tmp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(ledger, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, LEDGER_PATH)


def compute_roundup(amount: float) -> Decimal:
    """Spare change to the next whole dollar. Exact dollars round up by 0."""
    amt = Decimal(str(amount)).quantize(Decimal("0.01"))
    return amt.to_integral_value(rounding=ROUND_CEILING) - amt


def apply_transactions(ledger: dict, transactions: list[dict]) -> dict:
    balance = Decimal(ledger["balance"])
    seen = set(ledger["processed_tx_ids"])
    new_ids = []

    for tx in transactions:
        tx_id = tx["transaction_id"]
        if tx_id in seen:
            continue
        seen.add(tx_id)
        new_ids.append(tx_id)
        if tx["amount"] <= 0:   # refunds / payments / credits
            continue
        balance += compute_roundup(tx["amount"])

    ledger["balance"] = str(balance)
    ledger["processed_tx_ids"] = (ledger["processed_tx_ids"] + new_ids)[
        -MAX_TRACKED_IDS:
    ]
    return ledger