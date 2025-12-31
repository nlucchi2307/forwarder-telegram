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

source_chat = int(os.getenv("ENG_SOURCE_CHAT"))
target_chat = int(os.getenv("ENG_TARGET_CHAT"))

# === Topic mapping sorgente → destinazione ===
mapping = {
    int(os.getenv("ENG_SIGNAL_ROOM_TOPIC_ID_SOURCE")): int(os.getenv("ENG_SIGNAL_ROOM_TOPIC_ID_TARGET")),
    int(os.getenv("ENG_ANALYSIS_TOPIC_ID_SOURCE")): int(os.getenv("ENG_SIGNAL_ROOM_TOPIC_ID_TARGET")),
    int(os.getenv("ENG_HISTORICAL_TOPIC_ID_SOURCE")): int(os.getenv("ENG_HISTORICAL_TOPIC_ID_TARGET")),
}

keywords = [k.strip() for k in os.getenv("ENG_KEYWORDS_CHANNEL").split(",") if k.strip()]

print("📁 Working directory:", os.getcwd())
print(f"🚀 Using Telethon version {telethon.__version__}")

# =========================
# NEGATIVE KEYWORDS (HARD-CODED)
# =========================
NEGATIVE_KEYWORDS = [
    "live",
    "webinar",
    "link",
    "join",
    "participate",
]

# === CLIENT ===
client = TelegramClient("forwarder_eng_bot", api_id, api_hash)

async def start_client():
    await client.start(bot_token=bot_token)
    print("✅ [ENG] Bot autenticato correttamente con token!")
    return True

# === EVENT HANDLER ===
@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    topic_id = getattr(event.message, "forum_topic_id", None)

    text = (event.raw_text or "")
    text_lower = text.lower()
    has_media = bool(event.message.media)

    # ❌ BLOCCO NEGATIVE KEYWORDS
    if any(neg in text_lower for neg in NEGATIVE_KEYWORDS):
        print(f"[ENG] 🚫 Ignorato per negative keyword | testo: {text[:80]}")
        return

    # Se il messaggio non ha topic_id, decidiamo in base al contenuto
    if topic_id is None:
        hist_markers = [
            "weekly report",
            "weekly performance",
            "october 2025",
            "november 2025",
            "december 2025",
        ]

        if any(word in text_lower for word in hist_markers):
            topic_id = int(os.getenv("ENG_HISTORICAL_TOPIC_ID_SOURCE"))
            print(f"[DEBUG ENG] Nessun topic_id ma contiene indicatori 'Historical' → assegnato topic_id={topic_id}")
        else:
            topic_id = int(os.getenv("ENG_SIGNAL_ROOM_TOPIC_ID_SOURCE"))
            print(f"[DEBUG ENG] Nessun topic_id → trattato come Signal Room ({topic_id})")

    sender = await event.get_sender()
    sender_name = getattr(sender, "title", None) or getattr(sender, "username", None) or "Sconosciuto"

    matched = [
        k for k in keywords
        if re.search(rf'(?<![a-zA-Z]){re.escape(k)}(?![a-zA-Z])', text, flags=re.IGNORECASE)
    ]

    print(f"[DEBUG ENG] Messaggio ricevuto | topic_id={topic_id} | media={has_media} | testo: {text[:80]}")

    # 🔍 Gestione inoltro in base al topic
    if topic_id not in mapping:
        print(f"[{datetime.datetime.now()}] ⚪ [ENG] Ignorato (topic {topic_id} non gestito)")
        return

    if topic_id == int(os.getenv("ENG_HISTORICAL_TOPIC_ID_SOURCE")):
        motivo = "📜 Historical (inoltro completo)"
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
        print(f"[{datetime.datetime.now()}] ✅ [ENG] Inoltrato → topic {target_topic} | {motivo}")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] ❌ [ENG] Errore inoltro: {e}")

# === KEEP-ALIVE ===
async def keep_alive():
    while True:
        print(f"[{datetime.datetime.now()}] 🟢 [ENG] Bot attivo e in ascolto...")
        await asyncio.sleep(1800)

# === MAIN ===
async def main():
    await start_client()
    print(
        f"🔧 [ENG] Configurazione:\n"
        f"  - SOURCE_CHAT: {source_chat}\n"
        f"  - TARGET_CHAT: {target_chat}\n"
        f"  - Mapping: {mapping}\n"
        f"  - Keywords: {keywords}\n"
    )
    await asyncio.gather(
        client.run_until_disconnected(),
        keep_alive()
    )

if __name__ == "__main__":
    asyncio.run(main())
