import telebot
import psycopg2
import random
import os
import html
import time
from dotenv import load_dotenv
from telebot import types

# Load .env variables (Local testing only)
# On Railway, these will be loaded automatically from the dashboard
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found.")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found. Make sure to add the PostgreSQL plugin in Railway.")

ADMIN_ID = 1384677187   # REPLACE WITH YOUR REAL ID
HER_ID = 987654321      # REPLACE WITH HER REAL ID

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Helper function to get a database connection
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

# Create table (PostgreSQL syntax)
try:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS shayari (
                id SERIAL PRIMARY KEY,
                file_id TEXT,
                mood TEXT,
                text TEXT,
                used INTEGER DEFAULT 0
            );
            """)
        conn.commit()
    print("✅ Database connected and table checked.")
except Exception as e:
    print(f"❌ Database error: {e}")

# --- 🛠 ADMIN COMMANDS ---

@bot.message_handler(commands=['upload'])
def upload(message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split()
    mood = parts[1] if len(parts) > 1 else "any"

    msg = bot.send_message(
        message.chat.id,
        f"Send the voice note 🌙\nMood: {mood}"
    )
    bot.register_next_step_handler(msg, save_voice, mood)

def save_voice(message, mood):
    if not message.voice:
        bot.send_message(message.chat.id, "❌ That wasn't a voice note. Cancelled.")
        return

    file_id = message.voice.file_id

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO shayari (file_id, mood, text) VALUES (%s, %s, %s)",
                (file_id, mood, None)
            )
        conn.commit()

    bot.send_message(message.chat.id, f"✨ Voice saved as '{mood}'.")

@bot.message_handler(commands=['addtext'])
def add_text(message):
    if message.from_user.id != ADMIN_ID:
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.send_message(message.chat.id, "Usage: /addtext <mood> <shayari>")
        return

    mood, text = parts[1], parts[2]

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO shayari (file_id, mood, text) VALUES (%s, %s, %s)",
                (None, mood, text)
            )
        conn.commit()

    bot.send_message(message.chat.id, f"📝 Text saved as '{mood}'.")

# --- 💖 HER INTERFACE ---

@bot.message_handler(commands=['start', 'menu'])
def menu(message):
    if message.from_user.id not in [HER_ID, ADMIN_ID]:
        return
        
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('/romantic')
    btn2 = types.KeyboardButton('/sad')
    btn3 = types.KeyboardButton('/hope')
    btn4 = types.KeyboardButton('/shayari')
    
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(
        message.chat.id, 
        "How are you feeling right now? 🌙", 
        reply_markup=markup
    )

def send_shayari(message, mood):
    if message.from_user.id != HER_ID and message.from_user.id != ADMIN_ID:
        return

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # 1. First Attempt
            if mood == "any":
                cur.execute("SELECT id, file_id, text FROM shayari WHERE used=0 ORDER BY RANDOM() LIMIT 1")
            else:
                cur.execute("SELECT id, file_id, text FROM shayari WHERE mood=%s AND used=0 ORDER BY RANDOM() LIMIT 1", (mood,))
            
            row = cur.fetchone()

            # 2. Reset if empty
            if not row:
                if mood == "any":
                    cur.execute("UPDATE shayari SET used=0")
                else:
                    cur.execute("UPDATE shayari SET used=0 WHERE mood=%s", (mood,))
                conn.commit() # Commit the reset
                
                # Retry fetch
                if mood == "any":
                    cur.execute("SELECT id, file_id, text FROM shayari ORDER BY RANDOM() LIMIT 1")
                else:
                    cur.execute("SELECT id, file_id, text FROM shayari WHERE mood=%s ORDER BY RANDOM() LIMIT 1", (mood,))
                row = cur.fetchone()

            # 3. If still empty
            if not row:
                bot.send_message(message.chat.id, "He hasn’t filled this jar yet 💭")
                return

            sid, file_id, text_content = row
            
            # Mark used
            cur.execute("UPDATE shayari SET used=1 WHERE id=%s", (sid,))
            conn.commit()

        # Send Logic
        caption = random.choice([
            "For you. Always.",
            "He recorded this softly.",
            "Listen slowly 🌙",
            "Just a thought...",
            "Close your eyes."
        ])

        if file_id:
            bot.send_chat_action(message.chat.id, 'upload_voice')
            time.sleep(1)
            bot.send_voice(message.chat.id, file_id, caption=caption)
        else:
            bot.send_chat_action(message.chat.id, 'typing')
            time.sleep(1)
            safe_text = html.escape(text_content)
            safe_caption = html.escape(caption)
            bot.send_message(message.chat.id, f"💌 {safe_text}\n\n<i>{safe_caption}</i>", parse_mode="HTML")

    finally:
        conn.close()

# --- 🎭 COMMAND HANDLERS ---

@bot.message_handler(commands=['shayari'])
def any_shayari(message):
    send_shayari(message, "any")

@bot.message_handler(commands=['romantic'])
def romantic(message):
    send_shayari(message, "romantic")

@bot.message_handler(commands=['sad'])
def sad(message):
    send_shayari(message, "sad")

@bot.message_handler(commands=['hope'])
def hope(message):
    send_shayari(message, "hope")

print("Bot is running...")
bot.infinity_polling()