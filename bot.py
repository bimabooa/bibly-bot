import telebot
import google.generativeai as genai

# --- НАЛАШТУВАННЯ ---
TELEGRAM_TOKEN = "8997989049:AAFxERHINnJxyuch94t5cTYPf5Xq-o6UZak"
GEMINI_API_KEY = "AQ.Ab8RN6LM5wgiWOYHOVwqSLhCK4DBkbSBwxPw6-PCWdF4_SvrJQ"

# Налаштування Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Ініціалізація бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

def get_ai_response(user_text):
    try:
        response = model.generate_content(f"Ти — Ісус-помічник. Відповідай на питання користувача: {user_text}")
        return response.text
    except Exception as e:
        return f"Помилка ІІ: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Вітаю! Я готовий допомогти.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    answer = get_ai_response(message.text)
    bot.send_message(message.chat.id, answer)

if __name__ == "__main__":
    print("Бот запущений!")
    bot.polling(none_stop=True)
