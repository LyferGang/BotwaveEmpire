#!/usr/bin/env python3
"""
BOTWAVE PERSONAL BOT - "Boti1904"
Private assistant for Al Gringo ONLY

Bot Token: 8747407183:AAHimCXAm0SleFh7DCW_xxmH7vn09nnAZ3k
Owner: Al Gringo (8711428786)

This bot is PRIVATE - only YOU can access it.
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
import requests
import subprocess
from pathlib import Path

# Configuration
BOT_TOKEN = "8747407183:AAHimCXAm0SleFh7DCW_xxmH7vn09nnAZ3k"
OWNER_ID = 8711428786  # ONLY you can access
ALLOWED_USERS = {OWNER_ID}  # Strict access control
LM_STUDIO_URL = "http://localhost:1234/v1"
LM_STUDIO_MODEL = "llama-3.1-8b-instruct-abliterated-obliteratus"

# Paths
BASE_DIR = Path(__file__).parent
AGENT_RUNNER = BASE_DIR / "lib" / "agent_runner.py"

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonalBot:
    """Personal AI assistant for Al Gringo."""

    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()

    def setup_handlers(self):
        """Setup bot handlers."""
        # Commands
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.show_help))
        self.app.add_handler(CommandHandler("status", self.botwave_status))
        self.app.add_handler(CommandHandler("agents", self.agent_status))
        self.app.add_handler(CommandHandler("run", self.run_agent_task))
        self.app.add_handler(CommandHandler("audit", self.run_audit))
        self.app.add_handler(CommandHandler("deploy", self.deploy_bot))

        # Callbacks
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))

        # Messages - only from owner
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

    def is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized."""
        return user_id in ALLOWED_USERS

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message."""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("🔐 Access denied. This bot is private.")
            return

        welcome = """
🤖 *Boti1904 - Your Personal AI Assistant*

*Commands:*
/status - Botwave system status
/agents - Agent jobs status
/run <task> - Run agent task
/audit - Run self-audit
/deploy <bot> - Deploy a bot

*Quick Actions:*
"""
        keyboard = [
            [InlineKeyboardButton("📊 STATUS", callback_data="status")],
            [InlineKeyboardButton("🤖 AGENTS", callback_data="agents")],
            [InlineKeyboardButton("🔍 AUDIT", callback_data="audit")],
            [InlineKeyboardButton("💬 CHAT AI", callback_data="chat")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome, reply_markup=reply_markup, parse_mode="Markdown")

    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help."""
        if not self.is_authorized(update.effective_user.id):
            return

        help_text = """
*Botwave Personal Bot Commands:*

/status - Check all systems
/agents - List agent jobs
/run <task> - Create agent task
/audit - Run code self-audit
/deploy - Deploy/update bots

*Examples:*
/run Fix the lead capture bug
/audit --list-issues
"""
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def botwave_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show Botwave status."""
        if not self.is_authorized(update.effective_user.id):
            return

        # Get status
        try:
            result = subprocess.run(
                ["python3", str(BASE_DIR / "bin" / "cli.py"), "status"],
                capture_output=True, text=True, timeout=10
            )
            await update.message.reply_text(f"```\n{result.stdout}\n```", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Status check failed: {e}")

    async def agent_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show agent jobs."""
        if not self.is_authorized(update.effective_user.id):
            return

        try:
            result = subprocess.run(
                ["python3", str(AGENT_RUNNER), "list"],
                capture_output=True, text=True, timeout=10
            )
            await update.message.reply_text(f"```\n{result.stdout}\n```", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Agent status failed: {e}")

    async def run_agent_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Run an agent task."""
        if not self.is_authorized(update.effective_user.id):
            return

        task = " ".join(context.args)
        if not task:
            await update.message.reply_text("Usage: /run <task description>")
            return

        await update.message.reply_text(f"🤖 Creating agent task: {task}")

        try:
            result = subprocess.run(
                ["python3", str(AGENT_RUNNER), "create", "--name", f"telegram_task", "--task", task],
                capture_output=True, text=True, timeout=30
            )
            await update.message.reply_text(f"```\n{result.stdout}\n```", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Task creation failed: {e}")

    async def run_audit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Run self-audit."""
        if not self.is_authorized(update.effective_user.id):
            return

        await update.message.reply_text("🔍 Running self-audit...")

        audit_script = BASE_DIR / "skills" / "active" / "self-audit" / "audit.py"
        try:
            result = subprocess.run(
                ["python3", str(audit_script), "--list-issues"],
                capture_output=True, text=True, timeout=60
            )
            await update.message.reply_text(f"```\n{result.stdout}\n```", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"Audit failed: {e}")

    async def deploy_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Deploy a bot."""
        if not self.is_authorized(update.effective_user.id):
            return

        bot_name = " ".join(context.args) if context.args else "plumbing"
        await update.message.reply_text(f"🚀 Deploying {bot_name} bot...")

        # Run the bot
        bot_file = BASE_DIR / f"botwave_{bot_name}_bot.py"
        if bot_file.exists():
            try:
                result = subprocess.run(
                    ["python3", str(bot_file)],
                    capture_output=True, text=True, timeout=10
                )
                await update.message.reply_text(f"Bot started!\n```\n{result.stdout}\n```", parse_mode="Markdown")
            except Exception as e:
                await update.message.reply_text(f"Deploy failed: {e}")
        else:
            await update.message.reply_text(f"Bot file not found: {bot_file}")

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks."""
        if not self.is_authorized(update.effective_user.id):
            return

        query = update.callback_query
        await query.answer()
        data = query.data

        if data == "status":
            await self.botwave_status(update, context)
        elif data == "agents":
            await self.agent_status(update, context)
        elif data == "audit":
            await self.run_audit(update, context)
        elif data == "chat":
            await query.edit_message_text("💬 AI Chat ready! Send me a message and I'll use local LLM to respond.")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages with AI."""
        if not self.is_authorized(update.effective_user.id):
            await update.message.reply_text("🔐 Access denied.")
            return

        user_text = update.message.text

        # Get AI response from local LLM
        ai_response = self.get_ai_response(user_text)

        await update.message.reply_text(ai_response)

    def get_ai_response(self, user_text: str) -> str:
        """Get AI response from local LM Studio."""
        try:
            resp = requests.post(
                f"{LM_STUDIO_URL}/chat/completions",
                json={
                    "model": LM_STUDIO_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are Boti1904, Al Gringo's personal AI assistant for Botwave Empire. Help him manage bots, agents, and business automation. Be concise and actionable."},
                        {"role": "user", "content": user_text}
                    ]
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
        except:
            pass
        return "Having trouble connecting to LM Studio. Check status with /status"

    def run(self):
        """Start the bot."""
        logger.info("Starting Personal Bot (Boti1904) - Owner access only...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    bot = PersonalBot()
    bot.run()
