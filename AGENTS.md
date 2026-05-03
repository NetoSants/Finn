# TeleTony

Bot do Telegram para controle financeiro, processamento via n8n + Ollama.

## Arquitetura Simples

- **Entrypoint**: `bot/main.py`
- **Fluxo**: Bot (Docker) → Webhook n8n → Ollama (IA) → Telegram API / Google Sheets
- **Processamento**: Todas as mensagens em linguagem natural via webhook NLP (`/nlp`)
- **Sem comandos locais**: n8n roteia intents (gasto, renda, saldo, etc)

## Configuração

### Variáveis de ambiente (.env)
```
BOT_TOKEN=<token_telegram>
N8N_HOST=n8n                    # DNS do container Docker
N8N_PORT=5678
N8N_WEBHOOK_PATH=webhook-test   # padrão
N8N_URL_NLP=http://n8n:5678/webhook-test/nlp  # NLP (lowercase!)
ALLOWED_USER_IDS=1401845586      # Seu User ID
```

### Docker
- Container acessa n8n via `http://n8n:5678` (rede `telegrambot_default`)
- Ollama na máquina host: `http://192.168.1.105:11434` ou `host.docker.internal:11434`

## Dependências

`python-telegram-bot==21.6`, `python-dotenv==1.0.1`, `httpx`

## Execução

```bash
# Local (requer .env)
python bot/main.py

# Docker (no servidor)
docker logs telegrambot-bot-1 --tail 30
docker restart telegrambot-bot-1
```

## Workflow n8n Mínimo

Para iniciar testes do zero, crie um workflow simples:

1. **Webhook** (POST /nlp)
2. **Ollama node** (qwen2.5:1.5b)
   - Prompt: `Process: {{ $json.text }}`
3. **HTTP Request** → `https://api.telegram.org/bot{{ $env.BOT_TOKEN }}/sendMessage`
   - Body: `{"chat_id": {{ $json.user_id }}, "text": "Recebi: {{ $json.text }}"}`

## Próximos Passos

1. Configurar Ollama para extrair intent + campos
2. Adicionar roteamento por intent (Switch node)
3. Integrar Google Sheets para gastos/renda
4. Comandos: saldo/extrato via n8n
