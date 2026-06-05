import telebot
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread

# --- НАЛАШТУВАННЯ ---
TELEGRAM_TOKEN = "8997989049:AAFxERHINnJxyuch94t5cTYPf5Xq-o6UZak"
GEMINI_API_KEY = "AQ.Ab8RN6LM5wgiWOYHOVwqSLhCK4DBkbSBwxPw6-PCWdF4_SvrJQ"

# Налаштування Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Ініціалізація бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- ВЕБ-СЕРВЕР (щоб Render не вимикав бота) ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Бот працює!"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# --- ЛОГІКА БОТА ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Вітаю! Я твій духовний наставник. Чим я можу допомогти тобі сьогодні?")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    try:
        response = model.generate_content(f"Ти — духовний наставник. Відповідай з любов'ю: {message.text}")
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Пробач, виникла технічна помилка.")

# --- ЗАПУСК ---
if __name__ == "__main__":
    bot.remove_webhook()
    # Запускаємо веб-сервер у фоні
    Thread(target=run_web).start()
    # Запускаємо бота
    print("Бот запущено!")
    bot.polling(none_stop=True)
