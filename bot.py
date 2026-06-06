import telebot
import google.generativeai as genai
import os
from flask import Flask, request

# --- НАЛАШТУВАННЯ ---
TELEGRAM_TOKEN = "8997989049:AAFxERHINnJxyuch94t5cTYPf5Xq-o6UZak"
GEMINI_API_KEY = "AQ.Ab8RN6LM5wgiWOYHOVwqSLhCK4DBkbSBwxPw6-PCWdF4_SvrJQ"

# Налаштування Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# Обробка вхідних повідомлень від Telegram
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Логіка бота
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        # Gemini відповідає
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception:
        # Якщо щось не так, відправляємо просте повідомлення
        bot.reply_to(message, "Вибач, я зараз не можу відповісти. Спробуй пізніше.")

if __name__ == "__main__":
    # Встановлюємо вебхук при кожному запуску
    bot.remove_webhook()
    bot.set_webhook(url=f"https://bibly-bot-1.onrender.com/{TELEGRAM_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
