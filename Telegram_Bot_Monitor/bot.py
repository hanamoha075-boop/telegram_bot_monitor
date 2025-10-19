import telebot
import sqlite3
from datetime import datetime

# ضع هنا توكن البوت الخاص بك
BOT_TOKEN = "8295880590:AAFB635wZtQ82UDYLiUiIYnSkrfS69w0ZnY"

bot = telebot.TeleBot(BOT_TOKEN)

# مسار قاعدة البيانات الثابت
DB_PATH = "bot_data.db"

# إنشاء قاعدة البيانات والجداول إذا لم تكن موجودة
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # جدول المستخدمين
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            joined_date TEXT
        )
    """)
    # جدول الرسائل
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# حفظ المستخدم الجديد
def save_user(user):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # تحقق من وجود المستخدم
    c.execute("SELECT id FROM users WHERE id=?", (user.id,))
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (id, first_name, username, joined_date) VALUES (?, ?, ?, ?)",
            (user.id, user.first_name, user.username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
    conn.commit()
    conn.close()

# حفظ الرسائل
def save_message(user_id, message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (user_id, message, timestamp) VALUES (?, ?, ?)",
        (user_id, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

# عند أمر /start
@bot.message_handler(commands=['start'])
def start_message(message):
    save_user(message.from_user)
    bot.reply_to(message, f"مرحبًا {message.from_user.first_name}! 👋\nأنا بوت تجريبي لمراقبة المستخدمين.")

# التعامل مع أي رسالة
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    save_user(message.from_user)
    save_message(message.from_user.id, message.text)
    bot.reply_to(message, "✅ تم تسجيل رسالتك!")

print("✅ البوت يعمل الآن...")
bot.polling(none_stop=True)
