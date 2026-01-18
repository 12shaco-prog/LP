from telegram.ext import (
    Updater, MessageHandler, Filters,
    CommandHandler, ConversationHandler
)
from datetime import datetime
import re
import os

# ========= CONFIG =========
BOT_TOKEN = os.getenv("8336768468:AAHBGSbIisH4J9Ly6HONS6olfEUqaHMAuS4")  # Railway env variable
updater = Updater("PASTE_YOUR_BOT_TOKEN_HERE", use_context=True)

ALLOWED_USERS = [
    528232976,   # <-- PUT YOUR TELEGRAM USER ID
    679232825    # <-- OPTIONAL
]

PHOTO_ID = "AgACAgUAAxkBAAIBxxxxxxx"  # <-- YOUR TELEGRAM FILE_ID

# ========= STATES =========
INPUT_ROOM, INPUT_USAGE = range(2)

# ========= PRICES =========
USD_TO_RIEL = 4100
ELEC_PRICE_RIEL = 1000
WATER_PRICE_RIEL = 1000
MOTOR_PRICE_USD = 5


# ========= HELPERS =========
def allowed(update):
    return update.message.from_user.id in ALLOWED_USERS


# ========= START =========
def start(update, context):
    if not allowed(update):
        update.message.reply_text("❌ You are not allowed to use this bot.")
        return ConversationHandler.END

    context.user_data.clear()
    update.message.reply_text(
        "📋 បញ្ចូល:\n"
        "ឈ្មោះ អ្នកជួល  បន្ទប់  ជួល  ម៉ូតូ\n\n"
        "ឧទាហរណ៍:\n"
        "Sok Dara C2 70 2\n"
        "សុខ ដារ៉ា ត5 80 1"
    )
    return INPUT_ROOM


def parse_room(text):
    p = text.strip().split()
    if len(p) < 4:
        return None
    try:
        name = " ".join(p[:-3])
        room = p[-3]
        rent = float(p[-2])
        motors = int(p[-1])
        return name, room, rent, motors
    except:
        return None


def input_room(update, context):
    if not allowed(update):
        return ConversationHandler.END

    parsed = parse_room(update.message.text)
    if not parsed:
        update.message.reply_text("❌ សូមបញ្ចូល: ឈ្មោះ បន្ទប់ ជួល ម៉ូតូ")
        return INPUT_ROOM

    name, room, rent, motors = parsed

    context.user_data.update({
        "name": name,
        "room": room,
        "rent": rent,
        "motors": motors,
        "date": datetime.now().strftime("%d-%m-%Y")
    })

    update.message.reply_text(
        "⚡️💧 បញ្ចូលលេខ (ANY FORMAT):\n"
        "old_e → new_e  old_w → new_w\n\n"
        "ឧទាហរណ៍:\n"
        "1200 → 1250  500 → 520"
    )
    return INPUT_USAGE


def input_usage(update, context):
    if not allowed(update):
        return ConversationHandler.END

    nums = re.findall(r"\d+(?:\.\d+)?", update.message.text)
    if len(nums) < 4:
        update.message.reply_text("❌ សូមបញ្ចូលលេខ 4")
        return INPUT_USAGE

    old_e, new_e, old_w, new_w = map(float, nums[:4])

    e_used = new_e - old_e
    w_used = new_w - old_w

    elec_cost = e_used * ELEC_PRICE_RIEL
    water_cost = w_used * WATER_PRICE_RIEL

    rent = context.user_data["rent"]
    motors = context.user_data["motors"]
    motor_cost = motors * MOTOR_PRICE_USD

    fixed_usd = rent + motor_cost
    fixed_riel = fixed_usd * USD_TO_RIEL

    total_riel = fixed_riel + elec_cost + water_cost
    total_usd = total_riel / USD_TO_RIEL

    caption = f"""
🧾 វិក្កយបត្រ បន្ទប់ជួល

👤 អ្នកជួល: {context.user_data['name']}
🏠 បន្ទប់: {context.user_data['room']}
📅 ថ្ងៃបង់ប្រាក់: {context.user_data['date']}

💰 ជួលបន្ទប់: ${rent}
🏍️ ម៉ូតូ: {motors} × $5 = ${motor_cost}

⚡️ ភ្លើង: {old_e} → {new_e}
ប្រើអស់: {e_used} × {ELEC_PRICE_RIEL} = {elec_cost:,.0f} ៛

💧 ទឹក: {old_w} → {new_w}
ប្រើអស់: {w_used} × {WATER_PRICE_RIEL} = {water_cost:,.0f} ៛

-----------------------
💵 សរុប: {total_riel:,.0f} ៛
(≈ ${total_usd:.2f})

💱 $1 = {USD_TO_RIEL} ៛
"""

    update.message.reply_photo(
        photo=PHOTO_ID,
        caption=caption
    )

    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text("❌ បញ្ចប់ /start")
    return ConversationHandler.END


# ========= MAIN =========
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            INPUT_ROOM: [MessageHandler(Filters.text & ~Filters.command, input_room)],
            INPUT_USAGE: [MessageHandler(Filters.text & ~Filters.command, input_usage)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dp.add_handler(conv)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
