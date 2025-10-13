import os
import datetime
import re
from telethon import TelegramClient, events
from telethon.tl.types import Message


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

# ID del topic da monitorare (da impostare dopo averlo trovato)
SIGNAL_ROOM_TOPIC_ID = int(os.getenv("SIGNAL_ROOM_TOPIC_ID", "0"))  # fallback 0

# === CLIENT ===
client = TelegramClient('forwarder_eng_session', api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat))
async def handler(event: Message):
    # Se il gruppo è un forum, filtra solo il topic giusto
    if event.is_forum and event.reply_to and event.reply_to.forum_topic_id != SIGNAL_ROOM_TOPIC_ID:
        return  # ignora i messaggi degli altri topic

    sender = await event.get_sender()
    sender_id = sender.id if sender else None
    text = event.raw_text.lower() if event.raw_text else ""

    if sender_id in target_entity_ids:
        if any(re.search(rf'\b{k}\w*', text) for k in keywords):
            for chat in target_chats:
                try:
                    await client.send_message(
                        chat,
                        message=event.message,
                        file=event.message.media
                    )
                    tipo_media = "Media" if event.message.media else "Testo"
                    print(f"[{datetime.datetime.now()}] {tipo_media} inoltrato da {sender_id} → {chat}")
                except Exception as e:
                    print(f"[{datetime.datetime.now()}] Errore inoltro a {chat}: {e}")
        else:
            print(f"[{datetime.datetime.now()}] Ignorato (nessuna keyword)")
    else:
        print(f"[{datetime.datetime.now()}] Ignorato (mittente non in lista)")

client.start()
print("✅ Forwarder ENG attivo (solo topic Signal Room)...")
client.run_until_disconnected()