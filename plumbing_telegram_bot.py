#!/usr/bin/env python3
"""
Jimenez Plumbing - Telegram Customer Bot
Handles customer inquiries, quotes, and scheduling via Telegram.

Setup:
1. Add your bot token to .env as TG_PLUMBING_BOT_TOKEN
2. Run: python plumbing_telegram_bot.py
3. Share bot link with customers: t.me/YourBotName
"""

import os
import sys
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters, ConversationHandler
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('plumbing_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path("data/plumbing_customers.db")
DB_PATH.parent.mkdir(exist_ok=True)

# Conversation states
SELECTING_SERVICE, SELECTING_ISSUE, CONFIRMING_QUOTE, SCHEDULING = range(4)

# =============================================================================
# PRICING DATABASE
# =============================================================================

PLUMBING_SERVICES = {
    "drain_cleaning": {
        "name": "Drain Cleaning",
        "base_price": 149,
        "hours": 1,
        "keywords": ["clog", "drain", "slow", "backed up", "sink", "shower", "toilet"],
        "description": "Professional drain cleaning service"
    },
    "leak_repair": {
        "name": "Leak Repair",
        "base_price": 195,
        "hours": 2,
        "keywords": ["leak", "leaking", "drip", "dripping", "burst", "flood"],
        "description": "Leak detection and repair"
    },
    "water_heater": {
        "name": "Water Heater Service",
        "base_price": 295,
        "hours": 2,
        "keywords": ["water heater", "hot water", "no hot water", "pilot", "thermostat"],
        "description": "Water heater repair or replacement"
    },
    "toilet_repair": {
        "name": "Toilet Repair",
        "base_price": 175,
        "hours": 1,
        "keywords": ["toilet", "running", "not flushing", "broken toilet", "wobbly"],
        "description": "Toilet repair or replacement"
    },
    "faucet_repair": {
        "name": "Faucet Repair",
        "base_price": 125,
        "hours": 1,
        "keywords": ["faucet", "sink leak", "kitchen faucet", "bathroom faucet"],
        "description": "Faucet repair or replacement"
    },
    "pipe_repair": {
        "name": "Pipe Repair",
        "base_price": 250,
        "hours": 3,
        "keywords": ["pipe", "piping", "repiping", "copper pipe", "pvc pipe"],
        "description": "Pipe repair or replacement"
    },
    "emergency": {
        "name": "Emergency Service",
        "base_price": 350,
        "hours": 2,
        "keywords": ["emergency", "urgent", "asap", "now", "flooding"],
        "description": "24/7 Emergency plumbing service"
    },
    "inspection": {
        "name": "Plumbing Inspection",
        "base_price": 99,
        "hours": 1,
        "keywords": ["inspection", "check", "estimate", "quote"],
        "description": "Full plumbing system inspection"
    }
}

LABOR_RATE = 95  # per hour


# =============================================================================
# DATABASE FUNCTIONS
# =============================================================================

def init_database():
    """Initialize SQLite database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT UNIQUE,
                phone TEXT,
                name TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT,
                customer_name TEXT,
                phone TEXT,
                service_type TEXT,
                description TEXT,
                price_low REAL,
                price_high REAL,
                estimated_hours INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT,
                customer_name TEXT,
                phone TEXT,
                service_type TEXT,
                scheduled_date TEXT,
                scheduled_time TEXT,
                status TEXT DEFAULT 'scheduled',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    logger.info("Database initialized")


def save_customer(telegram_id: str, phone: str = "", name: str = "", address: str = ""):
    """Save or update customer info."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO customers (telegram_id, phone, name, address)
            VALUES (?, ?, ?, ?)
        """, (telegram_id, phone, name, address))


def save_quote(telegram_id: str, customer_name: str, phone: str, service_type: str,
               description: str, price_low: float, price_high: float, hours: int):
    """Save a generated quote."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO quotes (telegram_id, customer_name, phone, service_type,
                              description, price_low, price_high, estimated_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (telegram_id, customer_name, phone, service_type, description,
              price_low, price_high, hours))


