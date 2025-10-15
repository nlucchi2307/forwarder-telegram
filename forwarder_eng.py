import os
import datetime
import asyncio
from telethon import TelegramClient, events
import telethon

# === CONFIG ===
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

source_chat = int(os.getenv("SOURCE_CHAT_CHANNEL"))
target_chats_raw = [x.strip() for x in os.getenv("TARGET_CHATS_CHANNEL").split(",") if x.strip()]
keywords = [k.strip().lower() for k in os.getenv("KEYWORDS_CHANNEL").split(",") if k.strip()]
SIGNAL_ROOM_TOPIC_ID = int(os.getenv("SIGNAL_ROOM_TOPIC_ID", "0"))

print("📁 Working directory:", os.getcwd())
print(f"🚀 Using Telethon version {telethon.__version__}")

# === CLIENT ===
client = TelegramClient("forwarder_bot", api_id, api_hash)

async def start_client():
    await client.start(bot_token=bot_token)
    print("✅ Bot autenticato correttamente con token!")
    return True


# === RISOLUZIONE TARGETS ===
target_entities = []

async def resolve_targets():
    print("🔍 Caricamento dialoghi...")
    async for dialog in client.iter_dialogs():
        pass  # Popola la cache locale
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


# === KEEP-ALIVE TASK ===
async def keep_alive():
    while True:
        print(f"[{datetime.datetime.now()}] 🟢 Bot attivo e in ascolto...")
        await asyncio.sleep(1800)  # 30 minuti


# === MAIN ===
async def main():
    await start_client()
    print(f"🔧 Configurazione:\n  - Forum ID: {source_chat}\n  - Topic ID: {SIGNAL_ROOM_TOPIC_ID}\n  - Target chats: {target_chats_raw}\n  - Keywords: {keywords}\n")
    await resolve_targets()
    print(f"✅ Forwarder ENG attivo — monitorando solo il topic 'Signal Room' (ID {SIGNAL_ROOM_TOPIC_ID})...\n")

    # Avvio in parallelo di forwarder e keep_alive
    await asyncio.gather(
        client.run_until_disconnected(),
        keep_alive()
    )


# === ENTRY POINT ===
if __name__ == "__main__":
    asyncio.run(main())