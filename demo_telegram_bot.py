#!/usr/bin/env python3
"""
Botwave Demo Telegram Bot
Showcase bot for potential clients - demonstrates AI automation capabilities.

This bot interacts with users to show what Botwave can do for their business.
"""

import os
import sys
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot state
user_sessions = {}


class DemoBot:
    """Demo bot that showcases Botwave capabilities."""

    def __init__(self):
        self.name = "Botwave Demo Assistant"
        self.version = "1.0"

    def get_welcome_message(self) -> str:
        return (
            "🤖 *Welcome to Botwave Demo!*\n\n"
            "I'm your AI automation assistant. I can show you what Botwave does for small businesses.\n\n"
            "*What I can demonstrate:*\n"
            "• 📞 Auto-respond to customer inquiries\n"
            "• 📅 Schedule appointments intelligently\n"
            "• 💰 Generate instant quotes\n"
            "• 📊 Track business metrics\n"
            "• 🔔 Send automated reminders\n\n"
            "Try one of these commands or just ask me something!"
        )

    def generate_quote(self, service: str, details: str = "") -> str:
        """Generate a sample quote like a real service business would."""
        quotes = {
            "plumbing": {
                "leak": {"labor": 2.5, "parts": 150, "description": "Leak detection and repair"},
                "clog": {"labor": 1.5, "parts": 75, "description": "Drain cleaning and clearing"},
                "heater": {"labor": 4.0, "parts": 850, "description": "Water heater service/repair"},
                "default": {"labor": 2.0, "parts": 100, "description": "General plumbing service"}
            },
            "hvac": {
                "ac": {"labor": 3.0, "parts": 400, "description": "AC repair/recharge"},
                "furnace": {"labor": 3.5, "parts": 500, "description": "Furnace inspection/repair"},
                "default": {"labor": 2.5, "parts": 250, "description": "HVAC service call"}
            },
            "electrical": {
                "outlet": {"labor": 1.0, "parts": 50, "description": "Outlet repair/replacement"},
                "panel": {"labor": 4.0, "parts": 600, "description": "Electrical panel service"},
                "lighting": {"labor": 2.0, "parts": 150, "description": "Lighting installation"},
                "default": {"labor": 2.0, "parts": 100, "description": "Electrical service call"}
            }
        }

        service_type = "plumbing"  # default
        for key in quotes.keys():
            if key in service.lower():
                service_type = key
                break

        job_type = "default"
        for key in quotes[service_type].keys():
            if key in details.lower():
                job_type = key
                break

        quote = quotes[service_type].get(job_type, quotes[service_type]["default"])
        labor_rate = 95  # per hour
        labor_cost = quote["labor"] * labor_rate
        parts_cost = quote["parts"]
        total = labor_cost + parts_cost

        return (
            f"📋 *Instant Quote Estimate*\n\n"
            f"*Service:* {quote['description']}\n"
            f"*Labor:* {quote['labor']} hrs × ${labor_rate}/hr = ${labor_cost:.2f}\n"
            f"*Parts/Materials:* ${parts_cost:.2f}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"*Estimated Total:* *${total:.2f}*\n\n"
            f"⏱️ Generated in 2 seconds by Botwave\n"
            f"_This is a demo. Actual quotes may vary._"
        )

    def schedule_demo(self) -> str:
        return (
            "📅 *Schedule a Live Demo*\n\n"
            "Want to see Botwave in action for YOUR business?\n\n"
            "Book a free 30-minute consultation:\n"
            "• 📧 Email: contact@botwave.io\n"
            "• 🌐 Web: github.com/LyferGang/Botwave\n\n"
            "We'll analyze your workflow and show you exactly how much time/money Botwave can save."
        )

    def show_roi(self) -> str:
        return (
            "💰 *Your Potential Savings*\n\n"
            "Based on typical small business (5-20 employees):\n\n"
            "📞 *Phone/Admin Time Saved:*\n"
            "   15 hrs/week × $50/hr × 52 weeks = *$39,000/year*\n\n"
            "📋 *Faster Quotes = More Jobs:*\n"
            "   3 extra jobs/month × $500 avg = *$18,000/year*\n\n"
            "🔄 *Follow-ups & Repeat Business:*\n"
            "   10% increase in repeat customers = *$15,000+/year*\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "*Total Annual Value: ~$72,000*\n\n"
            "Botwave Professional: $149/month = $1,788/year\n"
            "*ROI: 40x your investment*\n\n"
            "_Results vary by business. This is an estimate._"
        )

    def explain_features(self) -> str:
        return (
            "🛠️ *Botwave Features*\n\n"
            "*1. Customer Inquiry Bot*\n"
            "   - Answers questions 24/7 via SMS, email, web\n"
            "   - Never misses a call while you're on a job\n\n"
            "*2. Quote Generator*\n"
            "   - Instant professional quotes from photos/details\n"
            "   - Close more jobs by responding faster\n\n"
            "*3. Smart Scheduling*\n"
            "   - Auto-books appointments without conflicts\n"
            "   - Sends reminders, handles reschedules\n\n"
            "*4. Payment Processing*\n"
            "   - Send invoices, take deposits\n"
            "   - Integrated with your bank\n\n"
            "*5. Business Analytics*\n"
            "   - See profitable jobs, customer patterns\n"
            "   - Make data-driven decisions\n\n"
            "Ready to see it live? Use /demo"
        )


