import telebot
import google.generativeai as genai
import os
from flask import Flask, request

# --- НАЛАШТУВАННЯ ---
TELEGRAM_TOKEN = "8997989049:AAFxERHINnJxyuch94t5cTYPf5Xq-o6UZak"
GEMINI_API_KEY = "AQ.Ab8RN6LM5wgiWOYHOVwqSLhCK4DBkbSBwxPw6-PCWdF4_SvrJQ"
WEBHOOK_URL = "https://bibly-bot-1.onrender.com" 

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

app = Flask(__name__)

@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def get_message():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "Помилка.")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + '/' + TELEGRAM_TOKEN)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
