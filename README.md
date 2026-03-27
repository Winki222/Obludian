```markdown
# Obsidian RAG Agent

A local AI assistant for your Obsidian vault. Answers questions about your notes,
finds connections between them, and reminds you about long-forgotten entries — all via Telegram.

## Features

- `/ask [question]` — query your knowledge base
- `/connections [file.md]` — find thematically related notes
- `/stale` — show notes that haven't been edited in a while
- `/new` — create a new note directly from Telegram
- `/reindex` — rebuild the index after changes to your vault
- Daily reminders about old notes

## Stack

| Component     | Technology                              |
|---------------|-----------------------------------------|
| Embeddings    | sentence-transformers (all-MiniLM-L6-v2)|
| Vector DB     | ChromaDB                                |
| LLM           | llama.cpp (local) or ollama             |
| Telegram bot  | aiogram 3                               |
| Scheduler     | APScheduler                             |

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/Winki222/Obludian
cd obsidian-agent
```

**2. Create a virtual environment**
```bash
# Linux / macOS / Termux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure config.json**
```bash
cp config.example.json config.json
```

Fill in the fields:
- `vault_path` — path to your Obsidian vault folder
- `bot_token` — token from @BotFather
- `my_id` — your Telegram ID (get it from @userinfobot)
- `gguf_path` — path to your `.gguf` model file

**5. Index your notes**
```bash
python -c "from core.config import load_config; from core.indexer import Indexer; Indexer(load_config()).index()"
```

**6. Run the bot**
```bash
python -m bot.bot
```

## 📱 Termux (Android)

```bash
pkg update && pkg install python
termux-setup-storage
pip install -r requirements.txt
```

Your vault should be located in `/sdcard/`. Add `termux-wake-lock` to your startup
script to prevent the bot from sleeping.

## ⚙️ Project Structure

```
obsidian-agent/
├── config.json          # your config (not in git!)
├── config.example.json  # example config
├── core/
│   ├── config.py        # config loader
│   ├── indexer.py       # note indexer
│   ├── retriever.py     # semantic search
│   ├── llm.py           # local LLM
│   └── agent.py         # agent logic
└── bot/
    ├── bot.py           # entry point
    ├── handlers.py      # bot commands
    └── scheduler.py     # reminders
```

## 🔒 Privacy

The bot only responds to messages from your Telegram ID.
All data is stored locally — no cloud involved.
```
