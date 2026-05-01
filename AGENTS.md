# TeleTony

Bot do Telegram para controle financeiro, integrado com workflows n8n e Google Sheets.

## Arquitetura

- **Entrypoint real**: `bot/main.py` (confirmado no Dockerfile), não o `bot.py` na raiz
- **Pacote**: `bot/` contém commands modulares (`commands/`) e utilitários (`utils/`)
- **Execução**: Container Docker em `192.168.193.90`, rede `telegrambot_default`
- **Integração**: Bot → webhooks n8n → Google Sheets
- **Acesso n8n**: http://192.168.193.90:5678
- **Acesso Portainer**: http://192.168.193.90:9000 (Stack: TeleTony)

## Convenções críticas

- **DNS do container**: Use `http://n8n:5678` para webhooks, nunca `localhost` ou IP
- **Workflows n8n devem estar ativados** (toggle verde) para receber chamadas de webhook
- **Sem fluxo padrão de desenvolvimento Python**: sem venv, sem testes, sem linting/typechecking
- **Atualizações**: `git push` → `git pull` no servidor → `docker build` ou recriar no Portainer
- **`.env` contém BOT_TOKEN sensível** — nunca faça commit; está no gitignore

## Convenção de idioma

- **Todo conteúdo voltado ao usuário deve estar em Português Brasileiro (pt-BR)**
- Respostas do bot, mensagens e documentação para usuários devem usar pt-BR
- Comentários de código e documentação técnica interna podem permanecer em inglês

## Dependências e bugs conhecidos

- **`httpx` ausente no `requirements.txt`**: usado em `bot/utils/n8n_client.py` e necessário para requisições n8n
- `requirements.txt` atual: `python-telegram-bot==21.6`, `python-dotenv==1.0.1`

## Comandos do bot implementados

| Comando | Descrição | Webhook |
|---------|-----------|---------|
| `/start` | Mensagem de boas-vindas | - |
| `/help` | Lista comandos disponíveis | - |
| `/ping` | Testar integração | `comandos` |
| `/gasto [valor] [desc]` | Registrar gasto | `financas` |
| `/renda [valor] [desc]` | Registrar renda | `financas` |
| `/saldo` | Consultar saldo atual | `comandos` |
| `/extrato` | Ver extrato de transações | `comandos` |

## Variáveis de ambiente

```
BOT_TOKEN=<do Portainer ou .env>
N8N_URL_FINANCAS=http://n8n:5678/webhook/financas
N8N_URL_COMANDOS=http://n8n:5678/webhook/comandos
```

## Comandos

```bash
# Executar localmente (requer .env com BOT_TOKEN)
python bot/main.py

# Operações Docker (no servidor)
docker logs telegrambot-bot-1 --tail 30
docker restart telegrambot-bot-1
docker exec -it telegrambot-bot-1 sh

# Testar conectividade n8n a partir do container
docker exec telegrambot-bot-1 sh -c 'wget -q -O- http://n8n:5678 --timeout=5'
```

## Arquivos gerados (gitignore)

- `planilha_financeira.xlsx` — criado por `criar_planilha.py`
- `contexto_teletony.txt`, `contexto_financeiro.md`, `TeleTony.md` — documentação
