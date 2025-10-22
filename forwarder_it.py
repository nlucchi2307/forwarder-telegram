import os
import datetime
import asyncio
import re
from telethon import TelegramClient, events
import telethon

# === CONFIG ===
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

source_chat = int(os.getenv("IT_SOURCE_CHAT"))
target_chat = int(os.getenv("IT_TARGET_CHAT"))

# === Topic mapping sorgente → destinazione ===
mapping = {
    int(os.getenv("IT_SALA_ORO_TOPIC_ID_SOURCE")): int(os.getenv("IT_SIGNAL_ROOM_TOPIC_ID_TARGET")),
    int(os.getenv("IT_ANALISI_TOPIC_ID_SOURCE")): int(os.getenv("IT_SIGNAL_ROOM_TOPIC_ID_TARGET")),
    int(os.getenv("IT_STORICO_SALA_TOPIC_ID_SOURCE")): int(os.getenv("IT_HISTORICAL_TOPIC_ID_TARGET")),
}

keywords = [k.strip() for k in os.getenv("IT_KEYWORDS_CHANNEL").split(",") if k.strip()]

print("📁 Working directory:", os.getcwd())
print(f"🚀 Using Telethon version {telethon.__version__}")

# === CLIENT ===
client = TelegramClient("forwarder_it_bot", api_id, api_hash)

async def start_client():
    await client.start(bot_token=bot_token)
    print("✅ [IT] Bot autenticato correttamente con token!")
    return True

# === EVENT HANDLER ===
@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    topic_id = getattr(event.message, "forum_topic_id", None)
    sender = await event.get_sender()
    sender_name = getattr(sender, "title", None) or getattr(sender, "username", None) or "Sconosciuto"
    text = (event.raw_text or "")
    has_media = bool(event.message.media)

    matched = [
        k for k in keywords
        if re.search(rf'(?<![a-zA-Z]){re.escape(k)}(?![a-zA-Z])', text, flags=re.IGNORECASE)
    ]

    print(f"[DEBUG IT] Messaggio ricevuto | topic_id={topic_id} | media={has_media} | testo: {text[:80]}")

    if topic_id not in mapping:
        print(f"[{datetime.datetime.now()}] ⚪ [IT] Ignorato (topic {topic_id} non gestito)")
        return

    # Se viene da Storico → inoltra tutto
    if topic_id == int(os.getenv("IT_STORICO_SALA_TOPIC_ID_SOURCE")):
        motivo = "📜 Storico (inoltro completo)"
        do_forward = True
    else:
        do_forward = bool(matched or has_media)
        motivo = "📸 Media" if has_media else f"🔑 Keywords: {matched}" if matched else "🚫 Ignorato"

    if not do_forward:
        print(f"[{datetime.datetime.now()}] Ignorato (nessuna keyword/media) | da {sender_name}")
        return

    target_topic = mapping[topic_id]
    try:
        await client.send_message(
            entity=target_chat,
            message=event.message,
            reply_to=target_topic
        )
        print(f"[{datetime.datetime.now()}] ✅ [IT] Inoltrato → topic {target_topic} | {motivo}")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] ❌ [IT] Errore inoltro: {e}")

# === KEEP-ALIVE ===
async def keep_alive():
    while True:
        print(f"[{datetime.datetime.now()}] 🟢 [IT] Bot attivo e in ascolto...")
        await asyncio.sleep(1800)

# === MAIN ===
async def main():
    await start_client()
    print(f"🔧 [IT] Configurazione:\n  - SOURCE_CHAT: {source_chat}\n  - TARGET_CHAT: {target_chat}\n  - Mapping: {mapping}\n  - Keywords: {keywords}\n")
    await asyncio.gather(
        client.run_until_disconnected(),
        keep_alive()
    )

if __name__ == "__main__":
    asyncio.run(main())
