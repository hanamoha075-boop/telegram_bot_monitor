import sqlite3
import os

# ✅ المسار الكامل لقاعدة البيانات
DB_PATH = "bot_data.db"

# إنشاء المجلد إذا لم يكن موجود
folder = os.path.dirname(DB_PATH)
if not os.path.exists(folder):
    os.makedirs(folder)
    print(f"تم إنشاء المجلد: {folder}")

# الاتصال بقاعدة البيانات (سيتم إنشاؤها إذا لم تكن موجودة)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# إنشاء جدول المستخدمين
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    username TEXT,
    joined_date TEXT
)
""")

# إنشاء جدول الرسائل
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
print(f"✅ تم إنشاء قاعدة البيانات والجداول في:\n{DB_PATH}")
