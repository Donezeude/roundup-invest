import argparse 
from decimal import Decimal, ROUND_DOWN

from . import ledger as ledger_store
from .broker import buying_power, invest
from .config import MAX_INVEST_PER_RUN, ROUNDUP_THRESHOLD
from .sources import get_transactions

def run(dry_run: bool = False) -> None:
    ledger = ledger_store.load()
    ledger = ledger_store.apply_transactions(ledger, get_transactions())
    ledger_store.save(ledger) # persist counted round-ups before anything else

    balance = Decimal(ledger["balance"])
    print(f"Accumulated spare change: ${balance}")

    if balance < ROUNDUP_THRESHOLD: 
        print(f"Below threshold(${ROUNDUP_THRESHOLD}); nothing to invest.")
        return

    amount = min(balance, MAX_INVEST_PER_RUN).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )

    if dry_run:
        print(f"[dry-run] Would invest ${amount}")
        return

    available = buying_power()
    if available < amount:
        print(f"Alpaca buying power ${available} < ${amount}. Fund the account.")
        return

    # Deduct BEFORE ordering: a crash can only under-invest, never double-invest.
    ledger["balance"] = str(balance - amount)
    ledger_store.save(ledger)
    try:
        order = invest(amount)
    except Exception:
        ledger["balance"] = str(balance)
        ledger_store.save(ledger)
        raise

    print(f"Invested ${amount} -> order {order.id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    run(dry_run=parser.parse_args().dry_run)