"""
QuantEdge AI Trading System - FastAPI High-Performance Backend
Exposes endpoints for Scanner, Charting, Level 2 / Tape, Signals,
Risk Cockpit, Order Execution, Journal, Analytics, and Backtest Replay.
"""

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from typing import Optional, List, Dict, Any
import os

from quantedge.config import DEFAULT_CONFIG, MarketRegimeType, RiskTier
from quantedge.data.feed import FEED_INSTANCE
from quantedge.data.latency_monitor import LatencyMonitor
from quantedge.data.models import OrderSide, OrderType, StrategyType, MistakeTag
from quantedge.scanner.five_pillar_scanner import SCANNER_INSTANCE
from quantedge.signals.engine import SIGNAL_ENGINE
from quantedge.signals.kronos_bridge import KRONOS_INSTANCE
from quantedge.risk.risk_engine import RISK_ENGINE
from quantedge.execution.order_manager import ORDER_MANAGER
from quantedge.journal.trade_journal import JOURNAL_INSTANCE
from quantedge.backtest.backtester import BACKTESTER_INSTANCE
from quantedge.compliance.regulatory import COMPLIANCE_MANAGER

app = FastAPI(
    title="QuantEdge AI Trading System",
    description="Strategic AI-assisted US Short-Term Momentum Trading Cockpit",
    version="2.6.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import threading
LATENCY_MONITOR = LatencyMonitor()

@app.on_event("startup")
def startup_event():
    # Warm up real-time market data in background thread without delaying server availability
    t = threading.Thread(target=FEED_INSTANCE.warmup_alpaca_live_data, daemon=True)
    t.start()

# Serve static web dashboard
web_static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "static")
if os.path.exists(web_static_dir):
    app.mount("/static", StaticFiles(directory=web_static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    index_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web", "templates", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>QuantEdge AI Trading System API is running. Dashboard template building...</h1>"


# --- Scanner Endpoints ---
@app.get("/api/scanner")
def get_scanner_results(regime: str = "Bullish"):
    market_regime = MarketRegimeType(regime) if regime in [r.value for r in MarketRegimeType] else MarketRegimeType.BULLISH
    candidates, summary = SCANNER_INSTANCE.scan_universe(market_regime=market_regime)
    return {
        "candidates": [c.model_dump() for c in candidates],
        "summary": summary
    }


# --- Charting & Market Data Endpoints ---
@app.get("/api/quote/{symbol}")
def get_quote(symbol: str):
    symbol = symbol.upper()
    quote = FEED_INSTANCE.get_quote(symbol)
    return quote


@app.get("/api/bars/{symbol}")
def get_bars(symbol: str, timeframe: str = "1m"):
    symbol = symbol.upper()
    bars = FEED_INSTANCE.get_bars(symbol, timeframe)
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "bars": [b.model_dump() for b in bars]
    }


@app.get("/api/orderflow/{symbol}")
def get_orderflow(symbol: str):
    symbol = symbol.upper()
    l2 = FEED_INSTANCE.get_level2_snapshot(symbol)
    return l2.model_dump()


@app.get("/api/tape/{symbol}")
def get_tape(symbol: str, limit: int = 35):
    symbol = symbol.upper()
    tape = FEED_INSTANCE.get_tape(symbol, limit)
    return {
        "symbol": symbol,
        "tape": [t.model_dump() for t in tape]
    }


# --- Signals & AI Intelligence ---
@app.get("/api/signals")
def get_active_signals():
    signals = SIGNAL_ENGINE.scan_all_signals()
    return {
        "signals": [s.model_dump() for s in signals]
    }


@app.get("/api/signals/{symbol}")
def get_symbol_signal(symbol: str):
    symbol = symbol.upper()
    meta = FEED_INSTANCE.universe_metadata.get(symbol, {})
    strat_name = StrategyType(meta.get("strategy", StrategyType.GAP_AND_GO_PULLBACK.value))
    sig = SIGNAL_ENGINE.generate_signal(symbol, strat_name)
    if not sig:
        raise HTTPException(status_code=404, detail="Signal not available for symbol")
    return sig.model_dump()


@app.get("/api/kronos/predict/{symbol}")
def get_kronos_prediction(symbol: str, horizon: int = 5):
    symbol = symbol.upper()
    bars = FEED_INSTANCE.get_bars(symbol)
    ohlcv = [b.model_dump() for b in bars]
    prediction = KRONOS_INSTANCE.predict_next_bars(ohlcv, horizon_bars=horizon, symbol=symbol)
    return {
        "symbol": symbol,
        "prediction": prediction
    }


# --- Discipline & Risk Cockpit Endpoints ---
@app.get("/api/risk/cockpit")
def get_risk_cockpit():
    state = RISK_ENGINE.get_cockpit_state()
    return state.model_dump()


@app.post("/api/risk/set_tier")
def set_risk_tier(payload: Dict[str, Any] = Body(...)):
    tier_str = payload.get("tier")
    approved = payload.get("approved_by_operator", False)
    
    tier_map = {
        "Tier 1": RiskTier.TIER_1_MICRO,
        "Tier 2": RiskTier.TIER_2_INTERMEDIATE,
        "Tier 3": RiskTier.TIER_3_ADVANCED
    }
    tier = tier_map.get(tier_str, RiskTier.TIER_1_MICRO)
    success, msg = RISK_ENGINE.set_risk_tier(tier, approved_by_operator=approved)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "cockpit": RISK_ENGINE.get_cockpit_state().model_dump()}


