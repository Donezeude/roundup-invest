from decimal import Decimal

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

from .config import ALPACA_PAPER, INVEST_TICKER, require


def _client() -> TradingClient:
    return TradingClient(
        require("ALPACA_API_KEY"),
        require("ALPACA_SECRET_KEY"), 
        paper=ALPACA_PAPER,
    )


def buying_power() -> Decimal:
    return Decimal(str(_client().get_account().buying_power))


def invest(amount: Decimal):
    order = MarketOrderRequest(
        symbol=INVEST_TICKER, 
        notional=float(amount),     # dollar-based fractional order
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
    )
    return _client().submit_order(order)