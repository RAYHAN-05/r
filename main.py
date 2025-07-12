
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import json
import random
import datetime
import time
import threading

TOKEN = "7659619297:AAFv6oSvikzxm14Qwe7ZmvhyGkp3xxJdNz4"  # Replace with your actual bot token
bot = telebot.TeleBot(TOKEN)

# Load or initialize channel data
try:
    with open("channels.json", "r") as f:
        data = json.load(f)
except:
    data = {"channels": {}, "signal_on": []}
    with open("channels.json", "w") as f:
        json.dump(data, f)

# Save function
def save_data():
    with open("channels.json", "w") as f:
        json.dump(data, f)

# Start message
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("SIGNAL ON", "SIGNAL OFF")
    markup.row("ADD CHANNEL", "CHANNEL LIST")
    bot.send_message(message.chat.id, "**💢 𝐀𝐔𝐓𝐎 𝐏𝐑𝐄𝐃𝐈𝐂𝐓𝐈𝗢𝗡 💢**\n\n**🚨 আমাদের বটে আপনাকে স্বাগতম আপনি এই বোট এর মাধ্যমে অটোমেটিক আপনার চ্যানেলে সিগনাল নিতে পারবেন।**", parse_mode="Markdown", reply_markup=markup)

# Add channel
@bot.message_handler(func=lambda m: m.text == "ADD CHANNEL")
def ask_channel(message):
    msg = bot.send_message(message.chat.id, "**⛔ ENTER YOUR CHANNEL LINK ⬇️**", parse_mode="Markdown")
    bot.register_next_step_handler(msg, add_channel)

def add_channel(message):
    link = message.text.replace("https://t.me/", "@")
    data["channels"][link] = True
    save_data()
    bot.send_message(message.chat.id, "**🔴 CHANNEL ADDED SUCCESSFULLY ✅**", parse_mode="Markdown")

# Channel List
@bot.message_handler(func=lambda m: m.text == "CHANNEL LIST")
def channel_list(message):
    if data["channels"]:
        msg = "**🔘 ALL CHANNEL LINK ⬇️**\n\n"
        for ch in data["channels"]:
            msg += f"CHANNEL LINK ———> `{ch}`\n"
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "**No channel added yet.**", parse_mode="Markdown")

# Signal ON
@bot.message_handler(func=lambda m: m.text == "SIGNAL ON")
def signal_on(message):
    markup = InlineKeyboardMarkup()
    for ch in data["channels"]:
        markup.add(InlineKeyboardButton(ch, callback_data=f"on|{ch}"))
    bot.send_message(message.chat.id, "**Select channel to SIGNAL ON**", reply_markup=markup, parse_mode="Markdown")

# Signal OFF
@bot.message_handler(func=lambda m: m.text == "SIGNAL OFF")
def signal_off(message):
    markup = InlineKeyboardMarkup()
    for ch in data["channels"]:
        markup.add(InlineKeyboardButton(ch, callback_data=f"off|{ch}"))
    bot.send_message(message.chat.id, "**Select channel to SIGNAL OFF**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    action, ch = call.data.split("|")
    if action == "on":
        if ch not in data["signal_on"]:
            data["signal_on"].append(ch)
            save_data()
        bot.answer_callback_query(call.id, f"Signal ON for {ch}")
    elif action == "off":
        if ch in data["signal_on"]:
            data["signal_on"].remove(ch)
            save_data()
        bot.answer_callback_query(call.id, f"Signal OFF for {ch}")

# Period Generator
def get_period_id():
    now = datetime.datetime.utcnow()
    date = now.strftime("%Y%m%d")
    minutes = now.hour * 60 + now.minute
    period = 10000 + minutes + 1
    return f"{date}{period}"

# Signal Message Generator
def generate_signal(period):
    result1 = random.choice(["𝐁𝐈𝐆", "𝐒𝐌𝐀𝐋𝐋"])
    result2 = random.choice(["🟢", "🔴"])
    result3 = random.choice(["𝟷", "𝟸", "𝟹", "𝟺", "𝟻", "𝟼", "𝟽", "𝟾", "𝟿", "𝟶"])
    return f"""**💢 𝗗𝗞 𝗪𝗜𝗡 𝗔𝗨𝗧𝗢 𝗣𝗥𝗘𝗗𝗜𝗖𝗧𝗜𝗢𝗡 💢**

**⏳ 𝙿𝙴𝚁𝙸𝙾𝙳 𝙸𝙳 : {period}**

**🚨 𝚁𝙴𝚂𝚄𝙻𝚃 --> {result1} + {result2} + {result3}**

**⭕ ᗰᑌՏT ᗷᗴ 7-8 ՏTᗴᑭ ᗰᗩIᑎTᗩIᑎ.**"""

# Auto Prediction Thread
def auto_predict():
    last_period = None
    while True:
        current = get_period_id()
        if current != last_period:
            last_period = current
            msg = generate_signal(current)
            for ch in data["signal_on"]:
                try:
                    bot.send_message(ch, msg, parse_mode="Markdown")
                except:
                    pass
        time.sleep(1)

threading.Thread(target=auto_predict).start()

# Start bot polling
bot.infinity_polling()
