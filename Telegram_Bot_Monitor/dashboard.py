import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import telebot

# ضع هنا توكن البوت الخاص بك
BOT_TOKEN = "8295880590:AAFB635wZtQ82UDYLiUiIYnSkrfS69w0ZnY"
bot = telebot.TeleBot(BOT_TOKEN)

# مسار قاعدة البيانات الثابت
DB_PATH = "bot_data.db"

class BotDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📊 Telegram Bot Dashboard")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f4f4f4")

        # عنوان
        title = tk.Label(self.root, text="لوحة مراقبة البوت 🤖", font=("Arial", 18, "bold"), bg="#f4f4f4")
        title.pack(pady=10)

        # عدد المستخدمين
        self.user_count_label = tk.Label(self.root, text="عدد المستخدمين: 0", font=("Arial", 14), bg="#f4f4f4")
        self.user_count_label.pack()

        # أزرار
        frame_btn = tk.Frame(self.root, bg="#f4f4f4")
        frame_btn.pack(pady=5)
        self.refresh_btn = tk.Button(frame_btn, text="🔄 تحديث البيانات", command=self.load_users)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        self.broadcast_btn = tk.Button(frame_btn, text="📢 إرسال رسالة", command=self.broadcast_message)
        self.broadcast_btn.pack(side=tk.LEFT, padx=5)

        # Treeview لعرض المستخدمين
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Username"), show="headings", selectmode="extended")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="الاسم")
        self.tree.heading("Username", text="المستخدم")
        self.tree.pack(pady=10, fill=tk.X, padx=10)
        self.tree.bind("<<TreeviewSelect>>", self.show_messages_for_user)

        # Listbox لعرض الرسائل
        lbl_messages = tk.Label(self.root, text="📩 الرسائل الخاصة بالمستخدم المحدد:", font=("Arial", 12), bg="#f4f4f4")
        lbl_messages.pack(pady=5)
        self.msg_listbox = tk.Listbox(self.root, width=120, height=15)
        self.msg_listbox.pack(padx=10, pady=5)

        # ملصق عدد الرسائل
        self.msg_count_label = tk.Label(self.root, text="إجمالي الرسائل: 0", font=("Arial", 12), bg="#f4f4f4")
        self.msg_count_label.pack(pady=5)

        # تحميل المستخدمين عند التشغيل
        self.load_users()
        self.root.mainloop()

    # الاتصال بالقاعدة
    def connect_db(self):
        return sqlite3.connect(DB_PATH)

    # تحميل المستخدمين
    def load_users(self):
        conn = self.connect_db()
        c = conn.cursor()
        # إنشاء الجدول إذا لم يكن موجودًا
        c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, first_name TEXT, username TEXT, joined_date TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, message TEXT, timestamp TEXT)")
        c.execute("SELECT id, first_name, username FROM users")
        rows = c.fetchall()
        conn.close()

        # تحديث Treeview
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", tk.END, values=row)
        self.user_count_label.config(text=f"عدد المستخدمين: {len(rows)}")

        # تنظيف الرسائل
        self.msg_listbox.delete(0, tk.END)
        self.msg_count_label.config(text="إجمالي الرسائل: 0")

    # عرض رسائل المستخدم المحدد
    def show_messages_for_user(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        # نأخذ أول مستخدم محدد لعرض رسائله
        user_id = self.tree.item(selected_items[0])["values"][0]

        conn = self.connect_db()
        c = conn.cursor()
        c.execute("SELECT message, timestamp FROM messages WHERE user_id=? ORDER BY id", (user_id,))
        messages = c.fetchall()
        conn.close()

        self.msg_listbox.delete(0, tk.END)
        for msg, ts in messages:
            self.msg_listbox.insert(tk.END, f"[{ts}] {msg}")

        self.msg_count_label.config(text=f"إجمالي الرسائل: {len(messages)}")

    # إرسال رسالة عامة أو محددة
    def broadcast_message(self):
        # الحصول على المستخدمين المحددين
        selected_items = self.tree.selection()
        if selected_items:
            users_to_send = [self.tree.item(i)["values"][0] for i in selected_items]
        else:
            # إذا لم يتم التحديد، نرسل لكل المستخدمين
            conn = self.connect_db()
            c = conn.cursor()
            c.execute("SELECT id FROM users")
            users_to_send = [row[0] for row in c.fetchall()]
            conn.close()

        msg = simpledialog.askstring("رسالة", "📝 اكتب الرسالة:")
        if not msg:
            return

        # إرسال الرسائل عبر البوت وتسجيلها
        conn = self.connect_db()
        c = conn.cursor()
        sent_count = 0
        for user_id in users_to_send:
            try:
                bot.send_message(user_id, msg)
                c.execute("INSERT INTO messages (user_id, message, timestamp) VALUES (?, ?, datetime('now'))", (user_id, msg))
                sent_count += 1
            except Exception as e:
                print(f"خطأ عند إرسال رسالة للمستخدم {user_id}: {e}")
        conn.commit()
        conn.close()

        messagebox.showinfo("تم الإرسال", f"✅ تم إرسال الرسالة لـ {sent_count} مستخدم.")

if __name__ == "__main__":
    BotDashboard()
