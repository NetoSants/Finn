# Finn

Bot do Telegram + Dashboard web para controle financeiro pessoal.

## Funcionalidades

- **Bot Telegram**: registre gastos e rendas, veja extratos, saldos, resumo mensal, metas, parcelas, exporte CSV
- **Dashboard web**: graficos, heatmap de gastos, faturas em aberto, CRUD completo, fixos (recorrentes)
- **Multi-banco**: suporte a varios bancos/contas, cada um com saldo proprio
- **Credito**: gastos no cartao de credito com dia de fechamento e faturas agrupadas
- **Metas**: defina limite mensal por categoria e acompanhe o progresso
- **Parcelas**: divida gastos em ate 12x com lancamento automatico mensal
- **Tudo local**: PostgreSQL, zero dependencia externa (sem SaaS, sem nuvem)

## Requisitos

- Docker e Docker Compose
- Token do [@BotFather](https://t.me/BotFather) no Telegram

## Setup rapido

```bash
# 1. Clone
git clone https://github.com/NetoSants/Finn.git
cd Finn

# 2. Crie o .env
cp .env.example .env
# Edite BOT_TOKEN e ALLOWED_USER_IDS

# 3. Suba tudo
docker compose up -d
```

O bot inicia em segundos. O dashboard fica em `http://localhost:8000`.

## Config (.env)

```
BOT_TOKEN=<token do BotFather>
DB_HOST=db                    # "localhost" quando rodar fora do Docker
DB_PORT=5432
DB_NAME=finn
DB_USER=finn
DB_PASSWORD=finn
ALLOWED_USER_IDS=1401845586   # IDs Telegram separados por virgula
```

## Comandos do bot

| Comando | Descricao |
|---------|-----------|
| `/gasto` | Registrar um gasto (valor, descricao, categoria, forma de pagamento, banco) |
| `/renda` | Registrar uma renda |
| `/extrato` | Extrato do mes atual ou de um mes especifico |
| `/saldo` | Saldo atual de todos os bancos |
| `/resumo` | Resumo do mes: total gasto, total renda, maior gasto, saldo |
| `/metas` | Ver e gerenciar limites mensais por categoria |
| `/categorias` | Listar categorias e totais do mes |
| `/bancos` | Gerenciar bancos/contas (saldo inicial, cor, tipo) |
| `/exportar` | Exportar transacoes como CSV |
| `/parcelas` | Ver parcelas ativas |
| `/ping` | Verificar se o bot esta online |

## Dashboard web

Acesse `http://localhost:8000` apos subir o container.

| Pagina | Descricao |
|--------|-----------|
| **Dashboard** | Visao geral: stats com gradiente, heatmap, faturas em aberto, progresso de metas, grafico donut de categorias, grafico de barras diario, transacoes recentes |
| **Transacoes** | Lista completa com filtro por tipo (gasto/renda), paginacao, excluir com um clique |
| **Categorias** | Grid com total gasto por categoria + barra de progresso |
| **Bancos** | Cards com efeito skeuomorphic de cartao de credito, saldo, cor dinamica |
| **Metas** | Aneis de progresso SVG, status ("no limite", "ultrapassou"), editar/excluir |
| **Fixos** | Gastos e rendas recorrentes com toggle ativar/desativar, excluir |

## Stack

- Python 3.11, `python-telegram-bot==21.6`, `psycopg2-binary`, `python-dotenv`
- PostgreSQL 15 (Alpine)
- FastAPI + Jinja2 + Tailwind CDN + Chart.js + Lucide icons
- Docker Compose

## Arquitetura

```
Telegram <--> bot/main.py (polling)
                 |
          bot/handlers/ (comandos e callbacks)
                 |
          bot/repository.py (SQL)
                 |
          PostgreSQL (db:5432)

Navegador <--> web/app.py (FastAPI, port 8000)
                   |
            web/templates/ (Jinja2)
```

- O bot usa `python-telegram-bot` com polling e `drop_pending_updates=True`
- Pool de conexoes: `psycopg2.pool.SimpleConnectionPool` (1-10)
- Acesso restrito por `ALLOWED_USER_IDS` em todos os comandos e mensagens
- Migrations rodam automaticamente na inicializacao do bot
- Nao ha testes, linting ou typechecking configurados

## Estrutura

```
.
├── bot/
│   ├── main.py           # Entrypoint do bot (polling)
│   ├── config.py         # Variaveis de ambiente (dotenv)
│   ├── database.py       # Pool de conexoes PostgreSQL
│   ├── repository.py     # Queries SQL helpers
│   ├── decorators.py     # Decorator de restricao de acesso
│   ├── utils.py          # Utilitarios de formatacao
│   ├── migrations.py     # Migrations automaticas (rodam no startup)
│   └── handlers/         # Comandos e callbacks do Telegram
│       ├── __init__.py   # Registro de COMMANDS e CALLBACKS
│       ├── gasto.py      # Fluxo completo de registro de gasto
│       ├── renda.py      # Fluxo completo de registro de renda
│       ├── extrato.py    # Extrato mensal
│       ├── saldo.py      # Saldo dos bancos
│       ├── resumo.py     # Resumo mensal
│       ├── metas.py      # Gerenciamento de metas
│       ├── categorias.py # Listagem de categorias
│       ├── bancos.py     # Gerenciamento de bancos (fluxo conversacional)
│       ├── parcelas.py   # Listagem de parcelas ativas
│       ├── exportar.py   # Exportacao CSV
│       ├── help.py       # Ajuda do bot (fallback EN)
│       ├── ajuda.py      # Ajuda em PT-BR com menu interativo
│       ├── menu.py       # Menu principal com botoes inline
│       ├── confirmacao.py# Utilitario de confirmacao (sim/nao)
│       ├── generic.py    # Fallback para mensagens desconhecidas
│       ├── meta.py       # Handler antigo de metas (convivencia)
│       └── start.py      # Comando /start
├── web/
│   ├── app.py            # FastAPI + Jinja2 templates
│   ├── main.py           # Uvicorn entrypoint (port 8000)
│   └── templates/        # Paginas do dashboard
│       ├── base.html     # Layout base com sidebar e dark mode
│       ├── dashboard.html# Visao geral com graficos e heatmap
│       ├── transacoes.html# Lista de transacoes com filtros
│       ├── categorias.html# Grid de categorias com totais
│       ├── bancos.html   # Cards estilo cartao de credito
│       ├── metas.html    # Aneis de progresso SVG
│       └── fixos.html    # Gastos/rendas recorrentes
├── .opencode/
│   └── command/
│       └── cleanup.md    # Comando de auditoria para opencode
├── init.sql              # Schema inicial do banco
├── docker-compose.yml    # db + bot + web
├── .env.example          # Template de configuracao
├── AGENTS.md             # Contexto para o opencode
└── README.md
```

## Deploy (servidor remoto)

O deploy e feito via SCP para o servidor Debian:

```bash
# Build local e envie
docker compose build
scp -r . debmine@10.249.146.90:finn/

# No servidor
ssh debmine@10.249.146.90
cd finn
docker compose up -d --build
```

## Desenvolvimento local

```bash
# So o banco (para rodar o bot direto)
docker compose up -d db

# Bot direto (precisa de .env com DB_HOST=localhost)
python -m bot.main

# Web direto
python -m web.main
```

Portas: bot usa polling (sem porta fixa), web na `8000`, PostgreSQL na `5432`.
