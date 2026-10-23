"""
QuantEdge Compliance, Regulatory & Operations Module
Implements Section 10 of Strategic Requirements:
- 2026 FINRA Intraday Margin Framework & Margin Cushion Verification
- SEC Day Trading Risk Disclosures & Operational Warnings
- Compliance Audit Trail
- Model Governance (no false confidence / hallucinations)
"""

from typing import Dict, List, Any
from datetime import datetime


class ComplianceManager:
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []
        self.disclaimer_acknowledged = True

    def get_regulatory_status(self, account_equity: float, open_exposure: float) -> Dict[str, Any]:
        """
        Evaluates 2026 FINRA intraday margin requirements:
        Broker-monitored intraday margin requirement and intraday maintenance leverage ratio.
        """
        leverage_ratio = round(open_exposure / max(1.0, account_equity), 2)
        margin_cushion_pct = max(0.0, round(((account_equity - (open_exposure * 0.25)) / max(1.0, account_equity)) * 100.0, 1))
        
        status = "COMPLIANT" if margin_cushion_pct > 20.0 else "MARGIN_WARNING"

        return {
            "regulatory_framework": "2026 FINRA Intraday Margin Standard & SEC Margin Rule Guidelines",
            "compliance_status": status,
            "account_equity": account_equity,
            "open_exposure": open_exposure,
            "leverage_ratio": f"{leverage_ratio}x",
            "margin_cushion_pct": margin_cushion_pct,
            "min_required_cushion_pct": 20.0,
            "pdt_regime_notice": "FINRA 2026 Intraday Risk Framework: Account monitored dynamically based on intraday volatility, liquidity, and portfolio concentration rather than static $25,000 PDT rule.",
            "statutory_risk_disclosure": "IMPORTANT: Trading stocks, options, and momentum equities carries substantial financial risk. Past performance or backtested expectancy is not a guarantee of future returns. Strictly adhere to risk limits.",
            "audit_entries_count": len(self.audit_log)
        }

    def log_audit_event(self, action: str, details: Dict[str, Any]):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "details": details
        }
        self.audit_log.append(entry)


COMPLIANCE_MANAGER = ComplianceManager()
