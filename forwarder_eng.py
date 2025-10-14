import os
import datetime
import re
import telethon
from telethon import TelegramClient, events
import pathlib

# === CONFIG ===
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# ID del forum sorgente
source_chat = int(os.getenv("SOURCE_CHAT_CHANNEL"))

# Canali di destinazione (ID numerici o @username)
target_chats_raw = [x.strip() for x in os.getenv("TARGET_CHATS_CHANNEL").split(",") if x.strip()]

# Keywords da cercare
keywords = [k.strip().lower() for k in os.getenv("KEYWORDS_CHANNEL").split(",") if k.strip()]

# ID del topic (Signal Room)
SIGNAL_ROOM_TOPIC_ID = int(os.getenv("SIGNAL_ROOM_TOPIC_ID", "0"))

# === CLIENT ===
session_path = str(pathlib.Path(__file__).parent / "forwarder_eng_session")
client = TelegramClient(session_path, api_id, api_hash)

print(f"🚀 Using Telethon version {telethon.__version__}")
print(f"🔧 Configurazione:\n  - Forum ID: {source_chat}\n  - Topic ID: {SIGNAL_ROOM_TOPIC_ID}\n  - Target chats: {target_chats_raw}\n  - Keywords: {keywords}\n")

# === SETUP ENTITÀ DESTINAZIONE ===
target_entities = []

async def resolve_targets():
    print("🔍 Caricamento dialoghi...")
    async for dialog in client.iter_dialogs():
        pass  # serve solo a popolare la cache locale

    for chat in target_chats_raw:
        try:
            # Se è un ID numerico, converti in int
            if chat.startswith("-100"):
                chat = int(chat)
            entity = await client.get_entity(chat)
            target_entities.append(entity)
            print(f"✅ Target risolto: {chat} → {entity.id} ({getattr(entity, 'title', 'N/A')})")
        except Exception as e:
            print(f"❌ Errore nel risolvere {chat}: {e}")


@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    """Gestisce nuovi messaggi nel forum (solo topic Signal Room)"""

    # --- Filtro topic ---
    topic_id = None
    if event.message.reply_to and hasattr(event.message.reply_to, "forum_topic_id"):
        topic_id = event.message.reply_to.forum_topic_id
    elif hasattr(event.message, "forum_topic_id"):
        topic_id = event.message.forum_topic_id

    if topic_id is not None and topic_id != SIGNAL_ROOM_TOPIC_ID:
        return  # non è il topic giusto

    # --- Info messaggio ---
    sender = await event.get_sender()
    sender_name = getattr(sender, "title", None) or getattr(sender, "username", None) or "Sconosciuto"
    sender_id = getattr(sender, "id", "N/A")
    text = (event.raw_text or "").lower().strip()

    # --- Keywords ---
    matched = [k for k in keywords if k in text]

    if matched:
        tipo_media = "📸 Media" if event.message.media else "💬 Testo"
        for entity in target_entities:
            try:
                await client.send_message(
                    entity,
                    message=event.message,
                    file=event.message.media
                )
                print(f"[{datetime.datetime.now()}] ✅ {tipo_media} inoltrato → {entity.id} | Mittente: {sender_name} | Keywords: {matched}")
            except Exception as e:
                print(f"[{datetime.datetime.now()}] ❌ Errore inoltro a {entity.id}: {e}")
    else:
        print(f"[{datetime.datetime.now()}] Ignorato (nessuna keyword) | Mittente: {sender_name} | ID: {sender_id}")

# === AVVIO CLIENT ===
async def main():
    await resolve_targets()
    print(f"✅ Forwarder ENG attivo — monitorando solo il topic 'Signal Room' (ID {SIGNAL_ROOM_TOPIC_ID})...\n")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
