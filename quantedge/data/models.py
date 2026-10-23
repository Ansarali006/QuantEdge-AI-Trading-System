"""
QuantEdge Data Models
Defines core domain models for bars, order flow, candidate screening, signals, orders, and risk state.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class StrategyType(str, Enum):
    GAP_AND_GO_PULLBACK = "Gap-and-Go Pullback"
    OPENING_RANGE_BREAKOUT = "Opening Range Breakout"
    VWAP_RECLAIM = "VWAP Reclaim"
    RELATIVE_STRENGTH_OPTIONS = "Relative-Strength Options"
    NEWS_CATALYST_MOMENTUM = "News Catalyst Momentum"
    FAILED_BREAKOUT_SHORT = "Failed Breakout Short"


class SignalType(str, Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    AVOID = "AVOID"


class SetupGrade(str, Enum):
    GRADE_A = "A"
    GRADE_B = "B"
    GRADE_C = "C"


class MistakeTag(str, Enum):
    FOMO = "FOMO"
    CHASED_ENTRY = "Chased Entry"
    MOVED_STOP = "Moved Stop"
    REVENGE_TRADE = "Revenge Trade"
    OVERTRADING = "Overtrading"
    HELD_PAST_10AM = "Held Past 10:00 AM"
    POOR_SPREAD = "Poor Bid-Ask Spread"
    PULLBACK_TOO_DEEP = "Pullback > 50%"
    RED_VOLUME_SURGE = "Ignored High Red Volume"
    NONE = "Clean Rule Adherence"


class Bar(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: Optional[float] = None
    ema9: Optional[float] = None
    ema21: Optional[float] = None
    is_crossing_candle: bool = False
    pullback_depth: Optional[float] = None
    time_sec: Optional[int] = None


class Level2Level(BaseModel):
    price: float
    shares: int
    orders_count: int


class Level2Snapshot(BaseModel):
    symbol: str
    timestamp: str
    bids: List[Level2Level]
    asks: List[Level2Level]
    spread: float
    bid_depth: int
    ask_depth: int
    imbalance_ratio: float  # (bid - ask) / (bid + ask), from -1.0 to 1.0
    big_seller_detected: bool = False
    iceberg_suspicion: bool = False
    tape_speed: float = 0.0  # transactions per second
    burst_of_red: bool = False


class TapeTick(BaseModel):
    timestamp: str
    price: float
    size: int
    side: str  # "BUY" (at/above ask) or "SELL" (at/below bid)
    condition: str = "Regular"


class ScannerCandidate(BaseModel):
    symbol: str
    price: float
    gap_pct: float
    relative_volume: float
    total_volume: int
    float_shares: float
    catalyst: str
    catalyst_type: str  # Earnings, FDA, Contract, News, None
    spread: float
    ai_score: float  # 0 to 100
    grade: SetupGrade
    news_status: str
    sweet_spot: bool
    reasons: List[str]
    pillars_passed: Dict[str, bool]


class TradeSignal(BaseModel):
    id: str
    symbol: str
    strategy: StrategyType
    signal_type: SignalType
    timestamp: str
    current_price: float
    entry_price: float
    stop_loss: float
    target_price: float
    reward_risk_ratio: float
    recommended_shares: int
    dollar_risk: float
    ai_confidence: float  # 0.0 to 1.0
    pullback_depth_pct: Optional[float] = None
    vwap_status: str
    ema9_status: str
    volume_confirmation: bool
    crossing_candle_confirmed: bool
    reasons: List[str]
    invalidation_criteria: List[str]
    rule_adherence_score: float  # 0 to 100
    kronos_forecast: Optional[Dict[str, Any]] = None


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    SELL_SHORT = "SELL_SHORT"
    BUY_TO_COVER = "BUY_TO_COVER"


class OrderType(str, Enum):
    MARKETABLE_LIMIT = "MARKETABLE_LIMIT"
    STOP_LOSS = "STOP_LOSS"
    PROFIT_TARGET = "PROFIT_TARGET"


class OrderStatus(str, Enum):
    PENDING_RISK = "PENDING_RISK"
    SUBMITTED = "SUBMITTED"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    CLOSED = "CLOSED"


class ExecutionOrder(BaseModel):
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    shares: int
    limit_price: float
    stop_loss: float
    target_price: float
    planned_rr: float
    fill_price: Optional[float] = None
    status: OrderStatus
    created_at: str
    filled_at: Optional[str] = None
    closed_at: Optional[str] = None
    realized_pnl: Optional[float] = None
    realized_r_multiple: Optional[float] = None
    slippage: float = 0.0
    commission: float = 0.0
    strategy: StrategyType
    entry_reason: str
    mistake_tags: List[MistakeTag] = []
    override_reason: Optional[str] = None
    ai_post_trade_summary: Optional[str] = None
    chart_snapshot_url: Optional[str] = None


class AccountCockpitState(BaseModel):
    equity: float
    buying_power: float
    realized_pnl_today: float
    unrealized_pnl: float
    peak_pnl_today: float
    giveback_amount: float
    giveback_pct: float
    daily_loss_limit: float
    daily_loss_consumed_pct: float
    risk_per_trade: float
    active_risk_tier: str
    is_locked_out: bool
    lockout_reason: Optional[str] = None
    market_time_est: str
    is_within_trading_window: bool
    total_trades_today: int
    win_rate_today: float
    average_r_today: float
    active_positions_count: int
