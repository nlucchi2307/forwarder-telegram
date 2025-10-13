import os
import datetime
import re
from telethon import TelegramClient, events

# config
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Canale di origine 
source_chat = os.getenv("SOURCE_CHAT_CHANNEL")

# Canali di destinazione 
target_chats = [x.strip() for x in os.getenv("TARGET_CHATS_CHANNEL").split(",") if x.strip()]

# ID del canale mittente (in questo caso coincide con quello di origine)
target_entity_ids = [int(x.strip()) for x in os.getenv("TARGET_ENTITY_IDS_CHANNEL").split(",") if x.strip()]

# Parole chiave da cercare nel testo (match parziale)
keywords = [k.strip().lower() for k in os.getenv("KEYWORDS_CHANNEL").split(",") if k.strip()]

# client
client = TelegramClient('forwarder_eng_session', api_id, api_hash)

@client.on(events.NewMessage(chats=source_chat))
async def handler(event):
    sender = await event.get_sender()
    sender_id = sender.id if sender else None
    text = event.raw_text.lower() if event.raw_text else ""

    # Controlla se il mittente è quello target (il canale stesso)
    if sender_id in target_entity_ids:
        # E se contiene almeno una keyword (match parziale)
        if any(re.search(rf'\b{k}\w*', text) for k in keywords):
            for chat in target_chats:
                try:
                    # Reinvia il messaggio (testo o media)
                    await client.send_message(
                        chat,
                        message=event.message,
                        file=event.message.media  # include immagini, video, documenti, ecc.
                    )

                    tipo_media = "Media" if event.message.media else " Testo"
                    print(f"[{datetime.datetime.now()}] {tipo_media} inoltrato da {sender_id} → {chat}")
                except Exception as e:
                    print(f"[{datetime.datetime.now()}] Errore inoltro a {chat}: {e}")
        else:
            print(f"[{datetime.datetime.now()}] Ignorato (nessuna keyword)")
    else:
        print(f"[{datetime.datetime.now()}] Ignorato (mittente non in lista)")

client.start()
print(" Forwarder ENG attivo...")
client.run_until_disconnected()
