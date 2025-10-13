import os
import datetime
import re
from telethon import TelegramClient, events

# config
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Canale di origine 
source_chat = os.getenv("SOURCE_CHAT_USER")

# Canali di destinazione 
target_chats = [x.strip() for x in os.getenv("TARGET_CHATS_USER").split(",") if x.strip()]

# ID utenti da monitorare 
target_user_ids = [int(uid.strip()) for uid in os.getenv("TARGET_USER_IDS_USER").split(",") if uid.strip()]

# Parole chiave (trigger del forward)
keywords = [k.strip().lower() for k in os.getenv("KEYWORDS_USER").split(",") if k.strip()]

# client
client = TelegramClient('forwarder_it_session', api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    sender = await event.get_sender()
    sender_id = sender.id if sender else None
    text = event.raw_text.lower() if event.raw_text else ""

    # Controlla se il mittente è tra quelli target
    if sender_id in target_user_ids:
        # Controlla se contiene almeno una parola chiave (match parziale)
        if any(re.search(rf'\b{k}\w*', text) for k in keywords):
            for chat in target_chats:
                try:
                    # Reinvia il messaggio (testo o media)
                    await client.send_message(
                        chat,
                        message=event.message,
                        file=event.message.media  # include foto, video, documenti
                    )

                    tipo_media = " Media" if event.message.media else " Testo"
                    print(f"[{datetime.datetime.now()}] {tipo_media} inoltrato da {sender_id} → {chat}")
                except Exception as e:
                    print(f"[{datetime.datetime.now()}]  Errore invio a {chat}: {e}")
        else:
            print(f"[{datetime.datetime.now()}]  Ignorato (nessuna keyword): {event.text[:60]}")
    else:
        print(f"[{datetime.datetime.now()}]  Ignorato (mittente {sender_id} non monitorato)")

client.start()
print(" Forwarder IT attivo...")
client.run_until_disconnected()
