import telebot
import google.generativeai as genai
import time

# --- КОНФІГУРАЦІЯ ---
TELEGRAM_TOKEN = "8997989049:AAFxERHINnJxyuch94t5cTYPf5Xq-o6UZak"
GEMINI_API_KEY = "AQ.Ab8RN6LM5wgiWOYHOVwqSLhCK4DBkbSBwxPw6-PCWdF4_SvrJQ"

# Налаштування Gemini (модель flash швидка і безкоштовна)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Ініціалізація бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- ФУНКЦІЇ БОТА ---

def get_ai_response(user_text):
    """Функція для спілкування з Gemini"""
    try:
        # Системна інструкція задає роль боту
        system_prompt = (
            "Ти — Ісус-помічник, духовний наставник. "
            "Відповідай м'яко, з любов'ю, спираючись на Біблію. "
            "Завжди відповідай мовою користувача."
        )
        response = model.generate_content(f"{system_prompt}\n\nПитання: {user_text}")
        return response.text
    except Exception as e:
        print(f"Помилка API Gemini: {e}")
        return "Вибач, я зараз маю труднощі з підключенням до духовної мудрості. Спробуй ще раз трохи згодом. 🙏"

# --- ОБРОБНИКИ ПОВІДОМЛЕНЬ ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Вітаю! Я твій духовний наставник. Я тут, щоб підтримати тебе та відповісти на питання через світло Святого Письма. Про що ти хочеш поговорити?")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Обробка звичайних текстових повідомлень"""
    # Показуємо статус "друкує..."
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Отримуємо відповідь від ІІ
    response_text = get_ai_response(message.text)
    
    # Відправляємо відповідь користувачу
    bot.reply_to(message, response_text)

# --- ЗАПУСК БОТА ---

if __name__ == "__main__":
    print("Бот запускається та підключається до серверів...")
    # remove_webhook потрібен, щоб "скинути" завислі з'єднання
    bot.remove_webhook()
    
    # Запуск бота з обробкою переривань
    try:
        bot.polling(none_stop=True, interval=1, timeout=20)
    except Exception as e:
        print(f"Критична помилка: {e}")
        time.sleep(5) # Зачекати 5 секунд перед перезапуском
