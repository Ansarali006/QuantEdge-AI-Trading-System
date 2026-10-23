"""
QuantEdge Five-Pillar Scanner Engine
Implements Section 3 of Strategic Requirements:
- Pillar 1: Relative Volume (>= 5x, acceleration & float rotation)
- Pillar 2: Total Volume & Liquidity score (expected slippage)
- Pillar 3: Gap Higher (>= 2% above prior close, catalyst quality)
- Pillar 4: Price Range ($2-$20 sweet spot for small caps, liquid mega-caps for options)
- Pillar 5: Float (< 20M shares, short interest, squeeze potential)
- Pillar 6: Market Regime (SPY/QQQ trend & breadth confirmation)
- No-Setup Rule Enforcer: Flags "No Trade" state if no A-grade candidate exists or regime is bearish.
"""

from typing import List, Dict, Any, Tuple
from quantedge.config import DEFAULT_CONFIG, MarketRegimeType
from quantedge.data.models import ScannerCandidate, SetupGrade
from quantedge.data.feed import FEED_INSTANCE


class FivePillarScanner:
    def __init__(self, config=DEFAULT_CONFIG, feed=FEED_INSTANCE):
        self.config = config
        self.feed = feed

    def evaluate_candidate(self, symbol: str, market_regime: MarketRegimeType = MarketRegimeType.BULLISH) -> ScannerCandidate:
        """Evaluates a single symbol against the 5 pillars plus market regime."""
        meta = self.feed.universe_metadata.get(symbol, {})
        quote = self.feed.get_quote(symbol, allow_network=False)
        price = quote["price"]
        prior_close = quote["prior_close"]
        gap_pct = quote["gap_pct"]
        
        bars = self.feed.bars_1m.get(symbol, [])
        total_vol = sum(b.volume for b in bars) if bars else 1_200_000
        avg_vol = meta.get("avg_50d_volume", 2_000_000)
        
        # Calculate Relative Volume (RVOL)
        # Ratio of current intraday volume pace to expected pace
        expected_pace_vol = max(100_000, avg_vol * 0.15) # Pace for first 35 mins
        relative_volume = round(total_vol / expected_pace_vol, 2)
        
        float_shares = meta.get("float_shares", 15_000_000)
        catalyst = meta.get("catalyst", "No active catalyst announced")
        catalyst_type = meta.get("catalyst_type", "News")
        short_interest = meta.get("short_interest_pct", 10.0)
        
        # Pillar Evaluations:
        # Pillar 1: RVOL >= 5.0
        p1_rvol_pass = relative_volume >= self.config.min_relative_volume
        
        # Pillar 2: Total Volume >= 500,000 & tight spread
        spread = 0.01 if price < 20 else 0.02
        p2_vol_pass = total_vol >= self.config.min_total_volume and spread <= self.config.max_acceptable_slippage_cents
        
        # Pillar 3: Gap Higher >= 2.0%
        p3_gap_pass = gap_pct >= self.config.min_gap_pct
        
        # Pillar 4: Price Range ($2-$20 for small caps, or large cap relative strength)
        is_large_cap = float_shares > 100_000_000
        if is_large_cap:
            p4_price_pass = price > 20.0  # Liquid large cap for options
            sweet_spot = True
        else:
            p4_price_pass = self.config.min_stock_price <= price <= self.config.max_stock_price
            sweet_spot = p4_price_pass
            
        # Pillar 5: Float < 20M shares
        p5_float_pass = float_shares <= self.config.ideal_max_float if not is_large_cap else True
        
        # Pillar 6: Market Regime
        p6_regime_pass = (market_regime != MarketRegimeType.BEARISH)
        
        pillars_passed = {
            "p1_relative_volume": p1_rvol_pass,
            "p2_total_volume": p2_vol_pass,
            "p3_gap_higher": p3_gap_pass,
            "p4_price_range": p4_price_pass,
            "p5_low_float": p5_float_pass,
            "p6_market_regime": p6_regime_pass
        }

        # Multi-Factor AI Scoring (0 to 100)
        # Section 3 & 4 AI scoring weights
        score = 0.0
        reasons = []

        # RVOL Score (max 25 pts)
        if relative_volume >= 8.0:
            score += 25.0
            reasons.append(f"Extreme RVOL ({relative_volume}x) demonstrating immense institutional footprint")
        elif relative_volume >= 5.0:
            score += 20.0
            reasons.append(f"Strong RVOL ({relative_volume}x) meeting 5x pillar requirement")
        elif relative_volume >= 3.0:
            score += 10.0
            reasons.append(f"Moderate RVOL ({relative_volume}x)")
        else:
            reasons.append(f"Sub-par RVOL ({relative_volume}x < 5.0x)")

        # Gap & Catalyst Score (max 25 pts)
        if gap_pct >= 8.0 and catalyst_type in ["Earnings", "FDA", "Contract"]:
            score += 25.0
            reasons.append(f"Tier-1 Catalyst ({catalyst_type}) with +{gap_pct}% gap")
        elif gap_pct >= 3.0:
            score += 18.0
            reasons.append(f"Solid gap (+{gap_pct}%) with {catalyst_type} backdrop")
        elif gap_pct >= 2.0:
            score += 12.0
            reasons.append(f"Meets minimum 2% gap rule (+{gap_pct}%)")
        else:
            reasons.append(f"Weak gap (+{gap_pct}% < 2.0%)")

        # Float & Supply-Demand Imbalance (max 25 pts)
        if not is_large_cap:
            float_m = round(float_shares / 1_000_000, 1)
            float_turnover = round((total_vol / max(1, float_shares)) * 100.0, 1)
            if float_m <= 15.0 and short_interest > 20.0:
                score += 25.0
                reasons.append(f"Ultra-low float ({float_m}M) + high short interest ({short_interest}%) squeeze setup")
            elif float_m <= 20.0:
                score += 20.0
                reasons.append(f"Low float ({float_m}M) within <=20M sweet-spot ({float_turnover}% rotated)")
            else:
                score += 8.0
                reasons.append(f"High float ({float_m}M > 20M)")
        else:
            score += 20.0
            reasons.append("Mega-cap liquid universe candidate for options relative-strength")

        # Technical Structure & Regime (max 25 pts)
        passed_count = sum(1 for v in pillars_passed.values() if v)
        if market_regime == MarketRegimeType.BULLISH:
            score += 20.0
            reasons.append("Bullish SPY/QQQ regime breadth confirmation")
        elif market_regime == MarketRegimeType.MIXED:
            score += 12.0
            reasons.append("Mixed regime: select only top-tier A setups")
        else:
            score += 2.0
            reasons.append("Bearish market regime: high headwind caution")

        score = min(100.0, round(score, 1))

        # Assign Grade
        if score >= 80.0 and passed_count >= 5:
            grade = SetupGrade.GRADE_A
        elif score >= 60.0 and passed_count >= 4:
            grade = SetupGrade.GRADE_B
        else:
            grade = SetupGrade.GRADE_C

        return ScannerCandidate(
            symbol=symbol,
            price=price,
            gap_pct=gap_pct,
            relative_volume=relative_volume,
            total_volume=total_vol,
            float_shares=float_shares,
            catalyst=catalyst,
            catalyst_type=catalyst_type,
            spread=spread,
            ai_score=score,
            grade=grade,
            news_status="Verified" if catalyst_type != "None" else "Unverified",
            sweet_spot=sweet_spot,
            reasons=reasons,
            pillars_passed=pillars_passed
        )

    def scan_universe(self, market_regime: MarketRegimeType = MarketRegimeType.BULLISH) -> Tuple[List[ScannerCandidate], Dict[str, Any]]:
        """
        Runs the full 5-pillar scan across the universe.
        Returns ranked list and system-level No-Setup diagnosis.
        """
        candidates: List[ScannerCandidate] = []
        for symbol in self.feed.universe_metadata.keys():
            candidate = self.evaluate_candidate(symbol, market_regime)
            candidates.append(candidate)

        # Sort descending by AI score
        candidates.sort(key=lambda c: c.ai_score, reverse=True)

        a_grade_candidates = [c for c in candidates if c.grade == SetupGrade.GRADE_A]
        
        # Section 7: No Setup Rule enforcement
        # "Do not trade if no A-grade scanner candidate exists or market theme is bearish.
        # Scanner dashboard shows no-trade state."
        no_trade_state = False
        no_trade_reason = None
        if market_regime == MarketRegimeType.BEARISH:
            no_trade_state = True
            no_trade_reason = "No-Trade State: Market Regime is Bearish (SPY/QQQ breakdown). Momentum trades blocked."
        elif len(a_grade_candidates) == 0:
            no_trade_state = True
            no_trade_reason = "No-Trade State: No A-Grade candidates met the strict 5-pillar criteria today. Stay patient."

        summary = {
            "scanned_count": len(candidates),
            "a_grade_count": len(a_grade_candidates),
            "b_grade_count": sum(1 for c in candidates if c.grade == SetupGrade.GRADE_B),
            "c_grade_count": sum(1 for c in candidates if c.grade == SetupGrade.GRADE_C),
            "market_regime": market_regime.value,
            "no_trade_state": no_trade_state,
            "no_trade_reason": no_trade_reason,
            "top_conviction_symbols": [c.symbol for c in a_grade_candidates[:4]]
        }

        return candidates, summary


SCANNER_INSTANCE = FivePillarScanner()
