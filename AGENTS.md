# Finn

Telegram bot for financial control. All UI strings are **Brazilian Portuguese**.

## Run

```bash
docker compose up -d db bot   # PostgreSQL + bot
docker compose up -d db       # PostgreSQL only (local dev)
python -m bot.main            # run bot directly (needs .env, DB running)
```

- Bot waits for DB healthcheck (`depends_on: db: condition: service_healthy`)
- `init.sql` auto-runs on first DB startup
- Timezone: `America/Sao_Paulo`

## Config (.env)

```
BOT_TOKEN=<token>
DB_HOST=localhost            # use "db" when running inside Docker
DB_PORT=5432 / DB_NAME=finn / DB_USER=finn / DB_PASSWORD=finn
ALLOWED_USER_IDS=1401845586  # comma-separated Telegram user IDs
OLLAMA_HOST=http://localhost:11434  # use "http://ollama:11434" in Docker
OLLAMA_MODEL=qwen2.5:0.5b
```

`bot/config.py` calls `load_dotenv()` at import time.

## Architecture

- **Entrypoint**: `python -m bot.main`
- **Polling** with `drop_pending_updates=True`
- **DB**: `psycopg2.pool.SimpleConnectionPool` (1-10) via `bot/database.py`
  - `database.py` reads env vars via `os.getenv()` **independently** from `config.py` — changes in one don't affect the other
  - All query helpers live in `bot/repository.py`
- **AI**: Ollama integration via `bot/ai.py`
  - Interprets informal messages (e.g., "gastei 50 no almoço")
  - Returns structured JSON for confirmation before saving
  - Model: `qwen2.5:0.5b` (lightweight, runs on CPU)

## Gotchas

- **Callback handlers bypass auth**: `CALLBACKS` in `main.py:42-43` are registered **without** the `restricted` wrapper. Only `COMMANDS` dict entries and the catch-all `MessageHandler` are protected. This means any Telegram user can trigger `gasto_callback` / `bancos_callback` if they guess the callback data.
- **`ping` is undocumented**: present in `COMMANDS` dict but missing from the `BotCommand` list in `post_init()` — won't appear in Telegram's bot menu.
- **`repository.py` commit behavior varies**: `_fetch` does NOT commit (read-only). `_fetch_one`, `_execute`, and `_insert` all call `commit()` (and `rollback()` on error). New query helpers should follow the same pattern.
- **No tests, linting, or typechecking** are configured.

## Adding a command

1. Create `bot/handlers/<name>.py`
2. Add handler + entry in `COMMANDS`/`CALLBACKS` dict in `bot/handlers/__init__.py`
3. Add `BotCommand` entry in `post_init()` in `bot/main.py`

## Tech stack

- Python 3.11, `python-telegram-bot==21.6`, `psycopg2-binary`, `python-dotenv`
- PostgreSQL 15 (Alpine), Docker Compose
