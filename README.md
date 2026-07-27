# Finn

Bot do Telegram para controle financeiro pessoal, com interpretação via IA local (Ollama).

## Funcionalidades

- **/gasto** — Registra gastos via formulário (valor, descrição, pagamento)
- **/renda** — Registra receitas via formulário
- **/gastos** — Lista gastos do mês (com paginação)
- **/rendas** — Lista receitas do mês (com paginação)
- **/extrato** — Extrato completo (gastos + rendas)
- **/bancos** — Gerencia categorias (bancos/cartões)
- **/ajuda** — Lista todos os comandos
- **Mensagem livre** — Digite algo como "gastei 50 no almoço" e a IA interpreta automaticamente

## Como rodar

```bash
# PostgreSQL + Bot
docker compose up -d db bot

# Só PostgreSQL (dev local)
docker compose up -d db

# Rodar direto (precisa de .env + DB rodando)
python -m bot.main
```

## Configuração (.env)

```
BOT_TOKEN=<token do BotFather>
DB_HOST=localhost            # use "db" quando rodar no Docker
DB_PORT=5432
DB_NAME=finn
DB_USER=finn
DB_PASSWORD=finn
ALLOWED_USER_IDS=1401845586  # IDs de Telegram separados por vírgula
OLLAMA_HOST=http://localhost:11434  # use "http://ollama:11434" no Docker
OLLAMA_MODEL=qwen2.5:0.5b
```

## Stack

- Python 3.11, python-telegram-bot 21.6
- PostgreSQL 15 (Alpine)
- Ollama + qwen2.5:0.5b (IA local, CPU)
- Docker Compose

## Estrutura

```
bot/
├── main.py            # Entrypoint, polling, handlers
├── config.py          # Variáveis de ambiente
├── database.py        # Pool de conexões PostgreSQL
├── repository.py      # Queries SQL
├── ai.py              # Integração Ollama
├── decorators.py      # Restrição de acesso
├── utils.py           # Formatação de valores/data
└── handlers/
    ├── __init__.py    # Registro de comandos/callbacks
    ├── commands.py    # /ajuda, /cancelar, /start
    ├── gastos.py      # /gasto, /gastos (CRUD de gastos)
    ├── rendas.py      # /renda, /rendas (CRUD de rendas)
    ├── bancos.py      # /bancos (categorias)
    └── generic.py     # Processamento de mensagens livres (IA)
```
