import telebot
import google.generativeai as genai
import os
from flask import Flask, request

# --- НАЛАШТУВАННЯ ---
TELEGRAM_TOKEN = "8997989049:AAFxERHINnJxyuch94t5cTYPf5Xq-o6UZak"
GEMINI_API_KEY = "AQ.Ab8RN6LM5wgiWOYHOVwqSLhCK4DBkbSBwxPw6-PCWdF4_SvrJQ"
WEBHOOK_URL = "https://bibly-bot-1.onrender.com"

# Ініціалізація
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# --- ВЕБХУК ДЛЯ TELEGRAM ---
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# --- ЛОГІКА БОТА ---
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    print(f"--- Отримано повідомлення: {message.text} ---")
    try:
        # Запит до Gemini
        prompt = f"Ти — духовний наставник. Відповідай з любов'ю: {message.text}"
        response = model.generate_content(prompt)
        
        # Перевірка, чи прийшла відповідь
        if response.text:
            print(f"--- Відповідь Gemini: {response.text[:50]}... ---")
            bot.reply_to(message, response.text)
        else:
            print("--- Помилка: Gemini повернув порожню відповідь ---")
            bot.reply_to(message, "Я отримав твоє питання, але не зміг сформулювати відповідь.")
            
    except Exception as e:
        print(f"--- КРИТИЧНА ПОМИЛКА: {str(e)} ---")
        bot.reply_to(message, f"Технічна помилка: {str(e)}")

# --- ЗАПУСК ---
if __name__ == "__main__":
    bot.remove_webhook()
    webhook_url = f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}"
    bot.set_webhook(url=webhook_url)
    print(f"Бот запущено! Вебхук встановлено на: {webhook_url}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
