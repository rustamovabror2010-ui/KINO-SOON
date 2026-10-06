import telebot, json, os

TOKEN = os.environ["TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])

bot = telebot.TeleBot(TOKEN)
FILE = os.environ.get("DATA_PATH", "movies.json")

def load():
    if os.path.exists(FILE):
        with open(FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False)

movies = load()

def is_admin(m):
    return m.from_user.id == ADMIN_ID

@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m, "Salom! Kino kodini yuboring.")

@bot.message_handler(commands=["list"], func=is_admin)
def list_movies(m):
    if not movies:
        return bot.reply_to(m, "Kinolar yo'q.")
    text = "\n".join(f"{c} — {v['name']}" for c, v in movies.items())
    bot.reply_to(m, text)

@bot.message_handler(commands=["del"], func=is_admin)
def delete(m):
    parts = m.text.split()
    if len(parts) < 2 or parts[1] not in movies:
        return bot.reply_to(m, "Ishlatish: /del 101")
    del movies[parts[1]]
    save()
    bot.reply_to(m, "O'chirildi.")

@bot.message_handler(content_types=["video", "document"], func=is_admin)
def add_movie(m):
    cap = (m.caption or "").strip()
    if not cap:
        return bot.reply_to(m, "Izohga kod va nom yozing: 101 Kino nomi")
    code, _, name = cap.partition(" ")
    file_id = m.video.file_id if m.content_type == "video" else m.document.file_id
    movies[code] = {"file_id": file_id, "type": m.content_type, "name": name or code}
    save()
    bot.reply_to(m, f"Qo'shildi: {code}")

@bot.message_handler(content_types=["text"])
def get_movie(m):
    code = m.text.strip()
    movie = movies.get(code)
    if not movie:
        return bot.reply_to(m, "Bunday kod topilmadi.")
    if movie["type"] == "video":
        bot.send_video(m.chat.id, movie["file_id"], caption=movie["name"])
    else:
        bot.send_document(m.chat.id, movie["file_id"], caption=movie["name"])

bot.infinity_polling()
