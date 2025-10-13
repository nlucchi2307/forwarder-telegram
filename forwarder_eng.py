import os
import datetime
from telethon import TelegramClient, events
import re 

# config
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
source_chat = os.getenv("SOURCE_CHAT")
target_chats = [x.strip() for x in os.getenv("TARGET_CHATS").split(",")]

target_entity_ids = [int(x.strip()) for x in os.getenv("TARGET_ENTITY_IDS").split(",")]
keywords = [k.strip().lower() for k in os.getenv("KEYWORDS").split(",")]

# client
client = TelegramClient('forwarder_session', api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    sender = await event.get_sender()
    sender_id = sender.id if sender else None
    text = event.raw_text.lower() if event.raw_text else ""

    # controlla se il mittente è tra quelli target
    if sender_id in target_entity_ids:
        # e se contiene almeno una keyword  #(k in text for k in keywords)
        if any(re.search(rf'\b{k}\w*', text) for k in keywords):
            for chat in target_chats:
                try:
                    # inoltra tutto il messaggio
                    await client.send_message(
                        chat,
                        message=event.message,
                        file=event.message.media  # include foto etc
                    )

                    # log più dettagliato
                    tipo_media = " Media" if event.message.media else "Testo"
                    print(f"[{datetime.datetime.now()}] {tipo_media} inoltrato da {sender_id} a {chat}")
                except Exception as e:
                    print(f"[{datetime.datetime.now()}] Errore inoltro a {chat}: {e}")
        else:
            print(f"[{datetime.datetime.now()}] Ignorato (nessuna keyword)")
    else:
        print(f"[{datetime.datetime.now()}] Ignorato (mittente non in lista)")

client.start()
print("Forwarder attivo...")
client.run_until_disconnected()
