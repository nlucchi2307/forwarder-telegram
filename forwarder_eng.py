import os
import datetime
import re
import telethon
from telethon import TelegramClient, events

# === CONFIG ===
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# ID del gruppo principale (forum)
source_chat = int(os.getenv("SOURCE_CHAT_CHANNEL"))

# Canali di destinazione
target_chats = [x.strip() for x in os.getenv("TARGET_CHATS_CHANNEL").split(",") if x.strip()]

# Parole chiave da cercare (match parziale, case-insensitive)
keywords = [k.strip().lower() for k in os.getenv("KEYWORDS_CHANNEL").split(",") if k.strip()]

# ID del topic da monitorare (ottenuto con lo script GetForumTopics)
SIGNAL_ROOM_TOPIC_ID = int(os.getenv("SIGNAL_ROOM_TOPIC_ID", "0"))  # fallback 0 se non trovato

# === CLIENT ===
client = TelegramClient("forwarder_eng_session", api_id, api_hash)

print(f"🚀 Using Telethon version {telethon.__version__}")
print(f"🔧 Configurazione:\n  - Forum ID: {source_chat}\n  - Topic ID: {SIGNAL_ROOM_TOPIC_ID}\n  - Target chats: {target_chats}\n  - Keywords: {keywords}\n")

@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    """Gestisce i nuovi messaggi dal forum Telegram (solo Signal Room)"""

    # --- FILTRO TOPIC ---
    topic_id = None
    if event.message.reply_to and hasattr(event.message.reply_to, "forum_topic_id"):
        topic_id = event.message.reply_to.forum_topic_id
    elif hasattr(event.message, "forum_topic_id"):
        topic_id = event.message.forum_topic_id

    if topic_id is not None and topic_id != SIGNAL_ROOM_TOPIC_ID:
        # Non è il topic giusto, ignora
        return

    # --- INFO MESSAGGIO ---
    sender = await event.get_sender()
    sender_name = getattr(sender, "title", None) or getattr(sender, "username", None) or "Sconosciuto"
    sender_id = getattr(sender, "id", "N/A")
    text = (event.raw_text or "").lower().strip()

    # --- CERCA KEYWORDS ---
    matched_keywords = [k for k in keywords if k in text]

    if matched_keywords:
        # Inoltra a tutti i target
        for chat in target_chats:
            try:
                await client.send_message(
                    chat,
                    message=event.message,
                    file=event.message.media  # include media
                )
                tipo_media = "📸 Media" if event.message.media else "💬 Testo"
                print(f"[{datetime.datetime.now()}] ✅ {tipo_media} inoltrato ({sender_name} | ID {sender_id}) → {chat} | Keywords: {matched_keywords}")
            except Exception as e:
                print(f"[{datetime.datetime.now()}] ❌ Errore inoltro a {chat}: {e}")
    else:
        print(f"[{datetime.datetime.now()}] Ignorato (nessuna keyword) | Mittente: {sender_name} | ID: {sender_id}")

# === AVVIO CLIENT ===
client.start()
print(f"✅ Forwarder ENG attivo — monitorando solo il topic 'Signal Room' (ID {SIGNAL_ROOM_TOPIC_ID})...\n")
client.run_until_disconnected()
