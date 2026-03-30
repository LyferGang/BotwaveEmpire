#!/usr/bin/env python3
"""
BOTWAVE PUBLIC DEMO BOT - "Captain Obvious"
Open to anyone - showcases Botwave capabilities

Bot Token: 8249528887:AAGjc386QGaG_-TJLkj3WOS03CYMqF0LOsc
Owner: Al Gringo (8711428786)

This bot is PUBLIC - anyone can message it to see what Botwave can do.
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
import requests
import sqlite3
from datetime import datetime
from pathlib import Path

# Configuration
BOT_TOKEN = "8249528887:AAGjc386QGaG_-TJLkj3WOS03CYMqF0LOsc"
OWNER_ID = 8711428786
LM_STUDIO_URL = "http://localhost:1234/v1"
LM_STUDIO_MODEL = "llama-3.1-8b-instruct-abliterated-obliteratus"

# Database
DB_PATH = Path(__file__).parent / "data" / "demo_bot.db"

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class PublicDemoBot:
    """Public demo bot showcasing Botwave capabilities."""

    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for demo leads."""
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS demo_leads (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                username TEXT,
                interest TEXT,
                message TEXT,
                contacted BOOLEAN DEFAULT FALSE,
                converted BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                action TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Demo bot database initialized")

    def setup_handlers(self):
        """Setup bot handlers."""
        # Commands
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("demo", self.demo_menu))
        self.app.add_handler(CommandHandler("features", self.show_features))
        self.app.add_handler(CommandHandler("pricing", self.show_pricing))
        self.app.add_handler(CommandHandler("contact", self.show_contact))
        self.app.add_handler(CommandHandler("getbot", self.get_bot_info))

        # Callbacks
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))

        # Messages
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message - WOW factor."""
        welcome = """
🤖 *Welcome to Botwave Empire!*

I'm *Captain Obvious*, your AI demo bot.

I can show you what Botwave can do for YOUR business:

✅ AI customer service (like me!)
✅ Lead capture & follow-up
✅ Payment processing
✅ Appointment scheduling
✅ Multi-agent automation
✅ Analytics & reporting

*Want a bot like this for YOUR business?*

