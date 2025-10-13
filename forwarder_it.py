import os
import datetime
import re
from telethon import TelegramClient, events

# config
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Canale di origine
source_chat = os.getenv("SOURCE_CHAT")

# Canali di destinazione
target_chats = [x.strip() for x in os.getenv("TARGET_CHATS").split(",")]

# ID degli utenti da monitorare
target_user_ids = [int(uid.strip()) for uid in os.getenv("TARGET_USER_IDS").split(",")]

# Parole chiave 
keywords = [k.strip().lower() for k in os.getenv("KEYWORDS").split(",")]


client = TelegramClient('forwarder_session', api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    sender = await event.get_sender()
    sender_id = sender.id if sender else None
    text = event.raw_text.lower() if event.raw_text else ""

    # Controlla se il messaggio viene da uno degli utenti target
    if sender_id in target_user_ids:
        #  Controlla se contiene almeno una parola chiave (match parziale)
        if any(re.search(rf'\b{k}\w*', text) for k in keywords):
            for chat in target_chats:
                try:
                    # Reinvia il messaggio 
                    await client.send_message(
                        chat,
                        message=event.message,
                        file=event.message.media  # include foto etc
                    )

                    tipo_media = " Media" if event.message.media else " Testo"
                    print(f"[{datetime.datetime.now()}] {tipo_media} inviato da {sender_id} → {chat}")
                except Exception as e:
                    print(f"[{datetime.datetime.now()}]  Errore invio a {chat}: {e}")
        else:
            print(f"[{datetime.datetime.now()}] Ignorato (nessuna keyword): {event.text[:60]}")
    else:
        print(f"[{datetime.datetime.now()}] Ignorato (mittente {sender_id} non monitorato)")


client.start()
print("Forwarder attivo ...")
client.run_until_disconnected()
