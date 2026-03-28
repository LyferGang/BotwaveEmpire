#!/usr/bin/env python3
"""
Plumbing Agent - Standalone Implementation

Handles plumbing issue classification, quote generation, and conversation management.
Uses local LLM (LM Studio/Ollama) for classification and SQLite for persistence.
"""

import os
import json
import sqlite3
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class IssueType(Enum):
    """Classification of plumbing issues for pricing."""
    LEAK = "leak"
    CLOGGED_DRAIN = "clogged_drain"
    TOILET_ISSUE = "toilet_issue"
    WATER_HEATER = "water_heater"
    PIPING_REPAIR = "piping_repair"
    INSTALLATION = "installation"
    EMERGENCY = "emergency"
    UNKNOWN = "unknown"


@dataclass
class Quote:
    """Generated quote for a plumbing issue."""
    conversation_id: str
    phone: str
    issue_type: str
    description: str
    price_low: float
    price_high: float
    estimated_hours: int
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# PRICE KNOWLEDGE BASE
# ============================================================================

PRICE_TABLE = {
    IssueType.LEAK: {"low": 100, "high": 500, "keywords": ["leak", "leaking", "dripping", "burst", "water everywhere"]},
    IssueType.CLOGGED_DRAIN: {"low": 75, "high": 250, "keywords": ["clog", "drain", "slow drain", "backed up", "gurgling"]},
    IssueType.TOILET_ISSUE: {"low": 150, "high": 450, "keywords": ["toilet", "running toilet", "not flushing", "flapper", "fill valve"]},
    IssueType.WATER_HEATER: {"low": 300, "high": 1500, "keywords": ["water heater", "hot water", "no hot water", "pilot light", "thermostat"]},
    IssueType.PIPING_REPAIR: {"low": 150, "high": 800, "keywords": ["pipe", "piping", "repiping", "copper", "pvc", "cpvc", "poly"]},
    IssueType.INSTALLATION: {"low": 150, "high": 600, "keywords": ["install", "faucet", "sink", "shower", "bathtub", "garbage disposal"]},
    IssueType.WATER_HEATER: {"low": 500, "high": 2000, "keywords": ["main line", "sewer line", "main sewer"]},
}

CLARIFYING_QUESTIONS = {
    IssueType.LEAK: [
        "Where is the leak located? (under sink, ceiling, wall, floor)",
        "Is it a slow drip or active flowing?",
        "Do you know what type of pipe is leaking?"
    ],
    IssueType.CLOGGED_DRAIN: [
        "Which drain is clogged? (kitchen sink, bathroom sink, shower, tub, toilet)",
        "Is water backing up or just draining slowly?",
        "Have you tried anything to clear it already?"
    ],
    IssueType.TOILET_ISSUE: [
        "Is the toilet running constantly or not flushing?",
        "Do you hear any unusual noises?",
        "Is there water on the floor around the toilet?"
    ],
    IssueType.WATER_HEATER: [
        "Is it gas or electric?",
        "No hot water at all or just not hot enough?",
        "How old is the water heater?"
    ],
    IssueType.PIPING_REPAIR: [
        "Where is the pipe located? (accessible or behind wall/floor)",
        "What material is the pipe? (copper, pvc, cpvc, poly)",
        "Is there active leaking or just need repair/replacement?"
    ],
    IssueType.INSTALLATION: [
        "What fixture needs to be installed?",
        "Do you have the fixture already or need me to supply it?",
        "Is this a new install or replacement?"
    ],
}


# ============================================================================
# LLM CLIENT FOR LM STUDIO
# ============================================================================