Tap below to explore! 👇
"""
        keyboard = [
            [InlineKeyboardButton("🎯 SEE FEATURES", callback_data="features")],
            [InlineKeyboardButton("💰 VIEW PRICING", callback_data="pricing")],
            [InlineKeyboardButton("🤖 TRY DEMO", callback_data="demo")],
            [InlineKeyboardButton("📞 GET YOUR BOT", callback_data="getbot")],
            [InlineKeyboardButton("💬 CHAT WITH AI", callback_data="chat_demo")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome, reply_markup=reply_markup, parse_mode="Markdown")
        self.log_interaction(update.effective_user.id, "start")

        # Notify owner of new visitor
        await self.notify_owner(f"👋 New visitor: @{update.effective_user.username or update.effective_user.id}")

    async def demo_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show interactive demo."""
        text = """
🎯 *Interactive Demo*

See Botwave in action! Choose a demo:

*Real Business Scenarios:*
• 🛠️ Plumbing service booking
• 🏥 Medical appointment scheduling
• 🛒 E-commerce order tracking
• 🍕 Restaurant ordering
• 📊 Business analytics

Which would you like to see?
"""
        keyboard = [
            [InlineKeyboardButton("🛠️ PLUMBING DEMO", callback_data="demo_plumbing")],
            [InlineKeyboardButton("🏥 MEDICAL DEMO", callback_data="demo_medical")],
            [InlineKeyboardButton("🛒 E-COMMERCE DEMO", callback_data="demo_ecommerce")],
            [InlineKeyboardButton("🍕 RESTAURANT DEMO", callback_data="demo_restaurant")],
            [InlineKeyboardButton("⬅️ BACK", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def show_features(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all features."""
        text = """
✨ *Botwave Features*

*🤖 AI Capabilities:*
• Natural language conversations
• Multi-language support
• Voice message transcription
• Image analysis (OCR, estimates)
• Sentiment analysis
• Smart human handoff

*💼 Business Tools:*
• Lead capture & CRM
• Stripe payment integration
• Appointment scheduling
• Automated follow-ups
• Broadcast messaging
• Analytics dashboard

*🔧 Technical:*
• Local LLM (your data stays private)
• Custom knowledge base (RAG)
• Webhook integrations
• Multi-bot coordination
• 24/7 uptime

Want to see it in action? Try the demo!
"""
        keyboard = [
            [InlineKeyboardButton("🎯 TRY DEMO", callback_data="demo")],
            [InlineKeyboardButton("💰 SEE PRICING", callback_data="pricing")],
            [InlineKeyboardButton("⬅️ BACK", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def show_pricing(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show pricing tiers."""
        text = """
💰 *Botwave Pricing*

*Starter - $299/mo*
• AI Chat Agent (Telegram)
• Basic Lead Capture
• Automated Quotes
• Monthly Reports
• Email Support

*Professional - $499/mo* ⭐ MOST POPULAR
• Everything in Starter
• Multi-Agent System
• Customer Portal
• PDF Reports
• Priority Support
• Custom Integrations

*Enterprise - $1,499/mo*
• Everything in Professional
• Unlimited Agents
• White-Label Option
• Custom AI Training
• Dedicated Support
• SLA Guarantee

*14-day FREE trial - No credit card required!*
"""
        keyboard = [
            [InlineKeyboardButton("🚀 START FREE TRIAL", callback_data="trial")],
            [InlineKeyboardButton("📞 TALK TO SALES", callback_data="sales")],
            [InlineKeyboardButton("⬅️ BACK", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def get_bot_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Info for getting your own bot."""
        text = """
🤖 *Get Your Own Botwave Bot!*

Ready to automate YOUR business?

*Here's what you get:*

✅ Custom Telegram bot (like me!)
✅ AI trained on YOUR business
✅ Lead capture & follow-up
✅ Payment processing
✅ Appointment booking
✅ 24/7 customer service
✅ Analytics dashboard

*Setup includes:*
• Bot configuration
• AI knowledge base setup
• Stripe integration
• CRM integration
• Training & onboarding

*Want to get started?*

Click below or message @AlGringo directly!
"""
        keyboard = [
            [InlineKeyboardButton("📞 CONTACT SALES", url="https://t.me/AlGringo")],
            [InlineKeyboardButton("🚀 START TRIAL", callback_data="trial")],
            [InlineKeyboardButton("⬅️ BACK", callback_data="back_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks."""
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == "features":
            await self.show_features(update, context)
        elif data == "pricing":
            await self.show_pricing(update, context)
        elif data == "demo":
            await self.demo_menu(update, context)
        elif data == "getbot":
            await self.get_bot_info(update, context)
        elif data == "chat_demo":
            await query.edit_message_text(
                "💬 *AI Chat Demo*\n\nAsk me anything about Botwave or test my AI capabilities!\n\nType your message below:",
                parse_mode="Markdown"
            )
        elif data.startswith("demo_"):
            await self.run_demo_scenario(query, data.split("_")[1])
        elif data == "trial":
            await query.edit_message_text(
                "🚀 *Start Your Free Trial!*\n\nMessage @AlGringo to get started.\n\nTell him:\n• Your business type\n• What you want to automate\n• Any specific needs\n\nHe'll set you up within 24 hours!"
            )
        elif data == "sales":
            await query.edit_message_text(
                "📞 *Talk to Sales*\n\nMessage @AlGringo directly for a personalized demo and pricing discussion."
            )
        elif data == "back_main":
            await self.start(update, context)

    async def run_demo_scenario(self, query, scenario):
        """Run an interactive demo scenario."""
        demos = {
            "plumbing": (
                "🛠️ *Plumbing Demo*\n\n*Customer:* 'My sink is clogged!'\n\n*Bot Response:*",
                "I understand you have a clogged sink! Let me help.\n\n🔧 Quick questions:\n1. Kitchen or bathroom?\n2. Completely blocked or slow drain?\n3. Any water backing up?\n\nI can book a technician or give you a quote!"
            ),
            "medical": (
                "🏥 *Medical Demo*\n\n*Patient:* 'I need to see a doctor'\n\n*Bot Response:*",
                "I can help you schedule an appointment!\n\n📅 Available today:\n• Dr. Smith - 2:00 PM\n• Dr. Jones - 3:30 PM\n• Dr. Lee - 4:45 PM\n\nWhich works for you? Or I can find another time."
            ),
            "ecommerce": (
                "🛒 *E-commerce Demo*\n\n*Customer:* 'Where is my order?'\n\n*Bot Response:*",
                "Let me check your order status!\n\n📦 Please provide:\n• Order number, or\n• Email used for order\n\nI'll track it and give you an update!"
            ),
            "restaurant": (
                "🍕 *Restaurant Demo*\n\n*Customer:* 'I want to order pizza'\n\n*Bot Response:*",
                "🍕 Great choice! What would you like?\n\n1. Pepperoni - $14.99\n2. Margherita - $12.99\n3. Supreme - $16.99\n4. Build your own\n\nType your order!"
            )
        }

        if scenario in demos:
            intro, response = demos[scenario]
            text = f"{intro}\n\n_{response}_\n\n*(This is automated AI response)*"
            await query.edit_message_text(text, parse_mode="Markdown")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages with AI."""
        user_text = update.message.text

        # Get AI response
        ai_response = self.get_ai_response(user_text)

        await update.message.reply_text(ai_response)
        self.log_interaction(update.effective_user.id, f"text: {user_text[:50]}")

    def get_ai_response(self, user_text: str) -> str:
        """Get AI response from local LM Studio."""
        try:
            resp = requests.post(
                f"{LM_STUDIO_URL}/chat/completions",
                json={
                    "model": LM_STUDIO_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are Captain Obvious, a friendly demo bot for Botwave Empire. You showcase AI capabilities to potential customers. Be engaging, informative, and helpful. When someone asks about getting a bot, direct them to @AlGringo."},
                        {"role": "user", "content": user_text}
                    ]
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except:
            pass
        return "Hmm, I'm having trouble thinking right now. Message @AlGringo for help!"

    async def notify_owner(self, message: str):
        """Send notification to owner."""
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": OWNER_ID, "text": message})
        except:
            pass

    def log_interaction(self, user_id: int, action: str):
        """Log interaction to database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            interaction_id = f"int_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            cursor.execute(
                "INSERT INTO interactions (id, user_id, action) VALUES (?, ?, ?)",
                (interaction_id, user_id, action[:200])
            )
            conn.commit()
            conn.close()
        except:
            pass

    def run(self):
        """Start the bot."""
        logger.info("Starting Public Demo Bot (Captain Obvious)...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = PublicDemoBot()
    bot.run()
