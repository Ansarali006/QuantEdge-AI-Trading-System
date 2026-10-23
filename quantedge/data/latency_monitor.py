"""
Market Data Latency and Health Monitor
Ensures data stream health, measures quote-to-execution latency,
and triggers automatic signal suspension when latency exceeds safe thresholds.
"""

import time
from typing import Dict, Any, Tuple


class LatencyMonitor:
    def __init__(self, max_allowed_latency_ms: float = 350.0):
        self.max_allowed_latency_ms = max_allowed_latency_ms
        self.last_heartbeat = time.time()
        self.last_latency_ms = 42.0  # Normal low latency default
        self.signals_suspended = False
        self.suspension_reason = None
        self.total_health_checks = 0
        self.failed_checks = 0

    def record_tick(self, feed_timestamp_sec: float) -> Tuple[bool, float]:
        """
        Record timestamp of incoming quote and calculate latency.
        Returns (is_healthy, latency_ms).
        """
        now = time.time()
        self.last_heartbeat = now
        self.total_health_checks += 1
        
        # Calculate latency in milliseconds
        latency_ms = max(0.0, (now - feed_timestamp_sec) * 1000.0)
        self.last_latency_ms = round(latency_ms, 2)
        
        if latency_ms > self.max_allowed_latency_ms:
            self.signals_suspended = True
            self.failed_checks += 1
            self.suspension_reason = f"High Latency: {self.last_latency_ms}ms exceeds threshold {self.max_allowed_latency_ms}ms"
            return False, self.last_latency_ms
        else:
            self.signals_suspended = False
            self.suspension_reason = None
            return True, self.last_latency_ms

    def check_staleness(self, max_stale_seconds: float = 5.0) -> bool:
        """Checks if feed stopped receiving updates."""
        elapsed = time.time() - self.last_heartbeat
        if elapsed > max_stale_seconds:
            self.signals_suspended = True
            self.suspension_reason = f"Data Feed Stalled: No quote received for {round(elapsed, 1)}s"
            return False
        return True

    def get_status(self) -> Dict[str, Any]:
        return {
            "healthy": not self.signals_suspended,
            "latency_ms": self.last_latency_ms,
            "max_allowed_ms": self.max_allowed_latency_ms,
            "signals_suspended": self.signals_suspended,
            "suspension_reason": self.suspension_reason,
            "last_heartbeat": self.last_heartbeat,
            "uptime_ratio": 1.0 - (self.failed_checks / max(1, self.total_health_checks))
        }
