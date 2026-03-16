"""
Shared data models for all FundHQ agents.
Lightweight dataclasses — no external dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid


@dataclass
class Signal:
    """A trading signal from any agent division."""
    coin: str
    side: str                          # LONG or SHORT
    source: str                        # e.g. "onchain:hyperliquid", "technical:quant"
    conviction: str = "medium"         # high, medium, low
    size_usd: float = 0.0
    entry_px: float = 0.0
    leverage: float = 1.0
    regime: str = "unknown"
    grade: str = "?"
    metadata: dict = field(default_factory=dict)
    id: str = field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:12]}")
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "coin": self.coin,
            "side": self.side,
            "source": self.source,
            "conviction": self.conviction,
            "size_usd": self.size_usd,
            "entry_px": self.entry_px,
            "leverage": self.leverage,
            "regime": self.regime,
            "grade": self.grade,
            "metadata": self.metadata,
            "created": self.created,
        }


@dataclass
class Entity:
    """A tracked entity — wallet, exchange, protocol, etc."""
    address: str
    label: str = ""
    venue: str = ""                    # hyperliquid, onchain, cex
    grade: str = "?"
    tags: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "label": self.label or self.address[:10],
            "venue": self.venue,
            "grade": self.grade,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class Alert:
    """An alert pushed to Fund HQ's dashboard."""
    title: str
    content: str
    source: str                        # agent that generated it
    severity: str = "info"             # info, warning, opportunity
    tags: list = field(default_factory=list)
    dismissed: bool = False
    id: str = field(default_factory=lambda: f"alert_{uuid.uuid4().hex[:12]}")
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.source,
            "title": self.title,
            "content": self.content,
            "severity": self.severity,
            "dismissed": self.dismissed,
            "created": self.created,
            "source": self.source,
            "tags": self.tags,
        }
