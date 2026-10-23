"""
QuantEdge AI Trading System - System Configuration
Aligned with Strategic Requirements Document.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional
from enum import Enum


class RiskTier(str, Enum):
    TIER_1_MICRO = "Tier 1 ($30 - $50)"
    TIER_2_INTERMEDIATE = "Tier 2 ($300 - $500)"
    TIER_3_ADVANCED = "Tier 3 ($3,000 - $5,000)"


class MarketRegimeType(str, Enum):
    BULLISH = "Bullish"
    MIXED = "Mixed"
    BEARISH = "Bearish"
    VOLATILITY_SHOCK = "Volatility Shock"


class SystemConfig(BaseModel):
    # Operating Parameters
    app_name: str = "QuantEdge AI Trading Cockpit"
    version: str = "2.6.0"
    timezone: str = "America/New_York"
    
    # Pillar 1 & 2: Volume & Liquidity Filters
    min_relative_volume: float = 5.0  # At least 5x 50-day average volume
    min_total_volume: int = 500_000   # Sufficient absolute volume
    max_acceptable_slippage_cents: float = 0.05
    
    # Pillar 3: Gap Higher
    min_gap_pct: float = 2.0  # At least 2% above prior close
    
    # Pillar 4: Price Range
    min_stock_price: float = 2.00
    max_stock_price: float = 20.00
    
    # Pillar 5: Float
    ideal_max_float: float = 20_000_000  # < 20M shares
    
    # Pillar 6: Market Regime SPY/QQQ
    active_regime: MarketRegimeType = MarketRegimeType.BULLISH
    
    # Strategy Rules (Section 4)
    max_pullback_depth: float = 0.50  # Must not retrace > 50%
    min_reward_risk_ratio: float = 2.0  # Minimum 2:1 planned R:R
    
    # Discipline & Risk Controls (Section 7)
    active_risk_tier: RiskTier = RiskTier.TIER_1_MICRO
    risk_per_trade_dollars: float = 40.0  # Default within $30 - $50
    account_equity: float = 25_000.0
    daily_loss_limit_dollars: float = 100.0  # Max daily loss
    profit_giveback_pct: float = 0.50  # 50% giveback triggers shutdown
    
    # Time Window (Default hard stop at 10:00 a.m. EST)
    market_open_time: str = "09:30"
    market_cutoff_time: str = "10:00"
    
    # Safety & Governance
    require_override_reason: bool = True
    no_setup_auto_lockout: bool = True
    fomo_lockout_active: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)


DEFAULT_CONFIG = SystemConfig()
