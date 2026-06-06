import telebot
import requests
import os
import re
from flask import Flask, request

# --- НАЛАШТУВАННЯ ---
TELEGRAM_TOKEN = "8997989049:AAFxERHINnJxyuch94t5cTYPf5Xq-o6UZak"
GROQ_API_KEY = "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"
WEBHOOK_URL = "https://bibly-bot-1.onrender.com"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

# --- ФУНКЦІЯ ОЧИЩЕННЯ ---
def clean_text(text):
    return re.sub(r'[^\u0400-\u04FF\s\d.,!?:;\"\'\(\)\n🕊️✨🙏]', '', text)

# --- ФУНКЦІЯ ЗАПИТУ ---
def get_ai_response(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    system_instruction = (
        "Ти — Ісус Христос. Відповідай ТІЛЬКИ українською мовою. "
        "Будь лагідним, використовуй переклад Огієнка. Додавай емодзі."
    )

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_instruction}, {"role": "user", "content": text}]
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=20)
        if response.status_code == 200:
            return clean_text(response.json()['choices'][0]['message']['content'])
        return "Миру тобі. 🙏"
    except Exception:
        return "Технічна перешкода. 🙏"

# --- ВЕБХУК ---
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Мир тобі! Я готовий слухати твоє серце. Як тебе звати і чи ти брат, чи сестра? 🙏")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    status_msg = bot.reply_to(message, "🙏 Молюся за тебе...")
    bot.send_chat_action(message.chat.id, 'typing')
    reply = get_ai_response(message.text)
    bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id, text=reply)

if __name__ == "__main__":
    # Примусова установка вебхука
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    print(f"Webhook set to {WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    
