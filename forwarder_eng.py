import os
import datetime
import asyncio
from telethon import TelegramClient, events
import telethon
import re 

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
    print("🔍 Risoluzione dei target senza iterare dialoghi...")
    for chat in target_chats_raw:
        try:
            chat_id = int(chat) if chat.startswith("-100") else chat
            entity = await client.get_entity(chat_id)
            target_entities.append(entity)
            print(f"✅ Target risolto: {chat_id} → {entity.id} ({getattr(entity, 'title', 'N/A')})")
        except Exception as e:
            print(f"❌ Errore nel risolvere {chat}: {e}")


# === EVENT HANDLER ===
@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    topic_id = getattr(event.message, "forum_topic_id", None)

    # 🔧 Log debug per capire da dove arriva il messaggio
    print(f"[DEBUG] Messaggio ricevuto | topic_id={topic_id} | testo: {event.raw_text[:60]}")

    # 👉 Filtro per topic: passa solo se è None (no forum) o se è il topic giusto
    if topic_id not in (None, SIGNAL_ROOM_TOPIC_ID):
        return

    sender = await event.get_sender()
    sender_name = getattr(sender, "title", None) or getattr(sender, "username", None) or "Sconosciuto"
    text = (event.raw_text or "").lower()

    # regex più flessibile per TP / SL / ecc.
    matched = [k for k in keywords if re.search(rf'\b{k}\b', text)]

    if matched:
        for entity in target_entities:
            try:
                await client.send_message(entity, message=event.message)
                print(f"[{datetime.datetime.now()}] ✅ Inoltrato → {entity.id} | da {sender_name} | keyword: {matched}")
            except Exception as e:
                print(f"[{datetime.datetime.now()}] ❌ Errore inoltro: {e}")
    else:
        print(f"[{datetime.datetime.now()}] Ignorato (nessuna keyword) | da {sender_name}")



# === KEEP-ALIVE TASK ===
async def keep_alive():
    while True:
        print(f"[{datetime.datetime.now()}] 🟢 Bot attivo e in ascolto...")
        await asyncio.sleep(1800)  # ogni 30 minuti


# === MAIN ===
async def main():
    await start_client()
    print(f"🔧 Configurazione:\n  - Forum ID: {source_chat}\n  - Topic ID: {SIGNAL_ROOM_TOPIC_ID}\n  - Target chats: {target_chats_raw}\n  - Keywords: {keywords}\n")
    await resolve_targets()
    print(f"✅ Forwarder ENG attivo — monitorando solo il topic 'Signal Room' (ID {SIGNAL_ROOM_TOPIC_ID})...\n")

    # Avvia forwarder + keep alive in parallelo
    await asyncio.gather(
        client.run_until_disconnected(),
        keep_alive()
    )


if __name__ == "__main__":
    asyncio.run(main())
