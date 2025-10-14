import os
import datetime
import re
import asyncio
from telethon import TelegramClient, events
from pathlib import Path
import telethon

# === CONFIG ===
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

source_chat = int(os.getenv("SOURCE_CHAT_CHANNEL"))
target_chats_raw = [x.strip() for x in os.getenv("TARGET_CHATS_CHANNEL").split(",") if x.strip()]
keywords = [k.strip().lower() for k in os.getenv("KEYWORDS_CHANNEL").split(",") if k.strip()]
SIGNAL_ROOM_TOPIC_ID = int(os.getenv("SIGNAL_ROOM_TOPIC_ID", "0"))

# === PATH SESSION FILE ===
BASE_DIR = Path(__file__).resolve().parent
SESSION_FILE = BASE_DIR / "forwarder_eng_session.session"

print("📁 Working directory:", os.getcwd())
print("📂 Script directory:", BASE_DIR)
print("📄 Session file path:", SESSION_FILE)
print(f"🚀 Using Telethon version {telethon.__version__}")

# === CLIENT ===
client = TelegramClient(str(SESSION_FILE), api_id, api_hash)

async def start_client():
    await client.connect()
    if not await client.is_user_authorized():
        print("❌ Sessione non valida o scaduta! Esegui localmente per rigenerarla.")
        return False
    print("✅ Sessione caricata correttamente!")
    return True


# === RISOLUZIONE TARGETS ===
target_entities = []

async def resolve_targets():
    print("🔍 Caricamento dialoghi...")
    async for dialog in client.iter_dialogs():
        pass  # popola la cache locale
    for chat in target_chats_raw:
        try:
            if chat.startswith("-100"):
                chat = int(chat)
            entity = await client.get_entity(chat)
            target_entities.append(entity)
            print(f"✅ Target risolto: {chat} → {entity.id} ({getattr(entity, 'title', 'N/A')})")
        except Exception as e:
            print(f"❌ Errore nel risolvere {chat}: {e}")


# === EVENT HANDLER ===
@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    topic_id = getattr(event.message, "forum_topic_id", None)
    if topic_id != SIGNAL_ROOM_TOPIC_ID:
        return

    sender = await event.get_sender()
    sender_name = getattr(sender, "title", None) or getattr(sender, "username", None) or "Sconosciuto"
    sender_id = getattr(sender, "id", "N/A")
    text = (event.raw_text or "").lower().strip()

    matched = [k for k in keywords if k in text]

    if matched:
        tipo_media = "📸 Media" if event.message.media else "💬 Testo"
        for entity in target_entities:
            try:
                await client.send_message(entity, message=event.message, file=event.message.media)
                print(f"[{datetime.datetime.now()}] ✅ {tipo_media} inoltrato → {entity.id} | Mittente: {sender_name} | Keywords: {matched}")
            except Exception as e:
                print(f"[{datetime.datetime.now()}] ❌ Errore inoltro a {entity.id}: {e}")
    else:
        print(f"[{datetime.datetime.now()}] Ignorato (nessuna keyword) | Mittente: {sender_name} | ID: {sender_id}")


# === MAIN ===
async def main():
    if not await start_client():
        return
    print(f"🔧 Configurazione:\n  - Forum ID: {source_chat}\n  - Topic ID: {SIGNAL_ROOM_TOPIC_ID}\n  - Target chats: {target_chats_raw}\n  - Keywords: {keywords}\n")
    await resolve_targets()
    print(f"✅ Forwarder ENG attivo — monitorando solo il topic 'Signal Room' (ID {SIGNAL_ROOM_TOPIC_ID})...\n")
    await client.run_until_disconnected()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
