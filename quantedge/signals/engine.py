"""
QuantEdge Signal Engine & Strategy Library
Implements Sections 2 and 4 of Strategic Requirements:
- Gap-and-Go Pullback with Crossing Candle entry
- 50% Pullback Depth Enforcer
- VWAP & 9 EMA Support Verification
- Green vs Red Volume Aggression Balance
- Minimum 2:1 Planned Reward/Risk Verification
- Invalidation Flags & Explainable Confidence Reasons
"""

import uuid
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from quantedge.config import DEFAULT_CONFIG, SystemConfig
from quantedge.data.models import (
    TradeSignal, SignalType, StrategyType, Bar, Level2Snapshot, SetupGrade
)
from quantedge.data.feed import FEED_INSTANCE
from quantedge.signals.kronos_bridge import KRONOS_INSTANCE


class SignalEngine:
    def __init__(self, config: SystemConfig = DEFAULT_CONFIG, feed=FEED_INSTANCE):
        self.config = config
        self.feed = feed

    def calculate_pullback_metrics(self, bars: List[Bar]) -> Tuple[float, float, float, float, bool]:
        """
        Calculates the initial morning run, pullback low, and pullback depth percentage.
        Rule: Must not retrace more than 50% of the initial move.
        Returns (initial_move, current_price, pullback_low, depth_ratio, is_valid)
        """
        if len(bars) < 5:
            return 0.0, 0.0, 0.0, 0.0, True
            
        open_price = bars[0].open
        session_high = max(b.high for b in bars)
        initial_move = session_high - open_price
        
        if initial_move <= 0.05:
            return initial_move, bars[-1].close, bars[-1].low, 0.0, True

        # Find lowest price since session_high occurred
        high_idx = 0
        for i, b in enumerate(bars):
            if b.high == session_high:
                high_idx = i
                break
                
        pullback_bars = bars[high_idx:]
        pullback_low = min(b.low for b in pullback_bars) if pullback_bars else bars[-1].low
        retrace = session_high - pullback_low
        depth_ratio = round(retrace / initial_move, 3)
        
        is_valid = (depth_ratio <= self.config.max_pullback_depth)
        return initial_move, bars[-1].close, pullback_low, depth_ratio, is_valid

    def evaluate_volume_profile(self, bars: List[Bar]) -> Tuple[bool, float, float, str]:
        """
        Rule (Section 4): Green candles should show stronger volume than red candles.
        Returns (is_green_dominant, green_vol, red_vol, description)
        """
        if not bars:
            return True, 0, 0, "No bars"

        recent = bars[-10:]
        green_vol = sum(b.volume for b in recent if b.close >= b.open)
        red_vol = sum(b.volume for b in recent if b.close < b.open)
        total = green_vol + red_vol
        
        green_ratio = round((green_vol / max(1, total)) * 100.0, 1)
        is_green_dominant = green_vol >= red_vol
        
        desc = f"Green volume {green_ratio}% vs Red {100.0 - green_ratio}%"
        return is_green_dominant, green_vol, red_vol, desc

    def evaluate_crossing_candle(self, bars: List[Bar]) -> Tuple[bool, Optional[float]]:
        """
        Rule (Section 4): Buy the crossing candle: first candle to make a new high above prior candle.
        Returns (is_crossing_trigger, prior_high)
        """
        if len(bars) < 2:
            return False, None
            
        current = bars[-1]
        prior = bars[-2]
        
        # Trigger when current candle high or close breaks above prior high
        if current.high > prior.high and current.close >= prior.high:
            return True, prior.high
        return False, prior.high

    def generate_signal(self, symbol: str, strategy: StrategyType = StrategyType.GAP_AND_GO_PULLBACK) -> Optional[TradeSignal]:
        """
        Evaluates real-time price action against the selected strategy rules.
        """
        bars = self.feed.get_bars(symbol)
        if len(bars) < 5:
            return None

        quote = self.feed.get_quote(symbol)
        current_price = quote["price"]
        curr_bar = bars[-1]
        vwap = curr_bar.vwap or current_price
        ema9 = curr_bar.ema9 or current_price
        ema21 = curr_bar.ema21 or current_price

        # Check pullback metrics
        init_move, _, pullback_low, depth_ratio, pullback_valid = self.calculate_pullback_metrics(bars)
        
        # Check volume aggression
        green_dom, g_vol, r_vol, vol_desc = self.evaluate_volume_profile(bars)
        
        # Check crossing candle
        crossing_trigger, prior_high = self.evaluate_crossing_candle(bars)

        # Check Level 2 orderbook signals
        l2 = self.feed.get_level2_snapshot(symbol)

        reasons = []
        invalidation_criteria = []
        passed_rules = 0
        total_rules = 5

        # 1. VWAP & 9 EMA hold status
        holds_vwap = current_price >= vwap
        holds_ema9 = current_price >= (ema9 - 0.02)
        if holds_vwap and holds_ema9:
            passed_rules += 1
            reasons.append(f"Price (${current_price}) holds firmly above VWAP (${vwap}) and 9 EMA (${ema9})")
        else:
            invalidation_criteria.append(f"Loss of VWAP (${vwap}) or 9 EMA (${ema9}) dynamic support")

        # 2. Pullback depth rule (<= 50%)
        if pullback_valid:
            passed_rules += 1
            reasons.append(f"Clean shallow pullback depth of {round(depth_ratio * 100, 1)}% (within <=50% limit)")
        else:
            invalidation_criteria.append(f"Pullback too deep: {round(depth_ratio * 100, 1)}% retracement exceeds 50% threshold")

        # 3. Volume profile (Green > Red)
        if green_dom:
            passed_rules += 1
            reasons.append(f"Buyer aggression confirmed: {vol_desc}")
        else:
            invalidation_criteria.append(f"High red volume surge on pullback: {vol_desc}")

        # 4. Crossing candle entry trigger
        if crossing_trigger:
            passed_rules += 1
            reasons.append(f"Crossing Candle Confirmed: broke prior candle high (${prior_high}) with buy momentum")
        else:
            reasons.append(f"Awaiting crossing candle above prior high (${prior_high})")

        # 5. Order flow tape & L2
        if l2.imbalance_ratio > 0.0 and not l2.burst_of_red:
            passed_rules += 1
            reasons.append(f"Positive Level 2 bid depth imbalance (+{round(l2.imbalance_ratio * 100, 1)}%) & no burst-of-red")
        else:
            if l2.burst_of_red:
                invalidation_criteria.append("Burst of red tape detected: consecutive aggressive market sells")
            if l2.big_seller_detected:
                invalidation_criteria.append("Institutional big seller wall detected on ask")

        # Risk and Stop-Loss Calculation (Section 4):
        # Stop-loss: Hard stop at pullback low or structure low
        stop_loss = round(max(0.01, pullback_low - 0.02), 2)
        stop_distance = max(0.03, round(current_price - stop_loss, 2))
        
        # Position sizing: Dollar risk / Stop distance
        dollar_risk = self.config.risk_per_trade_dollars
        recommended_shares = max(1, int(dollar_risk / stop_distance))
        
        # Reward/Risk: Minimum 2:1 planned R:R before entry
        min_target_gain = stop_distance * self.config.min_reward_risk_ratio
        day_high = self.feed.day_highs.get(symbol, current_price + min_target_gain)
        target_price = round(max(current_price + min_target_gain, day_high), 2)
        planned_rr = round((target_price - current_price) / max(0.01, stop_distance), 2)

        # --- Real Kronos Neural Sequence Forecasting ---
        kronos_pred = KRONOS_INSTANCE.predict_next_bars(bars, horizon_bars=5, symbol=symbol)
        kronos_prob = float(kronos_pred.get("probability_up", 0.50))
        kronos_target = float(kronos_pred.get("projected_target", current_price))
        kronos_change_pct = float(kronos_pred.get("projected_change_pct", 0.0))
        kronos_engine = kronos_pred.get("model_engine", "Kronos-Mini-v1")
        kronos_bias = kronos_pred.get("directional_bias", "NEUTRAL")

        # Composite AI Confidence:
        # 45% Rule Adherence + 55% Kronos Neural Directional Probability
        rule_adherence_score = round((passed_rules / total_rules) * 100.0, 1)
        ai_confidence = round(((rule_adherence_score / 100.0) * 0.45) + (kronos_prob * 0.55), 2)

        # Neural Confirmation / Invalidation Logic
        if kronos_prob >= 0.55:
            reasons.append(
                f"🤖 {kronos_engine}: {int(round(kronos_prob * 100))}% Bullish continuation "
                f"({kronos_change_pct:+.2f}% target ${kronos_target:.2f} over 5 bars)"
            )
        elif kronos_prob <= 0.42:
            invalidation_criteria.append(
                f"🤖 {kronos_engine}: Neural model flags bearish downside drift "
                f"({int(round((1.0 - kronos_prob) * 100))}% downside risk to ${kronos_target:.2f})"
            )

        # Signal Type Determination:
        # If L2 burst of red, topping tail, loss of VWAP, or severe neural breakdown -> AVOID/EXIT
        # If Crossing Candle confirmed + Pullback Valid + Holds VWAP + Neural Bullish Confirmation -> ENTRY
        if l2.burst_of_red or not holds_vwap or depth_ratio > 0.50:
            sig_type = SignalType.AVOID if not crossing_trigger else SignalType.EXIT
        elif crossing_trigger and pullback_valid and holds_vwap and planned_rr >= 2.0 and kronos_prob >= 0.48:
            sig_type = SignalType.ENTRY
        else:
            sig_type = SignalType.AVOID

        return TradeSignal(
            id=f"SIG-{symbol}-{uuid.uuid4().hex[:6].upper()}",
            symbol=symbol,
            strategy=strategy,
            signal_type=sig_type,
            timestamp=datetime.now().strftime("%H:%M:%S"),
            current_price=current_price,
            entry_price=current_price,
            stop_loss=stop_loss,
            target_price=target_price,
            reward_risk_ratio=planned_rr,
            recommended_shares=recommended_shares,
            dollar_risk=dollar_risk,
            ai_confidence=ai_confidence,
            pullback_depth_pct=round(depth_ratio * 100, 1),
            vwap_status="PASS" if holds_vwap else "FAIL",
            ema9_status="PASS" if holds_ema9 else "FAIL",
            volume_confirmation=green_dom,
            crossing_candle_confirmed=crossing_trigger,
            reasons=reasons,
            invalidation_criteria=invalidation_criteria,
            rule_adherence_score=rule_adherence_score,
            kronos_forecast=kronos_pred
        )

    def scan_all_signals(self) -> List[TradeSignal]:
        """Scans all candidates and returns valid active signals."""
        signals = []
        for symbol, meta in self.feed.universe_metadata.items():
            strategy_name = StrategyType(meta.get("strategy", StrategyType.GAP_AND_GO_PULLBACK.value))
            sig = self.generate_signal(symbol, strategy_name)
            if sig:
                signals.append(sig)
        return signals


SIGNAL_ENGINE = SignalEngine()
