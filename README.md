# Finn

Bot do Telegram + Dashboard web para controle financeiro pessoal.

## Funcionalidades

- **Bot Telegram**: `/gasto`, `/renda`, `/extrato`, `/saldo`, `/resumo`, `/metas`, `/categorias`, `/bancos`, `/exportar`, `/parcelas`
- **Dashboard web**: graficos, heatmap, faturas, fixos, CRUD completo
- **Faturas em aberto**: gastos no credito agrupados por banco
- **Fixos**: gastos/rendas recorrentes (web-only)
- **Tudo local**: PostgreSQL, sem dependencia externa

## Como rodar

```bash
# Tudo (DB + bot + web)
docker compose up -d

# So PostgreSQL (dev local)
docker compose up -d db

# Rodar direto (precisa de .env + DB rodando)
python -m bot.main
python -m web.main
```

## Config (.env)

```
BOT_TOKEN=<token do BotFather>
DB_HOST=localhost            # use "db" quando rodar no Docker
DB_PORT=5432
DB_NAME=finn
DB_USER=finn
DB_PASSWORD=finn
ALLOWED_USER_IDS=1401845586  # IDs de Telegram separados por virgula
```

## Stack

- Python 3.11, `python-telegram-bot==21.6`, `psycopg2-binary`, `python-dotenv`
- PostgreSQL 15 (Alpine)
- FastAPI + Jinja2 + Tailwind CDN + Chart.js + Lucide icons
- Docker Compose

## Estrutura

```
bot/
  main.py           # Entrypoint do bot (polling)
  config.py         # Variaveis de ambiente
  database.py       # Pool de conexoes PostgreSQL
  repository.py     # Queries SQL
  decorators.py     # Restricao de acesso
  utils.py          # Formatacao
  migrations.py     # Migrations automaticas
  handlers/         # Comandos e callbacks do Telegram
web/
  app.py            # FastAPI + Jinja2 templates
  templates/        # Paginas do dashboard
    base.html
    dashboard.html
    transacoes.html
    categorias.html
    bancos.html
    metas.html
    fixos.html
init.sql            # Schema inicial do banco
docker-compose.yml  # db + bot + web
```
