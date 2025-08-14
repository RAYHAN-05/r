import random
import requests
from datetime import datetime, timezone
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)


TOKEN = "8465059365:AAFGk-sPCnj77bx3oVDyqCzh_jO1SNdCBEI"

FIREBASE_BASE = "https://jssss-41e18-default-rtdb.firebaseio.com"
FIREBASE_USERS = f"{FIREBASE_BASE}/users"
FIREBASE_PRED = f"{FIREBASE_BASE}/manual_predictions"

# === Period Functions ===
def get_current_period():
    now = datetime.now(timezone.utc)
    minutes = now.hour * 60 + now.minute
    return f"{now.strftime('%Y%m%d')}1000{10001 + minutes}"

def get_next_period():
    now = datetime.now(timezone.utc)
    minutes = now.hour * 60 + now.minute + 1
    return f"{now.strftime('%Y%m%d')}1000{10001 + minutes}"


def get_user(user_id):
    r = requests.get(f"{FIREBASE_USERS}/{user_id}.json")
    return r.json() if r.ok and r.json() else None

def create_user(user_id, name):
    data = {"coins": 0, "name": name}
    requests.patch(f"{FIREBASE_USERS}/{user_id}.json", json=data)
    return data

def update_user(user_id, obj):
    requests.patch(f"{FIREBASE_USERS}/{user_id}.json", json=obj)

def get_manual_prediction(period):
    r = requests.get(f"{FIREBASE_PRED}/{period}.json")
    return r.json() if r.ok and r.json() else None

def set_manual_prediction(period, prediction):
    return requests.put(f"{FIREBASE_PRED}/{period}.json", json={"prediction": prediction}).ok


def main_keyboard():
    return ReplyKeyboardMarkup(
        [["🔮 PREDICT", "👤 PROFILE"], ["ℹ️ ABOUT"]],
        resize_keyboard=True
    )

def predict_mode_keyboard():
    return ReplyKeyboardMarkup(
        [["🤖 AUTO AI", "📝 MANUAL"], ["🔙 Back"]],
        resize_keyboard=True
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    user = get_user(u.id)
    if not user:
        user = create_user(u.id, u.full_name)
    await update.message.reply_text(f"👋 Welcome, {u.full_name}!", reply_markup=main_keyboard())

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    user = get_user(u.id)
    if not user:
        user = create_user(u.id, u.full_name)

    if user.get("coins", 0) <= 0:
        return await update.message.reply_text("❌ You have 0 coins. Contact @GodXAshura.")

    context.user_data["predict_mode"] = True
    await update.message.reply_text("Choose prediction mode:", reply_markup=predict_mode_keyboard())

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    u = update.effective_user
    uid = u.id

    user = get_user(uid)
    if not user:
        user = create_user(uid, u.full_name)

    if context.user_data.get("predict_mode"):
        if txt == "🔙 Back":
            context.user_data["predict_mode"] = False
            return await update.message.reply_text("Back to main menu", reply_markup=main_keyboard())

        coins = user.get("coins", 0)
        if coins <= 0:
            return await update.message.reply_text("❌ You have 0 coins. Contact RS_RAYHAN")

        period = get_current_period()

        if txt == "🤖 AUTO AI":
            pred = random.choice(["BIG", "SMALL"])
            conf = random.randint(85, 99)
            update_user(uid, {"coins": coins - 1})
            context.user_data["predict_mode"] = False
            return await update.message.reply_text(
                f"🎯 *RAYHAN AI PREDICTION*\n\n"
                f"⏰ Period: `{period}`\n"
                f"🔮 Prediction: *{pred}*\n"
                f"📈 Confidence: `{conf}%`\n"
                f"💰 Cost: `1 coin deducted`",
                parse_mode="Markdown",
                reply_markup=main_keyboard()
            )

        elif txt == "📝 MANUAL":
            manual = get_manual_prediction(period)
            context.user_data["predict_mode"] = False
            if manual and manual.get("prediction") in ["BIG", "SMALL"]:
                update_user(uid, {"coins": coins - 1})
                return await update.message.reply_text(
                    f"🧑‍💼 *MANUAL PREDICTION*\n\n"
                    f"⏰ Period: `{period}`\n"
                    f"🔮 Prediction: *{manual['prediction']}*\n"
                    f"📈 Confidence: `99%`\n"
                    f"💰 Cost: `1 coin deducted`",
                    parse_mode="Markdown",
                    reply_markup=main_keyboard()
                )
            else:
                return await update.message.reply_text(
                    "❌ Manual prediction not set by admin.",
                    reply_markup=main_keyboard()
                )
        else:
            return await update.message.reply_text("Please select from the buttons.")

    if txt == "🔮 PREDICT":
        return await predict(update, context)
    elif txt == "👤 PROFILE":
        return await profile(update, context)
    elif txt == "ℹ️ ABOUT":
        return await about(update, context)
    else:
        await update.message.reply_text("❓ Use the menu buttons.")

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    user = get_user(u.id)
    if not user:
        user = create_user(u.id, u.full_name)
    await update.message.reply_text(
        f"👤 Your Profile\n\n"
        f"Name: {user.get('name', 'N/A')}\n"
        f"Telegram ID: {u.id}\n"
        f"Coins: {user.get('coins', 0)}",
        parse_mode="Markdown"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 RAYHAN AI BOT by RS_RAYHAN")


async def admin_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        per = context.args[0]
        pred = context.args[1].upper()

        if per == "next":
            per = get_next_period()
        elif per == "current":
            per = get_current_period()

        if pred not in ("BIG", "SMALL"):
            raise ValueError("Invalid prediction")

        set_manual_prediction(per, pred)
        await update.message.reply_text(f"✅ Prediction set for `{per}` as *{pred}*", parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Usage: /admin_set <current|next|PERIOD> <BIG|SMALL>")

async def admin_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current = get_current_period()
    nextp = get_next_period()
    current_pred = get_manual_prediction(current)
    next_pred = get_manual_prediction(nextp)

    msg = f"📊 *PREDICTION STATUS*\n\n"
    msg += f"🕒 Current Period: `{current}`\n"
    msg += f"🔮 Prediction: *{current_pred['prediction']}*\n" if current_pred else "🔮 Prediction: Not set\n"
    msg += f"\n➡️ Next Period: `{nextp}`\n"
    msg += f"🔮 Prediction: *{next_pred['prediction']}*\n" if next_pred else "🔮 Prediction: Not set\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

async def add_coin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tg_id = context.args[0]
        amount = int(context.args[1])
        user = get_user(tg_id)
        if user:
            new_coins = user.get("coins", 0) + amount
            update_user(tg_id, {"coins": new_coins})
            await update.message.reply_text(f"✅ Added {amount} coins to user {tg_id}")
        else:
            await update.message.reply_text("❌ User not found.")
    except:
        await update.message.reply_text("❌ Usage: /add_coin <telegram_id> <amount>")


if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("admin_set", admin_set))
    app.add_handler(CommandHandler("admin_status", admin_status))
    app.add_handler(CommandHandler("add_coin", add_coin))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Bot running...")
    app.run_polling()