def save_appointment(telegram_id: str, customer_name: str, phone: str,
                     service_type: str, date: str, time: str, notes: str = ""):
    """Save a scheduled appointment."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO appointments (telegram_id, customer_name, phone,
                                     service_type, scheduled_date, scheduled_time, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (telegram_id, customer_name, phone, service_type, date, time, notes))


# =============================================================================
# BOT RESPONSES
# =============================================================================

WELCOME_MESSAGE = """
🔧 *Jimenez Plumbing - Automatic Assistant*

I can help you with:
• 📋 Instant price quotes
• 📅 Schedule service appointments
• 🚨 Emergency service info
• 💬 Talk to a plumber

*What service do you need?*
"""

EMERGENCY_MESSAGE = """
🚨 *EMERGENCY PLUMBING SERVICE*

For urgent plumbing emergencies:
• Major flooding/burst pipes
• Sewage backup
• No water to entire house
• Gas line issues

📞 *Call directly:* (555) 123-4567

Emergency service available 24/7
Response time: Under 2 hours
"""


def classify_service(message: str) -> str:
    """Classify service type from customer message."""
    message_lower = message.lower()

    for service_key, service_data in PLUMBING_SERVICES.items():
        for keyword in service_data["keywords"]:
            if keyword in message_lower:
                return service_key

    return "inspection"  # default


def generate_quote_text(service_key: str, description: str = "") -> str:
    """Generate a formatted quote message."""
    service = PLUMBING_SERVICES.get(service_key, PLUMBING_SERVICES["inspection"])

    labor_cost = service["hours"] * LABOR_RATE
    total_low = service["base_price"]
    total_high = int(service["base_price"] * 1.5)  # 50% buffer

    return f"""
📋 *PLUMBING QUOTE ESTIMATE*
━━━━━━━━━━━━━━━━━━━━━━

*Service:* {service['name']}
{service['description']}

*Estimated Labor:* {service['hours']} hour(s)
*Labor Rate:* ${LABOR_RATE}/hr

*Price Range:*
├ Min: ${total_low:,}
└ Max: ${total_high:,}

*Description:* {description or 'Standard service'}

━━━━━━━━━━━━━━━━━━━━━━
⏱️ This is an estimate. Final price may vary based on actual work required.

