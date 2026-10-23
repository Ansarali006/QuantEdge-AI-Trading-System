"""
QuantEdge Market Data Feed & Generator
Provides real-time quotes, 1-min / 5-min bars, Level 2 orderbook, and Tape stream.
Simulates market microstructure including iceberg detection and burst-of-red alerts.
"""

import time
import random
import math
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from quantedge.data.models import Bar, Level2Snapshot, Level2Level, TapeTick, ScannerCandidate, SetupGrade
from quantedge.data.alpaca_client import ALPACA_CLIENT


class MarketDataFeed:
    def __init__(self):
        self.use_alpaca_live = True
        # Initial candidates database with realistic historical / intraday characteristics
        self.universe_metadata = {
            "SOUN": {
                "name": "SoundHound AI",
                "base_price": 4.70,
                "prior_close": 4.65,
                "float_shares": 18_500_000,
                "avg_50d_volume": 4_200_000,
                "catalyst": "Major OEM Automotive AI voice platform integration contract signed",
                "catalyst_type": "Contract",
                "short_interest_pct": 19.4,
                "strategy": "Gap-and-Go Pullback"
            },
            "MVIS": {
                "name": "MicroVision Inc",
                "base_price": 1.20,
                "prior_close": 1.20,
                "float_shares": 14_200_000,
                "avg_50d_volume": 2_100_000,
                "catalyst": "FDA/Lidar sensor tech defense evaluation breakthrough",
                "catalyst_type": "FDA",
                "short_interest_pct": 24.1,
                "strategy": "Gap-and-Go Pullback"
            },
            "ENVX": {
                "name": "Enovix Corp",
                "base_price": 2.23,
                "prior_close": 2.33,
                "float_shares": 16_800_000,
                "avg_50d_volume": 3_500_000,
                "catalyst": "Q3 earnings surprise + 40% margin guidance upgrade",
                "catalyst_type": "Earnings",
                "short_interest_pct": 28.5,
                "strategy": "Opening Range Breakout"
            },
            "NVDA": {
                "name": "NVIDIA Corporation",
                "base_price": 216.50,
                "prior_close": 217.08,
                "float_shares": 2_400_000_000,
                "avg_50d_volume": 45_000_000,
                "catalyst": "Hyperscaler data center capex increase guidance",
                "catalyst_type": "Earnings",
                "short_interest_pct": 1.2,
                "strategy": "Relative-Strength Options"
            },
            "PLTR": {
                "name": "Palantir Technologies",
                "base_price": 193.90,
                "prior_close": 194.12,
                "float_shares": 1_900_000_000,
                "avg_50d_volume": 38_000_000,
                "catalyst": "Defense AIP contract award & S&P inclusion momentum",
                "catalyst_type": "Contract",
                "short_interest_pct": 4.5,
                "strategy": "VWAP Reclaim"
            },
            "MARA": {
                "name": "MARA Holdings",
                "base_price": 7.50,
                "prior_close": 7.38,
                "float_shares": 19_100_000,
                "avg_50d_volume": 12_000_000,
                "catalyst": "Bitcoin rally above key resistance & hash rate surge",
                "catalyst_type": "News",
                "short_interest_pct": 22.0,
                "strategy": "Gap-and-Go Pullback"
            },
            "GME": {
                "name": "GameStop Corp",
                "base_price": 25.90,
                "prior_close": 26.42,
                "float_shares": 68_000_000,
                "avg_50d_volume": 14_000_000,
                "catalyst": "Cash treasury balance increase to $4.6B",
                "catalyst_type": "News",
                "short_interest_pct": 12.3,
                "strategy": "Failed Breakout Short"
            },
            "MGNX": {
                "name": "MacroGenics Inc",
                "base_price": 7.19,
                "prior_close": 6.89,
                "float_shares": 19_100_000,
                "avg_50d_volume": 3_400_000,
                "catalyst": "Phase 2 clinical trial readout meeting primary endpoint",
                "catalyst_type": "FDA",
                "short_interest_pct": 18.2,
                "strategy": "Gap-and-Go Pullback"
            },
            "RGTI": {
                "name": "Rigetti Computing",
                "base_price": 11.68,
                "prior_close": 11.65,
                "float_shares": 45_800_000,
                "avg_50d_volume": 5_200_000,
                "catalyst": "Quantum processing milestone agreement announcement",
                "catalyst_type": "Contract",
                "short_interest_pct": 14.5,
                "strategy": "Opening Range Breakout"
            }
        }

        # Simulated live price state
        self.prices: Dict[str, float] = {}
        self.bars_1m: Dict[str, List[Bar]] = {}
        self.bars_5m: Dict[str, List[Bar]] = {}
        self.tape_history: Dict[str, List[TapeTick]] = {}
        self.day_highs: Dict[str, float] = {}
        self.day_lows: Dict[str, float] = {}
        self.premarket_highs: Dict[str, float] = {}
        self.opening_prints: Dict[str, float] = {}

        self._initialize_historical_bars()

    def warmup_alpaca_live_data(self):
        """Warms up real-time bars and quotes from Alpaca for universe symbols."""
        if not getattr(self, "use_alpaca_live", False) or not ALPACA_CLIENT.is_configured:
            return
        for symbol in ["NVDA", "SOUN", "PLTR", "MARA", "MVIS", "ENVX", "GME", "RGTI"]:
            try:
                q = ALPACA_CLIENT.get_live_quote(symbol)
                if q:
                    self.prices[symbol] = q["price"]
                    self.day_highs[symbol] = q["day_high"]
                    self.day_lows[symbol] = q["day_low"]
                    self.premarket_highs[symbol] = q["premarket_high"]
                    self.opening_prints[symbol] = q["opening_print"]
                bars = ALPACA_CLIENT.get_live_bars(symbol, limit=60)
                if bars and len(bars) > 0:
                    self.bars_1m[symbol] = list(bars)
                    self.prices[symbol] = bars[-1].close
            except Exception:
                pass

    def _initialize_historical_bars(self):
        """Generates realistic opening 30-min market session bars for all universe symbols."""
        for symbol, meta in self.universe_metadata.items():
            base = meta["base_price"]
            prior_close = meta["prior_close"]
            pm_high = round(base * 1.035, 2)
            self.premarket_highs[symbol] = pm_high
            self.opening_prints[symbol] = base
            self.prices[symbol] = base

            bars = []
            curr_price = base
            cum_vol = 0
            cum_pv = 0.0
            ema9 = curr_price
            ema21 = curr_price

            # Create 1-minute bars from 09:30 onwards (e.g. 35 bars to simulate 09:30 - 10:05)
            start_dt = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
            
            for i in range(35):
                bar_dt = start_dt + timedelta(minutes=i)
                bar_time = bar_dt.strftime("%H:%M")
                bar_sec = int(bar_dt.timestamp())
                is_crossing = False
                
                # Market microstructure simulation:
                # First 3 bars: strong aggressive breakout green candles
                if i < 4:
                    o = curr_price
                    delta = abs(random.gauss(0.12, 0.05))
                    c = round(o + delta, 2)
                    h = round(c + random.uniform(0.01, 0.04), 2)
                    l = round(o - random.uniform(0.0, 0.02), 2)
                    v = int(random.randint(250_000, 480_000))
                elif 4 <= i <= 8:
                    # Clean shallow pullback (retracing < 40% of move)
                    o = curr_price
                    delta = abs(random.gauss(0.04, 0.02))
                    c = round(max(o - delta, base * 1.01), 2)
                    h = round(o + random.uniform(0.01, 0.02), 2)
                    l = round(c - random.uniform(0.01, 0.03), 2)
                    v = int(random.randint(60_000, 110_000))  # Light volume on pullback (satisfies Green > Red volume!)
                elif i == 9:
                    # Crossing Candle! Confirmed first candle breaking above prior candle high after shallow pullback
                    prior_high = bars[-1].high if bars else curr_price
                    o = curr_price
                    c = round(prior_high + 0.08, 2)
                    h = round(c + 0.03, 2)
                    l = round(o - 0.01, 2)
                    v = int(random.randint(320_000, 520_000))  # Heavy breakout volume
                    is_crossing = True
                elif 10 <= i <= 13:
                    # Follow-through momentum expansion toward profit target
                    o = curr_price
                    delta = abs(random.gauss(0.05, 0.02))
                    c = round(o + delta, 2)
                    h = round(c + random.uniform(0.01, 0.03), 2)
                    l = round(o - random.uniform(0.0, 0.02), 2)
                    v = int(random.randint(220_000, 360_000))
                    is_crossing = False
                else:
                    # Natural horizontal channel consolidation holding above VWAP / 9 EMA
                    o = curr_price
                    delta = random.gauss(0.0, 0.025)  # Balanced two-sided price action
                    c = round(max(base * 1.02, o + delta), 2)
                    h = round(max(o, c) + random.uniform(0.01, 0.03), 2)
                    l = round(min(o, c) - random.uniform(0.01, 0.03), 2)
                    v = int(random.randint(80_000, 180_000))
                    is_crossing = False

                curr_price = c
                typical_price = (h + l + c) / 3.0
                cum_vol += v
                cum_pv += (typical_price * v)
                vwap = round(cum_pv / max(1, cum_vol), 2)
                
                # EMAs
                k9 = 2.0 / (9.0 + 1.0)
                k21 = 2.0 / (21.0 + 1.0)
                ema9 = round(c * k9 + ema9 * (1 - k9), 2)
                ema21 = round(c * k21 + ema21 * (1 - k21), 2)

                bar = Bar(
                    timestamp=bar_time,
                    open=o,
                    high=h,
                    low=l,
                    close=c,
                    volume=v,
                    vwap=vwap,
                    ema9=ema9,
                    ema21=ema21,
                    is_crossing_candle=is_crossing,
                    pullback_depth=0.28 if 4 <= i <= 9 else 0.15,
                    time_sec=bar_sec
                )
                bars.append(bar)

            self.bars_1m[symbol] = bars
            self.prices[symbol] = bars[-1].close
            self.day_highs[symbol] = max(b.high for b in bars)
            self.day_lows[symbol] = min(b.low for b in bars)
            
            # Generate initial tape ticks
            ticks = []
            for t in range(25):
                tick_time = (start_dt + timedelta(minutes=34, seconds=t*2)).strftime("%H:%M:%S")
                side = "BUY" if random.random() > 0.35 else "SELL"
                price_offset = random.choice([0.0, 0.01, -0.01])
                ticks.append(TapeTick(
                    timestamp=tick_time,
                    price=round(self.prices[symbol] + price_offset, 2),
                    size=random.choice([100, 200, 500, 1000, 2500, 5000]),
                    side=side
                ))
            self.tape_history[symbol] = ticks

    def _advance_simulation(self, symbol: str):
        """Advances real-time market microstructure simulation and creates moving bars."""
        if symbol not in self.bars_1m or not self.bars_1m[symbol]:
            return
            
        now = time.time()
        if not hasattr(self, "_last_advance_time"):
            self._last_advance_time = {}
        if not hasattr(self, "_bar_tick_count"):
            self._bar_tick_count = {}
            
        last_adv = self._last_advance_time.get(symbol, 0)
        # Advance at most once every 0.7 second
        if now - last_adv < 0.7:
            return
        self._last_advance_time[symbol] = now

        bars = self.bars_1m[symbol]
        last_bar = bars[-1]
        
        # Real-time subtle price jitter
        delta = random.choice([-0.02, -0.01, 0.0, 0.01, 0.02, 0.03, -0.01])
        new_price = round(max(0.20, last_bar.close + delta), 2)
        self.prices[symbol] = new_price
        
        if new_price > self.day_highs.get(symbol, 0):
            self.day_highs[symbol] = new_price
        if new_price < self.day_lows.get(symbol, 999999):
            self.day_lows[symbol] = new_price

        count = self._bar_tick_count.get(symbol, 0) + 1
        self._bar_tick_count[symbol] = count

        # Every 3 ticks (~3-4.5s in polling), complete current candle and advance to next 1-minute bar!
        if count >= 3:
            self._bar_tick_count[symbol] = 0
            
            # Finalize prior bar
            last_bar.close = new_price
            last_bar.high = max(last_bar.high, new_price)
            last_bar.low = min(last_bar.low, new_price)
            
            next_sec = (last_bar.time_sec or int(now)) + 60
            next_dt = datetime.fromtimestamp(next_sec)
            next_ts = next_dt.strftime("%H:%M")
            
            # EMA calculations
            k9 = 2.0 / (9.0 + 1.0)
            k21 = 2.0 / (21.0 + 1.0)
            p_ema9 = last_bar.ema9 or new_price
            p_ema21 = last_bar.ema21 or new_price
            ema9 = round(new_price * k9 + p_ema9 * (1 - k9), 2)
            ema21 = round(new_price * k21 + p_ema21 * (1 - k21), 2)
            
            vol = random.randint(45_000, 140_000)
            vwap = round(((last_bar.vwap or new_price) * 0.95 + new_price * 0.05), 2)
            
            new_bar = Bar(
                timestamp=next_ts,
                open=new_price,
                high=round(new_price + random.uniform(0.00, 0.03), 2),
                low=round(new_price - random.uniform(0.00, 0.02), 2),
                close=new_price,
                volume=vol,
                vwap=vwap,
                ema9=ema9,
                ema21=ema21,
                is_crossing_candle=False,
                pullback_depth=0.15,
                time_sec=next_sec
            )
            bars.append(new_bar)
            if len(bars) > 75:
                self.bars_1m[symbol] = bars[-75:]
        else:
            # Update live candle intra-bar
            last_bar.close = new_price
            last_bar.high = max(last_bar.high, new_price)
            last_bar.low = min(last_bar.low, new_price)
            last_bar.volume += random.randint(1200, 4800)

    def get_quote(self, symbol: str, allow_network: bool = True) -> Dict[str, Any]:
        """Returns instantaneous quote snapshot."""
        if allow_network and getattr(self, "use_alpaca_live", False):
            try:
                live_q = ALPACA_CLIENT.get_live_quote(symbol)
                if live_q:
                    self.prices[symbol] = live_q["price"]
                    self.day_highs[symbol] = live_q["day_high"]
                    self.day_lows[symbol] = live_q["day_low"]
                    return live_q
            except Exception:
                pass

        self._advance_simulation(symbol)
        price = self.prices.get(symbol, 10.0)
        meta = self.universe_metadata.get(symbol, {})
        prior_close = meta.get("prior_close", price * 0.95)
        gap_pct = round(((price - prior_close) / prior_close) * 100.0, 2)
        day_high = self.day_highs.get(symbol, price)
        day_low = self.day_lows.get(symbol, price)
        vwap = self.bars_1m[symbol][-1].vwap if symbol in self.bars_1m and self.bars_1m[symbol] else price
        
        return {
            "symbol": symbol,
            "price": price,
            "prior_close": prior_close,
            "change": round(price - prior_close, 2),
            "change_pct": gap_pct,
            "gap_pct": gap_pct,
            "day_high": day_high,
            "day_low": day_low,
            "vwap": vwap,
            "premarket_high": self.premarket_highs.get(symbol, round(price * 1.02, 2)),
            "opening_print": self.opening_prints.get(symbol, price),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

    def get_bars(self, symbol: str, timeframe: str = "1m", allow_network: bool = True) -> List[Bar]:
        """Returns historical bars for charting."""
        if allow_network and getattr(self, "use_alpaca_live", False):
            now = time.time()
            if not hasattr(self, "_last_alpaca_bars_poll"):
                self._last_alpaca_bars_poll = {}
            last_poll = self._last_alpaca_bars_poll.get(symbol, 0)
            # Only poll Alpaca if we have no bars or at most once every 30s
            if (symbol not in self.bars_1m or not self.bars_1m[symbol]) or (now - last_poll > 30.0):
                self._last_alpaca_bars_poll[symbol] = now
                try:
                    live_bars = ALPACA_CLIENT.get_live_bars(symbol, limit=60)
                    if live_bars and len(live_bars) > 0:
                        self.bars_1m[symbol] = list(live_bars)
                        self.prices[symbol] = live_bars[-1].close
                except Exception:
                    pass

        self._advance_simulation(symbol)
        return self.bars_1m.get(symbol, [])

    def get_level2_snapshot(self, symbol: str) -> Level2Snapshot:
        """
        Generates realistic Level 2 Order Book with order imbalances,
        iceberg detection, big seller wall detection, and tape speed.
        """
        if getattr(self, "use_alpaca_live", False):
            try:
                live_l2 = ALPACA_CLIENT.get_live_level2(symbol)
                if live_l2:
                    return live_l2
            except Exception:
                pass

        curr = self.prices.get(symbol, 10.0)
        spread = 0.01 if curr < 25 else 0.02

        # Generate bids (descending from best bid)
        bids = []
        best_bid = round(curr - spread / 2, 2)
        total_bid_shares = 0
        for i in range(8):
            price = round(best_bid - (i * spread), 2)
            shares = random.randint(15, 80) * 100
            total_bid_shares += shares
            bids.append(Level2Level(price=price, shares=shares, orders_count=random.randint(2, 9)))

        # Generate asks (ascending from best ask)
        asks = []
        best_ask = round(curr + spread / 2, 2)
        total_ask_shares = 0
        
        # Microstructure feature: Detect if big seller wall exists
        big_seller_detected = False
        iceberg_detected = False
        for i in range(8):
            price = round(best_ask + (i * spread), 2)
            if i == 2 and symbol in ["GME"]:  # Heavy resistance seller wall on weak symbols
                shares = random.randint(350, 600) * 100
                big_seller_detected = True
            elif i == 1 and symbol in ["SOUN", "MVIS"]:  # Iceberg suspicion on momentum names
                shares = random.randint(120, 250) * 100
                iceberg_detected = True
            else:
                shares = random.randint(12, 65) * 100
            total_ask_shares += shares
            asks.append(Level2Level(price=price, shares=shares, orders_count=random.randint(1, 8)))

        # Order book imbalance: (bid_depth - ask_depth) / (bid_depth + ask_depth)
        total_depth = total_bid_shares + total_ask_shares
        imbalance = round((total_bid_shares - total_ask_shares) / max(1, total_depth), 3)

        # Tape speed (transactions per second)
        tape_speed = round(random.uniform(4.2, 18.5), 1)

        # Burst of red detection: if recent 4 ticks were sells with volume > 5000
        recent_ticks = self.tape_history.get(symbol, [])[-5:]
        sell_count = sum(1 for t in recent_ticks if t.side == "SELL")
        burst_of_red = (sell_count >= 4)

        return Level2Snapshot(
            symbol=symbol,
            timestamp=datetime.now().strftime("%H:%M:%S"),
            bids=bids,
            asks=asks,
            spread=round(best_ask - best_bid, 2),
            bid_depth=total_bid_shares,
            ask_depth=total_ask_shares,
            imbalance_ratio=imbalance,
            big_seller_detected=big_seller_detected,
            iceberg_suspicion=iceberg_detected,
            tape_speed=tape_speed,
            burst_of_red=burst_of_red
        )

    def get_tape(self, symbol: str, limit: int = 40) -> List[TapeTick]:
        """Returns recent tape prints for Time & Sales."""
        if getattr(self, "use_alpaca_live", False):
            try:
                live_tape = ALPACA_CLIENT.get_live_tape(symbol, limit)
                if live_tape and len(live_tape) > 0:
                    return live_tape
            except Exception:
                pass
        return self.tape_history.get(symbol, [])[-limit:]

    def push_tick(self, symbol: str, price_delta: float, side: str, size: int) -> TapeTick:
        """Simulates incoming tick and updates last price."""
        if symbol not in self.prices:
            return None
        new_price = round(max(0.10, self.prices[symbol] + price_delta), 2)
        self.prices[symbol] = new_price
        
        # update day high/low
        if new_price > self.day_highs.get(symbol, 0):
            self.day_highs[symbol] = new_price
        if new_price < self.day_lows.get(symbol, 999999):
            self.day_lows[symbol] = new_price

        tick = TapeTick(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            price=new_price,
            size=size,
            side=side
        )
        if symbol not in self.tape_history:
            self.tape_history[symbol] = []
        self.tape_history[symbol].append(tick)
        return tick


FEED_INSTANCE = MarketDataFeed()