class LocalLLMClient:
    """Client for local LLM models via LM Studio OpenAI-compatible API."""

    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or os.getenv("LLM_URL", "http://127.0.0.1:1234/v1")
        self.model = model or os.getenv("LLM_MODEL", "qwen3.5-9b-claude-4.6-opus-uncensored-distilled")
        self.timeout = int(os.getenv("LLM_TIMEOUT", "30"))
        self.api_key = os.getenv("LLM_API_KEY", "not-needed")

    def classify_issue(self, user_message: str, context: str = "") -> Tuple[IssueType, float, str]:
        """
        Use LLM to classify the plumbing issue.

        Returns: (issue_type, confidence, reasoning)
        """
        prompt = f"""You are a plumbing issue classifier. Analyze this customer message and classify the issue.

Customer message: "{user_message}"
{context if context else ""}

Available issue types:
- leak: leaking water, dripping, burst pipes
- clogged_drain: slow drain, clog, backed up
- toilet_issue: running toilet, not flushing, toilet problems
- water_heater: no hot water, water heater issues
- piping_repair: pipe repair, repiping, pipe replacement
- installation: installing fixtures, faucet install, disposal install

Return ONLY a JSON object with this format:
{{
    "issue_type": "<one of the types above>",
    "confidence": <0.0 to 1.0>,
    "reasoning": "<brief explanation>"
}}

Do not include any other text. Just the JSON."""

        try:
            resp = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 300
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout
            )
            print(f"LLM response status: {resp.status_code}")
            resp.raise_for_status()
            data = resp.json()
            msg = data["choices"][0]["message"]
            content = msg.get("content", "") or msg.get("reasoning_content", "")
            print(f"LLM content: {content[:200]}...")

            # Try to extract JSON from content
            import re
            json_match = re.search(r'\{[^}]*"issue_type"[^}]*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                content = content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                content = content.strip()
                result = json.loads(content)

            issue_type = IssueType[result["issue_type"].upper()]
            return issue_type, float(result["confidence"]), result.get("reasoning", "")

        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            print(f"LLM classification failed: {e}")
            return self._keyword_classify(user_message)

    def _keyword_classify(self, text: str) -> Tuple[IssueType, float, str]:
        """Fallback keyword-based classification."""
        text_lower = text.lower()

        for issue_type, config in PRICE_TABLE.items():
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    return issue_type, 0.7, f"Matched keyword: {keyword}"

        return IssueType.UNKNOWN, 0.5, "No clear keywords matched"

    def generate_response(self, issue_type: IssueType, context: Dict[str, Any]) -> str:
        """Generate a conversational response."""
        questions = CLARIFYING_QUESTIONS.get(issue_type, ["Can you tell me more about the issue?"])
        question = questions[context.get("question_index", 0)]

        tone = "Got it — " if context.get("previous_messages", 0) > 0 else "Hey — "
        return f"{tone}{question}"


# ============================================================================
# SQLITE STORAGE LAYER
# ============================================================================

class PlumbingDB:
    """SQLite storage for quotes."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv("PLUMBING_DB_PATH", "./plumbing_quotes.db")

    def init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                phone TEXT,
                issue_type TEXT,
                description TEXT,
                price_low REAL,
                price_high REAL,
                estimated_hours INTEGER,
                status TEXT,
                created_at TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE,
                last_message TEXT,
                issue_type TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')

        conn.commit()
        conn.close()
        print(f"Database initialized at {self.db_path}")

    def save_quote(self, quote: Quote) -> int:
        """Save a quote and return its ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO quotes (conversation_id, phone, issue_type, description,
                               price_low, price_high, estimated_hours, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (quote.conversation_id, quote.phone, quote.issue_type, quote.description,
              quote.price_low, quote.price_high, quote.estimated_hours, quote.status, quote.created_at))

        quote_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return quote_id

    def get_quote(self, quote_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a quote by ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM quotes WHERE id = ?', (quote_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None


# ============================================================================
# PRICING ENGINE
# ============================================================================

class PricingEngine:
    """Calculate quotes based on issue type."""

    def calculate_quote(self, issue_type: IssueType, description: str) -> Tuple[int, int, int]:
        """
        Calculate price range for an issue.

        Returns: (price_low, price_high, estimated_hours)
        """
        if issue_type not in PRICE_TABLE:
            return 100, 300, 2  # Default fallback

        config = PRICE_TABLE[issue_type]
        base_low = config["low"]
        base_high = config["high"]

        # Adjust based on description complexity
        desc_lower = description.lower()
        if any(w in desc_lower for w in ["emergency", "urgent", "right now", "ASAP"]):
            base_low = int(base_low * 1.3)
            base_high = int(base_high * 1.3)

        hours_map = {
            "leak": 2,
            "clogged_drain": 1,
            "toilet": 2,
            "water_heater": 3,
            "piping": 4,
            "installation": 2,
        }

        hours = hours_map.get(issue_type.value.split("_")[0], 2)

        return base_low, base_high, hours


# ============================================================================
# MAIN PLUMBING AGENT
# ============================================================================

class PlumbingAgent:
    """Main Plumbing Agent that orchestrates all components."""

    def __init__(self):
        self.llm_client = LocalLLMClient()
        self.db = PlumbingDB()
        self.pricing = PricingEngine()
        self.conversations: Dict[str, Dict[str, Any]] = {}

    def initialize(self):
        """Initialize the agent."""
        print("Initializing Plumbing Agent...")
        self.db.init_db()
        print("Plumbing Agent ready!\n")

    def handle_message(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Handle an incoming message and return a response.

        Args:
            phone: Customer phone number (Telegram/WhatsApp ID)
            message: The customer's message text

        Returns:
            Response dict with status, response text, and optional quote
        """
        # Get or create conversation context
        conv_id = f"conv_{phone}_{datetime.now().timestamp()}"

        if phone not in self.conversations:
            self.conversations[phone] = {
                "conversation_id": conv_id,
                "phone": phone,
                "messages": [],
                "issue_classified": False,
                "quote_generated": False
            }

        conv = self.conversations[phone]
        conv["messages"].append({"role": "user", "content": message})

        # Classify the issue
        if not conv["issue_classified"]:
            issue_type, confidence, reasoning = self.llm_client.classify_issue(message)
            conv["issue_type"] = issue_type
            conv["issue_classified"] = True
            conv["confidence"] = confidence
            conv["reasoning"] = reasoning

            # Generate clarifying question
            questions = CLARIFYING_QUESTIONS.get(issue_type, ["Can you tell me more?"])
            response_text = f"Got it — {questions[0]}"

            return {
                "status": "clarification_needed",
                "response": response_text,
                "issue_type": issue_type.value,
                "confidence": confidence,
                "conversation_id": conv_id
            }

        # Check if user is confirming booking
        if message.upper() in ["YES", "BOOK IT", "LET'S DO IT"]:
            quote = self._generate_quote(phone, message, conv)
            quote_id = self.db.save_quote(quote)

            return {
                "status": "booked",
                "response": f"Awesome, you're booked! Quote #{quote_id}. I'll send you a time confirmation soon.",
                "quote_id": quote_id,
                "conversation_id": conv_id
            }

        # Generate quote if we have enough info
        if not conv["quote_generated"]:
            quote = self._generate_quote(phone, message, conv)
            quote_id = self.db.save_quote(quote)
            conv["quote_generated"] = True
            conv["quote"] = quote

            return {
                "status": "quoted",
                "response": f"Here's your estimate for {quote.issue_type.replace('_', ' ')}: ${quote.price_low} - ${quote.price_high}. Reply YES to book.",
                "quote_id": quote_id,
                "price_range": f"${quote.price_low} - ${quote.price_high}",
                "conversation_id": conv_id
            }

        # Default response
        return {
            "status": "ack",
            "response": "Got your message. What would you like to do next?",
            "conversation_id": conv_id
        }

    def _generate_quote(self, phone: str, message: str, conv: Dict) -> Quote:
        """Generate a quote for the customer."""
        issue_type = conv.get("issue_type", IssueType.UNKNOWN)
        description = conv.get("messages", [{"content": message}])[-1]["content"]

        price_low, price_high, hours = self.pricing.calculate_quote(issue_type, description)

        return Quote(
            conversation_id=conv["conversation_id"],
            phone=phone,
            issue_type=issue_type.value,
            description=description,
            price_low=price_low,
            price_high=price_high,
            estimated_hours=hours
        )


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Plumbing Agent CLI")
    parser.add_argument("--mode", choices=["test", "interactive"], default="test",
                        help="Run mode: test (single message) or interactive (chat loop)")
    parser.add_argument("--phone", default="+1234567890", help="Phone/contact ID")
    parser.add_argument("--message", "-m", help="Message to process (test mode)")

    args = parser.parse_args()

    # Initialize agent
    agent = PlumbingAgent()
    agent.initialize()

    if args.mode == "test":
        if not args.message:
            print("Error: --message required in test mode")
            return

        result = agent.handle_message(args.phone, args.message)
        print("\n=== Result ===")
        print(json.dumps(result, indent=2))

    elif args.mode == "interactive":
        print("\n=== Interactive Mode ===")
        print("Type messages to chat. Type 'quit' to exit.\n")

        phone = args.phone
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ["quit", "exit"]:
                    break

                result = agent.handle_message(phone, user_input)
                print(f"Agent: {result['response']}")
                print(f"Status: {result['status']}\n")

            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    main()
