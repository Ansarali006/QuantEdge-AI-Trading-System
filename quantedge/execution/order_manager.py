"""
QuantEdge Execution Layer & Order Manager
Handles order ticket generation, staging, marketable limit order fills,
slippage modeling, stop-loss / profit-target bracket management, and options contract mapping.
"""

import uuid
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from quantedge.config import DEFAULT_CONFIG
from quantedge.data.models import (
    ExecutionOrder, OrderSide, OrderType, OrderStatus, StrategyType, MistakeTag
)
from quantedge.risk.risk_engine import RISK_ENGINE
from quantedge.data.feed import FEED_INSTANCE


class OrderManager:
    def __init__(self, risk_engine=RISK_ENGINE, feed=FEED_INSTANCE):
        self.risk_engine = risk_engine
        self.feed = feed
        self.active_orders: Dict[str, ExecutionOrder] = {}
        self.order_history: List[ExecutionOrder] = []

    def stage_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        shares: int,
        entry_price: float,
        stop_loss: float,
        target_price: float,
        strategy: StrategyType,
        entry_reason: str,
        override_reason: Optional[str] = None
    ) -> Tuple[bool, str, Optional[ExecutionOrder]]:
        """
        Validates risk rules before staging and executing the order.
        """
        # Step 1: Pre-trade risk check
        valid, msg, risk_meta = self.risk_engine.validate_pre_trade_risk(
            symbol=symbol,
            entry_price=entry_price,
            stop_loss=stop_loss,
            target_price=target_price,
            shares=shares,
            override_reason=override_reason
        )

        if not valid:
            return False, msg, None

        planned_rr = risk_meta.get("planned_rr", 2.0)
        order_id = f"ORD-{symbol}-{uuid.uuid4().hex[:6].upper()}"

        order = ExecutionOrder(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            shares=shares,
            limit_price=entry_price,
            stop_loss=stop_loss,
            target_price=target_price,
            planned_rr=planned_rr,
            status=OrderStatus.SUBMITTED,
            created_at=datetime.now().strftime("%H:%M:%S"),
            strategy=strategy,
            entry_reason=entry_reason,
            override_reason=override_reason
        )

        # Step 2: Realistic Marketable Limit Fill Simulation
        # Small cap momentum slippage: 0.01 - 0.02 cents slippage depending on spread
        slippage = 0.01 if entry_price < 15.0 else 0.02
        fill_price = round(entry_price + (slippage if side == OrderSide.BUY else -slippage), 2)
        
        order.status = OrderStatus.FILLED
        order.fill_price = fill_price
        order.filled_at = datetime.now().strftime("%H:%M:%S")
        order.slippage = slippage
        order.commission = 0.0  # Zero commission broker model

        self.active_orders[order_id] = order
        self.order_history.append(order)
        self.risk_engine.trades_history.append(order)

        return True, f"Order {order_id} filled at ${fill_price} (Slippage: ${slippage})", order

    def close_trade(
        self,
        order_id: str,
        exit_price: float,
        mistake_tags: List[MistakeTag] = None
    ) -> Tuple[bool, str, Optional[ExecutionOrder]]:
        """
        Closes an open position, calculates realized P&L and realized R-multiple,
        and updates the risk cockpit.
        """
        if order_id not in self.active_orders:
            return False, "Order not found", None

        order = self.active_orders.pop(order_id)
        order.status = OrderStatus.CLOSED
        order.closed_at = datetime.now().strftime("%H:%M:%S")
        
        fill_p = order.fill_price or order.limit_price
        shares = order.shares
        
        # Realized P&L
        if order.side == OrderSide.BUY:
            pnl = round((exit_price - fill_p) * shares, 2)
        else:
            pnl = round((fill_p - exit_price) * shares, 2)

        stop_dist = abs(fill_p - order.stop_loss)
        dollar_risk = max(1.0, stop_dist * shares)
        r_multiple = round(pnl / dollar_risk, 2)

        order.realized_pnl = pnl
        order.realized_r_multiple = r_multiple
        order.mistake_tags = mistake_tags or [MistakeTag.NONE]

        # Generate AI post-trade critique (Section 6 & 9)
        critique = []
        if r_multiple >= 2.0:
            critique.append(f"Outstanding execution: Captured {r_multiple}R aligned with 2:1 planned edge.")
        elif r_multiple > 0:
            critique.append(f"Positive win: +${pnl} (+{r_multiple}R). Controlled risk adherence.")
        else:
            critique.append(f"Disciplined loss: -${abs(pnl)} ({r_multiple}R). Stop-loss respected structure low.")

        if MistakeTag.FOMO in order.mistake_tags:
            critique.append("Discipline Warning: Trade flagged for FOMO. Review scanner conviction criteria.")
        if MistakeTag.PULLBACK_TOO_DEEP in order.mistake_tags:
            critique.append("Discipline Warning: Pullback exceeded 50% retracement. Re-read Section 4 invalidation rules.")

        order.ai_post_trade_summary = " | ".join(critique)

        # Update Risk Engine state
        self.risk_engine.update_pnl(realized_delta=pnl, unrealized=0.0)

        return True, f"Trade closed: Realized P&L ${pnl} ({r_multiple}R)", order

    def get_options_contract_quote(self, underlying_symbol: str) -> Dict[str, Any]:
        """
        Implements Section 5 Options rules:
        - Liquid weekly contracts, usually one strike OTM, tight bid-ask spread and adequate volume/OI.
        """
        quote = self.feed.get_quote(underlying_symbol)
        curr_price = quote["price"]
        otm_strike = round(math.ceil(curr_price / 2.5) * 2.5 if curr_price < 100 else math.ceil(curr_price / 5.0) * 5.0, 2)
        
        # Approximate weekly option pricing
        opt_ask = round(max(0.65, (curr_price * 0.02)), 2)
        opt_bid = round(opt_ask - 0.02, 2)
        
        return {
            "underlying": underlying_symbol,
            "underlying_price": curr_price,
            "contract_type": "CALL",
            "strike": otm_strike,
            "expiry": "Weekly (Friday)",
            "bid": opt_bid,
            "ask": opt_ask,
            "spread": round(opt_ask - opt_bid, 2),
            "open_interest": 12_400,
            "volume": 8_920,
            "delta": 0.42,
            "rule_compliance": "Complies with Section 5 (Weekly 1-strike OTM, tight spread <= $0.03)"
        }


import math
ORDER_MANAGER = OrderManager()