@app.post("/api/risk/kill_switch")
def trigger_kill_switch():
    result = RISK_ENGINE.emergency_kill_switch()
    COMPLIANCE_MANAGER.log_audit_event("EMERGENCY_KILL_SWITCH", result)
    return result


@app.post("/api/risk/reset_lockout")
def reset_lockout(payload: Dict[str, Any] = Body(...)):
    reason = payload.get("reason", "Operator administrative reset with formal justification")
    RISK_ENGINE.is_locked_out = False
    RISK_ENGINE.lockout_reason = None
    COMPLIANCE_MANAGER.log_audit_event("LOCKOUT_RESET_OVERRIDE", {"reason": reason})
    return {"success": True, "message": "Lockout manually cleared", "cockpit": RISK_ENGINE.get_cockpit_state().model_dump()}


# --- Order Execution Endpoints ---
@app.post("/api/order/stage")
def stage_order(order_data: Dict[str, Any] = Body(...)):
    symbol = order_data.get("symbol", "").upper()
    side = OrderSide(order_data.get("side", OrderSide.BUY.value))
    order_type = OrderType(order_data.get("order_type", OrderType.MARKETABLE_LIMIT.value))
    shares = int(order_data.get("shares", 100))
    entry_price = float(order_data.get("entry_price", 10.0))
    stop_loss = float(order_data.get("stop_loss", 9.80))
    target_price = float(order_data.get("target_price", 10.50))
    strategy = StrategyType(order_data.get("strategy", StrategyType.GAP_AND_GO_PULLBACK.value))
    entry_reason = order_data.get("entry_reason", "Confirmed crossing candle pullback setup holding VWAP")
    override_reason = order_data.get("override_reason", None)

    success, msg, order = ORDER_MANAGER.stage_order(
        symbol=symbol,
        side=side,
        order_type=order_type,
        shares=shares,
        entry_price=entry_price,
        stop_loss=stop_loss,
        target_price=target_price,
        strategy=strategy,
        entry_reason=entry_reason,
        override_reason=override_reason
    )

    if not success:
        return {"success": False, "message": msg}

    return {
        "success": True,
        "message": msg,
        "order": order.model_dump()
    }


@app.post("/api/order/close")
def close_trade(payload: Dict[str, Any] = Body(...)):
    order_id = payload.get("order_id")
    exit_price = float(payload.get("exit_price", 10.0))
    raw_tags = payload.get("mistake_tags", [])
    
    mistake_tags = [MistakeTag(t) for t in raw_tags if t in [m.value for m in MistakeTag]]
    success, msg, order = ORDER_MANAGER.close_trade(order_id, exit_price, mistake_tags)
    
    if not success:
        raise HTTPException(status_code=400, detail=msg)
        
    return {
        "success": True,
        "message": msg,
        "closed_order": order.model_dump(),
        "cockpit": RISK_ENGINE.get_cockpit_state().model_dump()
    }


@app.get("/api/options/contract/{symbol}")
def get_options_contract(symbol: str):
    symbol = symbol.upper()
    contract = ORDER_MANAGER.get_options_contract_quote(symbol)
    return contract


# --- Journal & Analytics ---
@app.get("/api/journal")
def get_journal():
    return {
        "entries": JOURNAL_INSTANCE.get_journal_entries()
    }


@app.get("/api/analytics")
def get_analytics():
    return JOURNAL_INSTANCE.compute_analytics()


# --- Backtesting Lab ---
@app.post("/api/backtest/run")
def run_backtest(params: Dict[str, Any] = Body(...)):
    strategy = params.get("strategy", "Gap-and-Go Pullback")
    risk_per_trade = float(params.get("risk_per_trade", 40.0))
    slippage = float(params.get("slippage_cents", 0.02))
    max_pullback = float(params.get("max_pullback_depth", 0.50))
    min_rr = float(params.get("min_reward_risk", 2.0))
    days = int(params.get("days", 30))

    result = BACKTESTER_INSTANCE.run_strategy_backtest(
        strategy_name=strategy,
        risk_per_trade=risk_per_trade,
        slippage_cents=slippage,
        max_pullback_depth=max_pullback,
        min_reward_risk=min_rr,
        days=days
    )
    return result


# --- Compliance & Latency ---
@app.get("/api/compliance")
def get_compliance_status():
    cockpit = RISK_ENGINE.get_cockpit_state()
    return COMPLIANCE_MANAGER.get_regulatory_status(cockpit.equity, open_exposure=0.0)


@app.get("/api/latency")
def get_latency_status():
    status = LATENCY_MONITOR.get_status()
    alpaca_active = getattr(FEED_INSTANCE, "use_alpaca_live", False)
    status["feed_source"] = "🟢 Alpaca Live" if alpaca_active else "🟢 Live Simulation"
    return status
