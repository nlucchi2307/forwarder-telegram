import os
import datetime
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
source_chat = os.getenv("SOURCE_CHAT")
target_chats = os.getenv("TARGET_CHATS").split(",")  # separa con virgole
target_user_id = int(os.getenv("TARGET_USER_ID"))

client = TelegramClient('forwarder_session', api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    sender = await event.get_sender()
    if sender.id == target_user_id:
        for chat in target_chats:
            try:
                await event.forward_to(chat)
                print(f"[{datetime.datetime.now()}] Inoltrato a {chat}: {event.text[:50]}")
            except Exception as e:
                print(f"Errore inoltro a {chat}: {e}")

client.start()
print("✅ Forwarder avviato e in ascolto...")
client.run_until_disconnected()
