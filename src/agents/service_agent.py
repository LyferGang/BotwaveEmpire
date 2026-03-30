"""
Service Business Agent
Handles service business quotes, customer management, and job scheduling
Generic agent for any service-based business (plumbing, HVAC, electrical, etc.)
"""

import re
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from core.base_agent import BaseAgent
from core.config import Config


class IssueType(Enum):
    """Classification of service issues for pricing."""
    LEAK = "leak"
    CLOGGED_DRAIN = "clogged_drain"
    TOILET_ISSUE = "toilet_issue"
    WATER_HEATER = "water_heater"
    PIPING_REPAIR = "piping_repair"
    INSTALLATION = "installation"
    EMERGENCY = "emergency"
    ELECTRICAL = "electrical"
    HVAC = "hvac"
    GENERAL = "general"
    UNKNOWN = "unknown"


@dataclass
class Quote:
    """Generated quote for a service request."""
    conversation_id: str
    phone: str
    issue_type: str
    description: str
    price_low: float
    price_high: float
    estimated_hours: int
    status: str = "pending"
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()


# Pricing knowledge base - customizable per business type
PRICE_TABLE = {
    IssueType.LEAK: {
        "low": 100, "high": 500,
        "keywords": ["leak", "leaking", "dripping", "burst", "water"]
    },
    IssueType.CLOGGED_DRAIN: {
        "low": 75, "high": 250,
        "keywords": ["clog", "drain", "slow drain", "backed up", "gurgling"]
    },
    IssueType.TOILET_ISSUE: {
        "low": 150, "high": 450,
        "keywords": ["toilet", "running", "not flushing", "flapper"]
    },
    IssueType.WATER_HEATER: {
        "low": 300, "high": 1500,
        "keywords": ["water heater", "hot water", "pilot light", "thermostat"]
    },
    IssueType.PIPING_REPAIR: {
        "low": 150, "high": 800,
        "keywords": ["pipe", "piping", "repiping", "copper", "pvc"]
    },
    IssueType.INSTALLATION: {
        "low": 150, "high": 600,
        "keywords": ["install", "faucet", "sink", "shower", "bathtub"]
    },
    IssueType.EMERGENCY: {
        "low": 200, "high": 1000,
        "keywords": ["emergency", "flooding", "urgent", "asap"]
    },
    IssueType.ELECTRICAL: {
        "low": 100, "high": 600,
        "keywords": ["electrical", "outlet", "breaker", "wiring", "spark"]
    },
    IssueType.HVAC: {
        "low": 150, "high": 800,
        "keywords": ["hvac", "ac", "heating", "furnace", "air conditioner"]
    },
    IssueType.GENERAL: {
        "low": 75, "high": 300,
        "keywords": ["repair", "fix", "broken", "maintenance"]
    },
}


class ServiceAgent(BaseAgent):
    """
    Agent for service business automation.

    Generic agent that can be configured for any service business:
    - Plumbing companies
    - HVAC services
    - Electrical contractors
    - General home services

    Capabilities:
    - Issue classification and quoting
    - Customer conversation management
    - Job scheduling
    - Price estimation
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("service", config)
        Config.ensure_directories()
        self.db_path = Config.DATA_DIR / "services.db"
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database for service business."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    issue_type TEXT NOT NULL,
                    description TEXT,
                    price_low REAL,
                    price_high REAL,
                    estimated_hours INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    phone TEXT NOT NULL,
                    issue_type TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def run(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute service business task.

        Args:
            task_input: Must contain 'action' key

        Returns:
            Standardized result
        """
        action = task_input.get("action")

        try:
            if action == "classify":
                return self._classify_issue(task_input)
            elif action == "quote":
                return self._generate_quote(task_input)
            elif action == "conversation":
                return self._handle_conversation(task_input)
            else:
                return self._format_error(
                    ValueError(f"Unknown action: {action}"),
                    "Supported actions: classify, quote, conversation"
                )
        except Exception as e:
            return self._format_error(e)

    def _classify_issue(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Classify a service issue from description."""
        description = task_input.get("description", "").lower()

        for issue_type, data in PRICE_TABLE.items():
            for keyword in data["keywords"]:
                if keyword in description:
                    return self._format_success({
                        "issue_type": issue_type.value,
                        "confidence": "keyword_match",
                        "price_range": {"low": data["low"], "high": data["high"]}
                    }, f"Classified as: {issue_type.value}")

        return self._format_success({
            "issue_type": IssueType.UNKNOWN.value,
            "confidence": "none",
            "price_range": None
        }, "Unable to classify - manual review needed")

    def _generate_quote(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a quote for a customer."""
        phone = task_input.get("phone", "")
        description = task_input.get("description", "")
        issue_type_str = task_input.get("issue_type", "")

        # Determine price range
        if issue_type_str:
            try:
                issue_type = IssueType(issue_type_str)
                pricing = PRICE_TABLE.get(issue_type, {})
            except ValueError:
                pricing = {}
        else:
            # Auto-classify
            classification = self._classify_issue({"description": description})
            issue_type_str = classification["data"]["issue_type"]
            pricing = classification["data"].get("price_range", {})

        quote = Quote(
            conversation_id=task_input.get("conversation_id", "unknown"),
            phone=phone,
            issue_type=issue_type_str,
            description=description,
            price_low=pricing.get("low", 100),
            price_high=pricing.get("high", 500),
            estimated_hours=task_input.get("estimated_hours", 2)
        )

        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO quotes
                (conversation_id, phone, issue_type, description, price_low, price_high, estimated_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (quote.conversation_id, quote.phone, quote.issue_type,
                  quote.description, quote.price_low, quote.price_high, quote.estimated_hours))

        return self._format_success({
            "quote": {
                "phone": quote.phone,
                "issue_type": quote.issue_type,
                "price_low": quote.price_low,
                "price_high": quote.price_high,
                "estimated_hours": quote.estimated_hours
            }
        }, "Quote generated successfully")

    def _handle_conversation(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer conversation."""
        phone = task_input.get("phone", "")
        message = task_input.get("message", "")

        # Classify the issue from message
        classification = self._classify_issue({"description": message})

        return self._format_success({
            "phone": phone,
            "classification": classification["data"],
            "next_steps": ["Generate quote", "Schedule appointment"]
        }, "Conversation processed")
