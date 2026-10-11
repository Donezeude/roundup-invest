import csv
import hashlib 
from collections import Counter
from datetime import date, timedelta

from .config import (
    LOOKBACK_DAYS,
    PLAID_ENV,
    TX_CSV_PATH,
    TX_SOURCE,
    require,
)

def plaid_client():
    from plaid import Environment
    from plaid.api import plaid_api
    from plaid.api_client import ApiClient
    from plaid.configuration import Configuration

    hosts = {
        "sandbox": Environment.Sandbox, 
        "production": Environment.Production,
    }
    config = Configuration(
        hosts=hosts[PLAID_ENV],
        api_key={
            "clientId": require("PLAID_CLIENT_ID"), 
            "secret": require("PLAID_SECRET"),
        },
    )
    return plaid_api.PlaidApi(ApiClient(config))


def plaid_transactions() -> list[dict]:
    from plaid.model.transactions_get_request import TransactionsGetRequest
    from plaid.model.transactions_get_request_options import (
        TransactionsGetRequestOptions,
    )

    client = plaid_client()
    access_token = require("PLAID_ACCESS_TOKEN")
    start = date.today() - timedelta(days=LOOKBACK_DAYS)
    end = date.today()

    results: list = []
    while True:
        req = TransactionsGetRequest(
            access_token=access_token,
            start_date=start,
            end_date=end,
            options=TransactionsGetRequestOptions(count=500, offset=len(results)),
        )
        resp = client.transactions_get(req)
        results.extend(resp.transactions)
        if len(results) >= resp.total_transactions or not resp.transactions: 
            break

    # Skip pending: they can change amount or vanish when they post.
    return [
        {"transaction_id": t.transaction_id, "amount": float(t.amount), "name": t.name}
        for t in results
        if not t.pending
    ]


def csv_transactions() -> list[dict]:
    """Expects columns: date,description,amount (positive = spending)."""
    rows = []
    occurrences: Counter = Counter()
    with open(TX_CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            key = f"{row['date']}|{row['description']}|{row['amount']}"
            occurrences[key] += 1 # same-day identical purchases stay distinct
            tx_id = hashlib.sha256(f"{key}|{occurrences[key]}".encode()).hexdigest()
            rows.append(
                {
                    "transaction_id": tx_id,
                    "amount": float(row["amount"]),
                    "name": row["description"],
                }
            )
    return rows


def get_transactions() -> list[dict]:
    if TX_SOURCE == "plaid":
        return plaid_transactions()
    if TX_SOURCE == "csv":
        return csv_transactions()
    raise RuntimeError(f"Unknown TX_SOURCE: {TX_SOURCE}")