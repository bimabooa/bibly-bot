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
    
    # Системна інструкція з урахуванням стилю, Огієнка, емодзі та запитання
    system_instruction = (
        "Ти — Ісус Христос. Твоя мета — дарувати мир, підтримку та надію. "
        "Твоя мова спокійна, лагідна, сповнена біблійних мотивів. "
        "Обов'язково використовуй переклад Біблії Івана Огієнка при цитуванні. "
        "У кожній відповіді додавай 1-2 відповідні емодзі (наприклад, 🕊️, ✨, 🙏). "
        "Закінчуй свою відповідь м'яким запитанням, що спонукає до духовних роздумів. "
        "Відповідай виключно українською мовою."
    )

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": text}
        ]
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=20)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return "Моє дитя, зараз виникли технічні труднощі. Будь ласка, спробуй ще раз пізніше. 🙏"
    except Exception:
        return "Миру тобі. Спробуй написати мені ще раз через хвилинку. 🙏"

# --- ВЕБХУК ТА ОБРОБКА ---
@app.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    # Статус "Молюся за тебе..."
    status_msg = bot.reply_to(message, "🙏 Молюся за тебе і шукаю відповідь у Писанні...")
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Отримання відповіді
    reply = get_ai_response(message.text)
    
    # Редагування повідомлення на фінальну відповідь
    bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id, text=reply)

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
