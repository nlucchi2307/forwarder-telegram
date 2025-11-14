# 🚀 Telegram Forwarder Bot t

Bot Telegram basato su **Telethon**, progettato per inoltrare automaticamente messaggi da un canale/gruppo sorgente verso uno di destinazione, mantenendo i **topic (forum)** e applicando un filtro tramite **keywords**, **media**, e categorie speciali (*Historical*).

Ottimizzato per il deployment su **Railway**.

---

## ✨ Funzionalità

- 📡 Forward automatico messaggi
- 🗂 Supporto completo ai **topic forum** (topic source → topic target)
- 🔍 Filtro intelligente:
  - Inoltra se contiene **keywords**
  - Inoltra se contiene **media**
  - Inoltra sempre i messaggi proveniente da un determinato topic, e diretti ad uno specifico. 
- 🧠 Auto-detection topic quando assente
- 🟢 Keep-alive per Railway
- 🛠 Log dettagliati per debugging

---

## 🧩 Variabili d'Ambiente

Poiché il file `.env` non può essere reso pubblico su Railway, le variabili devono essere configurate manualmente nella sezione **Variables** del progetto.

> ⚠️ **Importante:** assicurarsi che tutti i valori siano corretti per evitare errori di connessione o autorizzazione.

---

## 🚀 Deployment su Railway

- 📄 Il file **Procfile** specifica il comando di avvio del servizio  
- 🔧 Railway esegue il bot automaticamente ad ogni build  
- 📡 Il bot rimane online grazie al sistema di logging continuo e alla funzione di keep-alive  

---



