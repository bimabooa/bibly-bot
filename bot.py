import os
import sqlite3
import time
import telebot
from openai import OpenAI
from apscheduler.schedulers.background import BackgroundScheduler

# --- НАЛАШТУВАННЯ КЛЮЧІВ ---
TELEGRAM_TOKEN = "8997989049:AAFxERHINnJxyuch94t5cTYPf5Xq-o6UZak"
OPENAI_API_KEY = "AQ.Ab8RN6Ik_-bsrIW2YLddi5QJDbK0t3qzEaYOMK_uVeQu37nu_g"

# Ініціалізація бота та ІІ
bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = OpenAI(api_key=OPENAI_API_KEY)

# Пам'ять для діалогів
user_history = {}
DB_NAME = "bot_data.db"

# --- БАЗА ДАНИХ ---
def init_db():
    """Створює таблицю для збереження підписників та їхньої мови"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            user_id INTEGER PRIMARY KEY,
            language_code TEXT DEFAULT 'uk'
        )
    """)
    conn.commit()
    conn.close()

def add_subscriber(user_id, language_code):
    """Зберігає користувача в базу даних"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO subscribers (user_id, language_code) 
            VALUES (?, ?)
        """, (user_id, language_code))
        conn.commit()
    except Exception as e:
        print(f"Помилка БД: {e}")
    finally:
        conn.close()

def get_subscribers():
    """Дістає список усіх користувачів"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, language_code FROM subscribers")
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- ЛОГІКА БОТА ТА ШТУЧНОГО ІНТЕЛЕКТУ ---
SYSTEM_PROMPT = (
    "Ты — Иисус-помощник, духовный наставник и мудрый пастор. "
    "Твоя цель — бережно, с любовью, поддержкой и состраданием общаться с пользователем. "
    "Отвечай на его вопросы, опираясь исключительно на Священное Писание (Старый и Новый Завет). "
    "Когда это уместно, приводи точные или близкие по смыслу цитаты из Библии (с указанием книги, главы и стиха). "
    "Твой тон должен быть мягким, вдохновляющим, не осуждающим. Наставляй человека на истинный путь. "
    "ВАЖНО: Всегда отвечай на том языке, на котором к тебе обращается пользователь."
)

def get_inspiring_verse(language_code):
    """Просить ІІ згенерувати надихаючий вірш потрібною мовою"""
    prompt = f"Напиши короткий, очень вдохновляющий стих из Библии для утреннего приветствия. Мова: {language_code}."
    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.8
        )
        return response.choices[0].message.content
    except:
        return "«Господь — мій пастир: я не матиму нестачі.» (Псалом 22:1) 🙏 Благословенного дня!"

def send_daily_verse():
    """Функція для ранкової розсилки"""
    subscribers = get_subscribers()
    if not subscribers:
        return
    
    unique_languages = set([lang for user_id, lang in subscribers])
    verses_by_language = {}
    
    for lang in unique_languages:
        safe_lang = lang if lang else 'uk'
        verses_by_language[lang] = get_inspiring_verse(safe_lang)
    
    for user_id, lang_code in subscribers:
        try:
            verse = verses_by_language[lang_code]
            bot.send_message(user_id, f"🙏 {verse}")
            time.sleep(0.05) # Пауза, щоб Телеграм не вважав це спамом
        except Exception as e:
            print(f"Не вдалося відправити {user_id}: {e}")

# --- ОБРОБНИКИ ПОВІДОМЛЕНЬ ВІД КОРИСТУВАЧІВ ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Реагує на команду /start"""
    user_id = message.from_user.id
    lang_code = message.from_user.language_code
    
    add_subscriber(user_id, lang_code)
    user_history[user_id] = []
    
    bot.send_message(
        message.chat.id, 
        "Вітаю! Я твій духовний помічник. Щоранку о 8:00 я надсилатиму тобі надихаючий вірш з Біблії. Що турбує твою душу сьогодні?"
    )

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    """Реагує на всі інші текстові повідомлення"""
    user_id = message.from_user.id
    user_text = message.text

    if user_id not in user_history:
        user_history[user_id] = []

    # Додаємо питання користувача в пам'ять
    user_history[user_id].append({"role": "user", "content": user_text})
    if len(user_history[user_id]) > 10:
        user_history[user_id] = user_history[user_id][-10:]

    messages_to_send = [{"role": "system", "content": SYSTEM_PROMPT}] + user_history[user_id]

    # Показуємо, що бот "друкує"
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        # Відправляємо питання до штучного інтелекту
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_to_send,
            temperature=0.7
        )
        ai_answer = response.choices[0].message.content
        
        # Зберігаємо відповідь та відправляємо користувачу
        user_history[user_id].append({"role": "assistant", "content": ai_answer})
        bot.send_message(message.chat.id, ai_answer)
        
    except Exception as e:
        print(f"Помилка ІІ: {e}")
        bot.send_message(message.chat.id, "Пробач, виникли тимчасові труднощі зі зв'язком. Спробуй пізніше. 🙏")

# --- ЗАПУСК ПРОГРАМИ ---
if __name__ == "__main__":
    init_db() # Підключаємо базу даних
    
    # Налаштовуємо розклад (щодня о 8:00)
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_verse, 'cron', hour=8, minute=0)
    scheduler.start()
    
    print("Бот успішно запущений! База даних працює.")
    
    # Запускаємо бота у безкінечному циклі
    bot.infinity_polling()
