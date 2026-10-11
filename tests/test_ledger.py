from decimal import Decimal

from roundup.ledger import apply_transactions, compute_roundup


def test_roundup_basic():
    assert compute_roundup(4.32) == Decimal("0.68")


def test_whole_dollar_rounds_by_zero():
    assert compute_roundup(5.00) == Decimal("0.00")


def test_skips_refunds():
    ledger = {"balance": "0.00", "processed_tx_ids": []}
    txs = [{"transaction_id": "a", "amount": -3.50, "name": "refund"}]
    assert Decimal(apply_transactions(ledger, txs)["balance"]) == Decimal("0.00")


def test_idempotent():
    ledger = {"balance": "0.00", "processed_tx_ids": []}
    txs = [{"transaction_id": "a", "amount": 4.32, "name": "coffee"}]
    once = apply_transactions(ledger, txs)
    twice = apply_transactions(once, txs)
    assert twice["balance"] == "0.68"