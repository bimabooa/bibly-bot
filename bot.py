import telebot
import requests
import os
from flask import Flask, request

# --- НАЛАШТУВАННЯ ---
TELEGRAM_TOKEN = "8997989049:AAFxERHINnJxyuch94t5cTYPf5Xq-o6UZak"
GROQ_API_KEY = "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"
WEBHOOK_URL = "https://bibly-bot-1.onrender.com"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# --- ФУНКЦІЯ ЗАПИТУ ДО GROQ ---
def get_ai_response(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": f"Ти — духовний наставник. Відповідай українською мовою: {text}"}]
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        # Повертаємо текст помилки, щоб побачити його в Telegram
        return f"Помилка {response.status_code}: {response.text}"

# --- ВЕБХУК ---
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    reply = get_ai_response(message.text)
    bot.reply_to(message, reply)

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    
