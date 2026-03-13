# Obsidian RAG Agent

Локальный AI-ассистент для Obsidian vault. Отвечает на вопросы по твоим заметкам, находит связи между ними и напоминает о давно забытых записях — всё через Telegram.

![demo](screenshots/demo.jpg)

## Возможности

- `/ask [вопрос]` — задать вопрос по базе знаний
- `/connections [файл.md]` — найти тематически связанные заметки
- `/stale` — показать заметки которые давно не редактировались
- `/new` — создать новую заметку прямо из Telegram
- `/reindex` — обновить индекс после изменений в vault
- Ежедневные напоминания о старых заметках

## Стек

| Компонент | Технология |
|---|---|
| Эмбеддинги | sentence-transformers (all-MiniLM-L6-v2) |
| Векторная БД | ChromaDB |
| LLM | llama.cpp (локально) или ollama |
| Telegram бот | aiogram 3 |
| Планировщик | APScheduler |

## Установка

**1. Клонировать репозиторий**
```bash
git clone https://github.com/Winki222/Obludian
cd obsidian-agent
```

**2. Создать виртуальное окружение**
```bash
# Linux / macOS / Termux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

**3. Установить зависимости**
```bash
pip install -r requirements.txt
```

**4. Настроить config.json**
```bash
cp config.example.json config.json
```
Заполни поля:
- `vault_path` — путь к папке Obsidian vault
- `bot_token` — токен от @BotFather
- `my_id` — твой Telegram ID (узнай у @userinfobot)
- `gguf_path` — путь к .gguf модели

**5. Проиндексировать заметки**
```bash
python -c "from core.config import load_config; from core.indexer import Indexer; Indexer(load_config()).index()"
```

**6. Запустить бота**
```bash
python -m bot.bot
```

## 📱 Termux (Android)

```bash
pkg update && pkg install python
termux-setup-storage
pip install -r requirements.txt
```
Vault должен находиться в `/sdcard/`. Добавь `termux-wake-lock` в скрипт запуска чтобы бот не засыпал.

## ⚙️ Структура проекта

```
obsidian-agent/
├── config.json          # настройки (не в git!)
├── config.example.json  # пример настроек
├── core/
│   ├── config.py        # загрузка конфига
│   ├── indexer.py       # индексация заметок
│   ├── retriever.py     # поиск по смыслу
│   ├── llm.py           # локальная LLM
│   └── agent.py         # логика агента
└── bot/
    ├── bot.py           # точка входа
    ├── handlers.py      # команды бота
    └── scheduler.py     # напоминания
```

## 🔒 Безопасность

Бот отвечает только на сообщения от твоего Telegram ID. Все данные хранятся локально — никаких облаков.


