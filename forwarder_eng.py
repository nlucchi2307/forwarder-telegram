import os
import datetime
import re
from telethon import TelegramClient, events

# === CONFIG ===
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# ID del gruppo principale (forum)
source_chat = int(os.getenv("SOURCE_CHAT_CHANNEL"))

# Canali di destinazione
target_chats = [x.strip() for x in os.getenv("TARGET_CHATS_CHANNEL").split(",") if x.strip()]

# ID del mittente (canale principale)
target_entity_ids = [int(x.strip()) for x in os.getenv("TARGET_ENTITY_IDS_CHANNEL").split(",") if x.strip()]

# Parole chiave da cercare
keywords = [k.strip().lower() for k in os.getenv("KEYWORDS_CHANNEL").split(",") if k.strip()]

# ID del topic da monitorare (ottenuto con lo script GetForumTopics)
SIGNAL_ROOM_TOPIC_ID = int(os.getenv("SIGNAL_ROOM_TOPIC_ID", "0"))  # fallback 0 se non trovato

# === CLIENT ===
client = TelegramClient('forwarder_eng_session', api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    """Gestisce i nuovi messaggi dal forum Telegram"""

    # --- FILTRO TOPIC: lascia passare solo il topic 'Signal Room' ---
    topic_id = None
    if event.message.reply_to and hasattr(event.message.reply_to, "forum_topic_id"):
        topic_id = event.message.reply_to.forum_topic_id
    elif hasattr(event.message, "forum_topic_id"):
        topic_id = event.message.forum_topic_id

    if topic_id is not None and topic_id != SIGNAL_ROOM_TOPIC_ID:
        # Non è il topic giusto, ignora
        return

    # --- INFO SUL MESSAGGIO ---
    sender = await event.get_sender()
    sender_id = sender.id if sender else None
    text = event.raw_text.lower() if event.raw_text else ""

    # --- LOGICA PRINCIPALE ---
    if sender_id in target_entity_ids:
        if any(re.search(rf'\b{k}\w*', text) for k in keywords):
            for chat in target_chats:
                try:
                    await client.send_message(
                        chat,
                        message=event.message,
                        file=event.message.media  # supporta media, immagini, documenti, ecc.
                    )
                    tipo_media = "Media" if event.message.media else "Testo"
                    print(f"[{datetime.datetime.now()}] {tipo_media} inoltrato da {sender_id} → {chat}")
                except Exception as e:
                    print(f"[{datetime.datetime.now()}] ❌ Errore inoltro a {chat}: {e}")
        else:
            print(f"[{datetime.datetime.now()}] Ignorato (nessuna keyword trovata)")
    else:
        print(f"[{datetime.datetime.now()}] Ignorato (mittente non in lista)")

# === AVVIO CLIENT ===
client.start()
print(f"✅ Forwarder ENG attivo — monitorando solo il topic 'Signal Room' (ID {SIGNAL_ROOM_TOPIC_ID})...")
client.run_until_disconnected()