*Would you like to:*
1️⃣ Book this service
2️⃣ Get another quote
3️⃣ Speak with a plumber
"""


def get_available_slots() -> list:
    """Generate available time slots for next 3 business days."""
    slots = []
    today = datetime.now()

    for day_offset in range(1, 5):  # Next 4 days
        date = today + timedelta(days=day_offset)
        day_name = date.strftime("%A, %b %d")

        # Business hours: 7am - 6pm
        times = ["7:00 AM", "9:00 AM", "11:00 AM", "1:00 PM", "3:00 PM", "5:00 PM"]

        slots.append({
            "date": date.strftime("%Y-%m-%d"),
            "day_name": day_name,
            "times": times
        })

    return slots


# =============================================================================
# CONVERSATION HANDLERS
# =============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command."""
    user = update.effective_user
    logger.info(f"Customer {user.first_name} started conversation")

    # Save customer
    save_customer(str(user.id))

    # Create service selection keyboard
    keyboard = []
    for key, service in PLUMBING_SERVICES.items():
        keyboard.append([InlineKeyboardButton(
            service["name"],
            callback_data=f"service_{key}"
        )])

    keyboard.append([InlineKeyboardButton("🚨 Emergency", callback_data="service_emergency")])
    keyboard.append([InlineKeyboardButton("📞 Call Now", callback_data="call_now")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

    return SELECTING_SERVICE


async def service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle service selection."""
    query = update.callback_query
    await query.answer()

    service_key = query.data.replace("service_", "")
    context.user_data['selected_service'] = service_key

    if service_key == "emergency":
        await query.edit_message_text(EMERGENCY_MESSAGE, parse_mode='Markdown')
        return SELECTING_SERVICE

    if service_key == "call_now":
        await query.edit_message_text(
            "📞 *Call Jimenez Plumbing*\n\n"
            "📱 (555) 123-4567\n\n"
            "Business Hours: Mon-Sat 7am-6pm",
            parse_mode='Markdown'
        )
        return SELECTING_SERVICE

    service = PLUMBING_SERVICES.get(service_key, PLUMBING_SERVICES["inspection"])

    await query.edit_message_text(
        f"🔧 *{service['name']}*\n\n"
        f"{service['description']}\n\n"
        f"*Please describe your issue:*\n"
        f"(e.g., 'Kitchen sink is clogged' or 'Water heater not getting hot')",
        parse_mode='Markdown'
    )

    return SELECTING_ISSUE


async def issue_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle issue description and generate quote."""
    description = update.message.text
    service_key = context.user_data.get('selected_service', 'inspection')

    # Generate and show quote
    quote_text = generate_quote_text(service_key, description)

    # Save quote to database
    user = update.effective_user
    save_quote(
        telegram_id=str(user.id),
        customer_name=user.first_name,
        phone=user.username or "",
        service_type=service_key,
        description=description,
        price_low=PLUMBING_SERVICES[service_key]["base_price"],
        price_high=int(PLUMBING_SERVICES[service_key]["base_price"] * 1.5),
        hours=PLUMBING_SERVICES[service_key]["hours"]
    )

    # Booking keyboard
    keyboard = [
        [InlineKeyboardButton("📅 Book Appointment", callback_data="book_now")],
        [InlineKeyboardButton("📞 Call to Schedule", callback_data="call_now")],
        [InlineKeyboardButton("🔄 New Quote", callback_data="new_quote")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(quote_text, reply_markup=reply_markup, parse_mode='Markdown')

    return CONFIRMING_QUOTE


async def quote_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle quote-related button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == "book_now":
        # Show available slots
        slots = get_available_slots()
        keyboard = []
        for slot in slots:
            keyboard.append([InlineKeyboardButton(
                slot["day_name"],
                callback_data=f"date_{slot['date']}"
            )])
        keyboard.append([InlineKeyboardButton("« Back", callback_data="back_to_quote")])

        await query.edit_message_text(
            "📅 *Select a Date*\n\n"
            "Available appointment slots:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return SCHEDULING

    elif query.data == "new_quote":
        # Start over
        await start(update, context)
        return SELECTING_SERVICE

    elif query.data == "call_now":
        await query.edit_message_text(
            "📞 *Call Jimenez Plumbing*\n\n"
            "📱 (555) 123-4567\n\n"
            "We're ready to take your call!",
            parse_mode='Markdown'
        )
        return SELECTING_SERVICE

    elif query.data == "back_to_quote":
        service_key = context.user_data.get('selected_service', 'inspection')
        quote_text = generate_quote_text(service_key, "")
        await query.edit_message_text(quote_text, parse_mode='Markdown')
        return CONFIRMING_QUOTE

    return SELECTING_SERVICE


async def date_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle date selection."""
    query = update.callback_query
    await query.answer()

    selected_date = query.data.replace("date_", "")
    context.user_data['selected_date'] = selected_date

    # Generate time slot buttons
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
    day_name = date_obj.strftime("%A, %b %d")

    keyboard = []
    times = ["7:00 AM", "9:00 AM", "11:00 AM", "1:00 PM", "3:00 PM", "5:00 PM"]
    for time in times:
        keyboard.append([InlineKeyboardButton(time, callback_data=f"time_{time}")])

    keyboard.append([InlineKeyboardButton("« Back", callback_data="book_now")])

    await query.edit_message_text(
        f"📅 *{day_name}*\n\n"
        f"Select a time slot:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

    return SCHEDULING


async def time_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle time selection and confirm appointment."""
    query = update.callback_query
    await query.answer()

    selected_time = query.data.replace("time_", "")
    selected_date = context.user_data.get('selected_date', '')
    service_key = context.user_data.get('selected_service', 'inspection')

    user = update.effective_user
    service = PLUMBING_SERVICES.get(service_key, PLUMBING_SERVICES["inspection"])

    # Save appointment
    save_appointment(
        telegram_id=str(user.id),
        customer_name=user.first_name,
        phone=user.username or "",
        service_type=service_key,
        date=selected_date,
        time=selected_time,
        notes=""
    )

    # Format date for display
    date_obj = datetime.strptime(selected_date, "%Y-%m-%d")
    display_date = date_obj.strftime("%A, %B %d")

    await query.edit_message_text(
        f"✅ *APPOINTMENT CONFIRMED!*\n\n"
        f"🔧 *Service:* {service['name']}\n"
        f"📅 *Date:* {display_date}\n"
        f"⏰ *Time:* {selected_time}\n\n"
        f"👤 *Customer:* {user.first_name}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"You'll receive a reminder the day before.\n\n"
        f"📞 Questions? Call (555) 123-4567\n\n"
        f"*Thank you for choosing Jimenez Plumbing!*",
        parse_mode='Markdown'
    )

    logger.info(f"Appointment booked: {user.first_name} on {display_date} at {selected_time}")

    # Notify admin (dad) if chat ID is set
    admin_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if admin_chat_id:
        try:
            await context.bot.send_message(
                chat_id=admin_chat_id,
                text=f"🔔 *NEW APPOINTMENT BOOKED*\n\n"
                     f"👤 {user.first_name}\n"
                     f"🔧 {service['name']}\n"
                     f"📅 {display_date} at {selected_time}\n\n"
                     f"Telegram: @{user.username or 'N/A'}"
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")

    return SELECTING_SERVICE


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle general messages."""
    message_text = update.message.text.lower()
    user = update.effective_user

    # Check for common keywords
    if any(word in message_text for word in ["emergency", "urgent", "flood", "burst"]):
        await update.message.reply_text(EMERGENCY_MESSAGE, parse_mode='Markdown')
        return SELECTING_SERVICE

    if any(word in message_text for word in ["price", "cost", "quote", "how much"]):
        await update.message.reply_text(
            "I can generate a quote for you!\n\n"
            "Please select a service from the menu below:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(s["name"], callback_data=f"service_{k}")]
                for k, s in PLUMBING_SERVICES.items()
            ])
        )
        return SELECTING_SERVICE

    if any(word in message_text for word in ["schedule", "book", "appointment"]):
        await start(update, context)
        return SELECTING_SERVICE

    # Default: show help
    await update.message.reply_text(
        "🔧 *Jimenez Plumbing Assistant*\n\n"
        "I can help you:\n"
        "• Get instant quotes\n"
        "• Schedule appointments\n"
        "• Emergency service info\n\n"
        "Use /start to see all options.",
        parse_mode='Markdown'
    )

    return SELECTING_SERVICE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation."""
    await update.message.reply_text("Conversation cancelled. Use /start to begin again.")
    return SELECTING_SERVICE


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Start the bot."""
    # Initialize database
    init_database()

    # Get token
    token = os.getenv("TG_PLUMBING_BOT_TOKEN")

    if not token or token == "your_bot_token_here":
        print("=" * 60)
        print("🔧 Jimenez Plumbing Telegram Bot")
        print("=" * 60)
        print("\n⚠️  Bot token not configured!")
        print("\nSetup instructions:")
        print("1. Open Telegram and message @BotFather")
        print("2. Send: /newbot")
        print("3. Follow prompts to create your bot")
        print("4. Copy the token BotFather gives you")
        print("5. Add to .env: TG_PLUMBING_BOT_TOKEN='your-token-here'")
        print("6. Run this script again")
        print("=" * 60)
        return

    # Build application
    app = Application.builder().token(token).build()

    # Set up conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_SERVICE: [
                CallbackQueryHandler(service_selected, pattern='^service_'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
            ],
            SELECTING_ISSUE: [
                MessageHandler(filters.TEXT, issue_description),
            ],
            CONFIRMING_QUOTE: [
                CallbackQueryHandler(quote_callback, pattern='^(book_now|call_now|new_quote|back_to_quote)'),
            ],
            SCHEDULING: [
                CallbackQueryHandler(date_selected, pattern='^date_'),
                CallbackQueryHandler(time_selected, pattern='^time_'),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('help', start))
    app.add_handler(CommandHandler('quote', start))

    # Start polling
    logger.info("Starting Jimenez Plumbing Telegram Bot...")
    logger.info("Share your bot: https://t.me/" + token.split(':')[0].replace('bot', '', 1) + "bot")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