# Global demo bot instance
demo = DemoBot()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    logger.info(f"User {user.first_name} started the bot")

    await update.message.reply_text(
        demo.get_welcome_message(),
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = (
        "📖 *Botwave Demo Help*\n\n"
        "*Commands:*\n"
        "/start - Welcome message\n"
        "/quote - Generate a sample quote\n"
        "/schedule - Book a live demo\n"
        "/roi - See potential savings\n"
        "/features - Learn what Botwave does\n"
        "/demo - Start interactive demo\n\n"
        "*Or just ask me something!*\n"
        "Try: 'How much to fix a leak?'"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /quote command."""
    if context.args:
        service = " ".join(context.args)
        response = demo.generate_quote(service, service)
    else:
        # Show interactive options
        keyboard = [
            [InlineKeyboardButton("🔧 Plumbing", callback_data="quote_plumbing")],
            [InlineKeyboardButton("❄️ HVAC", callback_data="quote_hvac")],
            [InlineKeyboardButton("⚡ Electrical", callback_data="quote_electrical")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        response = "Select a service type for a sample quote:"
        await update.message.reply_text(response, reply_markup=reply_markup)
        return

    await update.message.reply_text(response, parse_mode='Markdown')


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /schedule command."""
    await update.message.reply_text(demo.schedule_demo(), parse_mode='Markdown')


async def roi_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /roi command."""
    await update.message.reply_text(demo.show_roi(), parse_mode='Markdown')


async def features_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /features command."""
    await update.message.reply_text(demo.explain_features(), parse_mode='Markdown')


async def demo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /demo command - start interactive demo."""
    keyboard = [
        [InlineKeyboardButton("📞 Customer Inquiry Demo", callback_data="demo_inquiry")],
        [InlineKeyboardButton("📋 Quick Quote Demo", callback_data="demo_quote")],
        [InlineKeyboardButton("📅 Scheduling Demo", callback_data="demo_schedule")],
        [InlineKeyboardButton("📊 Business Metrics Demo", callback_data="demo_metrics")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎯 *Interactive Demo*\n\n"
        "Choose what you'd like to see:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button callbacks."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("quote_"):
        service_type = data.replace("quote_", "")
        response = demo.generate_quote(service_type, "")
        await query.edit_message_text(response, parse_mode='Markdown')

    elif data == "demo_inquiry":
        response = (
            "📞 *Customer Inquiry Demo*\n\n"
            "Botwave can automatically respond to common questions:\n\n"
            "*Customer:* 'Are you open on weekends?'\n"
            "*Botwave:* 'Yes! We're available Saturday 8am-4pm. For emergencies, we have 24/7 service. Would you like to book an appointment?'\n\n"
            "*Customer:* 'How much for a drain cleaning?'\n"
            "*Botwave:* 'Drain cleaning starts at $149 for the first hour. Most jobs are completed within that time. Would you like me to schedule a technician?'\n\n"
            "This happens automatically - no human needed!"
        )
        await query.edit_message_text(response, parse_mode='Markdown')

    elif data == "demo_quote":
        response = (
            "📋 *Quick Quote Demo*\n\n"
            "1. Customer sends photo of the job\n"
            "2. Botwave analyzes the image\n"
            "3. Generates quote in seconds\n"
            "4. Sends professional PDF estimate\n\n"
            "*Result:*\n"
            "• Customer gets instant response\n"
            "• You win more jobs (speed matters!)\n"
            "• No time wasted on site visits for small jobs\n\n"
            "Try /quote to see it in action!"
        )
        await query.edit_message_text(response, parse_mode='Markdown')

    elif data == "demo_schedule":
        response = (
            "📅 *Scheduling Demo*\n\n"
            "Botwave manages your calendar intelligently:\n\n"
            "*Customer:* 'I need someone Tuesday morning'\n"
            "*Botwave checks calendar* → 'We have 9am or 11am available. Which works?'\n\n"
            "*Customer:* '9am works'\n"
            "*Botwave:* 'Booked! Technician will arrive between 8:45-9am. You'll get a reminder Monday evening.'\n\n"
            "*Behind the scenes:*\n"
            "✓ No double-booking\n"
            "✓ Automatic reminders sent\n"
            "✓ Calendar synced across team\n"
            "✓ Customer gets confirmation SMS/email"
        )
        await query.edit_message_text(response, parse_mode='Markdown')

    elif data == "demo_metrics":
        response = (
            "📊 *Business Metrics Demo*\n\n"
            "Botwave tracks what matters:\n\n"
            "*This Week's Dashboard:*\n"
            "• 47 inquiries handled automatically\n"
            "• 23 quotes generated (85% response rate)\n"
            "• 18 jobs booked from auto-quotes\n"
            "• $12,450 in new revenue\n"
            "• 14 hours saved on admin work\n\n"
            "*Top Services:*\n"
            "1. Drain cleaning (12 jobs)\n"
            "2. Water heater service (8 jobs)\n"
            "3. Leak repair (6 jobs)\n\n"
            "All visible in your web dashboard!"
        )
        await query.edit_message_text(response, parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular messages."""
    user_message = update.message.text.lower()
    logger.info(f"Message from {update.effective_user.first_name}: {user_message}")

    # Simple keyword-based responses to demo AI capabilities
    responses = {
        "leak": demo.generate_quote("plumbing", "leak"),
        "clog": demo.generate_quote("plumbing", "clog"),
        "drain": demo.generate_quote("plumbing", "clog"),
        "water heater": demo.generate_quote("plumbing", "heater"),
        "ac": demo.generate_quote("hvac", "ac"),
        "air conditioning": demo.generate_quote("hvac", "ac"),
        "furnace": demo.generate_quote("hvac", "furnace"),
        "electric": demo.generate_quote("electrical", ""),
        "electrical": demo.generate_quote("electrical", ""),
        "outlet": demo.generate_quote("electrical", "outlet"),
        "price": "I can generate a quote for you! Tell me what service you need (plumbing, HVAC, electrical) and what the issue is.",
        "cost": "I can generate a quote for you! Tell me what service you need (plumbing, HVAC, electrical) and what the issue is.",
        "quote": "I can generate a quote for you! Tell me what service you need (plumbing, HVAC, electrical) and what the issue is.",
        "schedule": demo.schedule_demo(),
        "book": demo.schedule_demo(),
        "appointment": demo.schedule_demo(),
        "demo": "Use /demo to start the interactive demo, or /schedule to book a live consultation!",
        "roi": demo.show_roi(),
        "savings": demo.show_roi(),
        "money": demo.show_roi(),
        "features": demo.explain_features(),
        "what can you do": demo.explain_features(),
        "help": "Try /help to see all commands, or ask me about pricing, scheduling, or our services!"
    }

    response = None
    for keyword, reply in responses.items():
        if keyword in user_message:
            response = reply
            break

    if not response:
        response = (
            "Thanks for your message! I'm the Botwave demo assistant.\n\n"
            "I can help you:\n"
            "• Generate quotes (tell me the service)\n"
            "• Show you potential savings (/roi)\n"
            "• Explain features (/features)\n"
            "• Book a live demo (/schedule)\n\n"
            "What would you like to know?"
        )

    await update.message.reply_text(response, parse_mode='Markdown' if '*' in response else None)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error: {context.error}")


def main() -> None:
    """Start the bot."""
    # Get token from environment or use demo token
    token = os.getenv("TG_DEMO_BOT_TOKEN")

    if not token or token == "your_demo_bot_token_here":
        print("=" * 60)
        print("🤖 Botwave Demo Telegram Bot")
        print("=" * 60)
        print("\nTo run this demo bot:")
        print("1. Create a bot via @BotFather on Telegram")
        print("2. Get your token from BotFather")
        print("3. Set env var: export TG_DEMO_BOT_TOKEN='your-token'")
        print("4. Run: python demo_telegram_bot.py")
        print("\nOr add token to .env as TG_DEMO_BOT_TOKEN")
        print("=" * 60)
        return

    # Build application
    app = Application.builder().token(token).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("quote", quote_command))
    app.add_handler(CommandHandler("schedule", schedule_command))
    app.add_handler(CommandHandler("roi", roi_command))
    app.add_handler(CommandHandler("features", features_command))
    app.add_handler(CommandHandler("demo", demo_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Add error handler
    app.add_error_handler(error_handler)

    # Start the bot
    logger.info("Starting Botwave Demo Bot...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
