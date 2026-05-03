# TeleTony - Obsidian Notes
> Notas técnicas para configuração, manutenção e desenvolvimento do bot financeiro.

## 📌 Visão Geral
- Bot do Telegram para controle financeiro caseiro
- Integração: Bot (Docker) → n8n (Docker) → Ollama (Host) / Google Sheets / Telegram API
- **Arquitetura atual**: Comandos locais + Processamento NLP para mensagens livres
- **Seu User/Chat ID**: `1401845586` (definido em `ALLOWED_USER_IDS`)

---

## 🔧 Configurações Críticas
### Variáveis de Ambiente (.env)
```env
BOT_TOKEN=<token_telegram>
N8N_HOST=n8n                    # DNS do container Docker
N8N_PORT=5678
N8N_WEBHOOK_PATH=webhook-test   # Padrão de todos os webhooks
N8N_URL_FINANCAS=http://n8n:5678/webhook-test/financas  # Gastos/Rendas
N8N_URL_COMANDOS=http://n8n:5678/webhook-test/comandos  # Saldo/Extrato/Ping
N8N_URL_NLP=http://n8n:5678/webhook-test/nlp          # NLP (lowercase!)
ALLOWED_USER_IDS=1401845586
```

### Docker
- Rede: `telegrambot_default`
- Containers acessam n8n via `http://n8n:5678` (nunca localhost/IP)
- Ollama roda na máquina host (Windows): acesso do n8n via `http://192.168.1.105:11434` ou `http://host.docker.internal:11434`

---

## 🤖 Estrutura Atual do Bot (Pós-Refatoração)
### Comandos Locais (em `bot/commands/`)
| Comando | Descrição | URL n8n | Handler |
|---------|-----------|---------|---------|
| `/start` | Boas-vindas | - | `start.py` |
| `/help` | Ajuda | - | `help.py` |
| `/gasto [valor] [desc]` | Registra gasto | `N8N_URL_FINANCAS` | `gasto.py` |
| `/renda [valor] [desc]` | Registra renda | `N8N_URL_FINANCAS` | `renda.py` |
| `/saldo` | Consulta saldo | `N8N_URL_COMANDOS` | `saldo.py` |
| `/extrato` | Mostra extrato | `N8N_URL_COMANDOS` | `extrato.py` |
| `/ping` | Testa integração | `N8N_URL_COMANDOS` | `ping.py` |

### Processamento NLP (Mensagens Livres)
- Todas as mensagens de texto **sem comando** são enviadas para `N8N_URL_NLP`
- n8n + Ollama processa e responde via Telegram API
- Bot envia "⏳ Um momento" e n8n responde diretamente

---

## 📂 Arquivos do Projeto
| Arquivo | Descrição |
|---------|-----------|
| `bot/main.py` | Entrypoint do bot, handlers de mensagens |
| `bot/config.py` | Configurações e URLs de webhook |
| `bot/utils/__init__.py` | Exporta funções de utils |
| `bot/utils/n8n_client.py` | Cliente HTTP para n8n (com e sem resposta) |
| `bot/commands/__init__.py` | Exporta todos os comandos |
| `bot/commands/start.py` | Handler do /start |
| `bot/commands/help.py` | Handler do /help |
| `bot/commands/gasto.py` | Handler do /gasto |
| `bot/commands/renda.py` | Handler do /renda |
| `bot/commands/saldo.py` | Handler do /saldo |
| `bot/commands/extrato.py` | Handler do /extrato |
| `bot/commands/ping.py` | Handler do /ping |
| `AGENTS.md` | Instruções para agentes/colaboradores |
| `.env` | Variáveis de ambiente (não versionar) |

---

## 🛠️ Alterações no Código do Bot
### `bot/utils/n8n_client.py`
- `fazer_requisicao_n8n(url, dados)`: Aguarda resposta (usa em comandos que precisam de retorno)
- `fazer_requisicao_n8n_sem_resposta(url, dados)`: Fire-and-forget (usa no NLP)

### `bot/main.py`
- Handlers registrados: `/start`, `/help`, `/gasto`, `/renda`, `/saldo`, `/extrato`, `/ping`
- Mensagens de texto sem comando → `process_message()` → NLP webhook
- Mensagens com comando → Handlers locais correspondentes

---

## 🛠️ Workflows n8n
### Ativação de Webhooks
Todos os webhooks devem estar ativos no n8n (status "Active") antes de usar os comandos.

### 1. NLP (`/nlp`) - Processamento de Linguagem Natural
**Webhook**: POST `/webhook-test/nlp`
1. **Webhook** (POST /nlp) → Recebe payload: `text`, `user_id`, `username`, `timestamp`
2. **Ollama node** (qwen2.5:1.5b) → Prompt: `Analise: {{ $json.text }}`
3. **HTTP Request** → `https://api.telegram.org/bot{{ $env.BOT_TOKEN }}/sendMessage`
   - Body: `{"chat_id": {{ $json.user_id }}, "text": "{{ $json.output }}"}`

### 2. Finanças (`/financas`) - Gastos/Rendas
**Webhook**: POST `/webhook-test/financas`
- Recebe payload: `tipo` (gasto/renda), `valor`, `descricao`, `pagamento` (opcional), `user_id`, `username`, `timestamp`
- **Google Sheets node** → Salva na aba correspondente (Gastos/Rendas)
- **HTTP Request** → `https://api.telegram.org/bot{{ $env.BOT_TOKEN }}/sendMessage`
  - Body: `{"chat_id": {{ $json.user_id }}, "text": "✅ {{ $json.tipo }} registrado: R$ {{ $json.valor }}"}`

### 3. Comandos (`/comandos`) - Saldo/Extrato/Ping
**Webhook**: POST `/webhook-test/comandos`
- Recebe payload: `intent` (saldo/extrato/ping), `user_id`, `username`, `timestamp`
- **Switch node** → Roteia para lógica de cada intent
- **HTTP Request** → `https://api.telegram.org/bot{{ $env.BOT_TOKEN }}/sendMessage`
  - Body: `{"chat_id": {{ $json.user_id }}, "text": "{{ $json.response }}"}`

---

## ⚠️ Problemas Comuns & Soluções
### Erro de Importação no Python
> **Causa**: Arquivo não exportado no `__init__.py`
> **Solução**: Verifique se todos os handlers estão exportados em `bot/commands/__init__.py` e `bot/utils/__init__.py`

### Timeout do Ollama
> **Solução**: Bot usa fire-and-forget para NLP. n8n responde quando Ollama terminar.

### Comando não reconhecido
> **Solução**: Verifique se o handler está registrado em `main.py` e exportado no `__init__.py`

### Erro 404 no Webhook n8n
> **Solução**: Certifique-se que o path está lowercase (`/nlp` não `/NLP`) e o workflow está ativo

---

## 🧪 Testes
1. **Bot**: Execute `python bot/main.py`
2. **Comandos locais**:
   - `/gasto 30 almoço` → Deve registrar gasto via `N8N_URL_FINANCAS`
   - `/renda 500 salário` → Deve registrar renda via `N8N_URL_FINANCAS`
   - `/saldo` → Deve consultar via `N8N_URL_COMANDOS`
3. **NLP**: Envie mensagem sem comando: "Gastei 40 com jogo do bixo"
4. **n8n**: Teste webhooks via curl:
   ```bash
   curl -X POST http://localhost:5678/webhook-test/nlp \
     -H "Content-Type: application/json" \
     -d '{"text": "gastei 30", "user_id": 1401845586, "username": "teste", "timestamp": "2026-05-03 01:00:00"}'
   ```

---

## 📝 Próximos Passos
- [ ] Testar todos os comandos localmente
- [ ] Configurar workflows n8n para `/financas` e `/comandos`
- [ ] Melhorar prompt do Ollama para NLP
- [ ] Adicionar validação de dados nos comandos
- [ ] Documentar exemplos de uso no `/help`

---

## 📋 To Do List - Sistema de Bancos e Parcelas

### 1. Gestão de Bancos
- [ ] **Comando `/cadastrar_banco`**
  - [ ] Adicionar handler para registrar banco com nome e dia de fechamento
  - [ ] Validar dia de fechamento (1-31)
  - [ ] Enviar payload para n8n via webhook específico
  - [ ] Atualizar aba "Bancos" no Google Sheets (colunas: Nome, Fechamento, Data Cadastro)
- [ ] **Listagem de Bancos**
  - [ ] Criar webhook n8n para listar bancos existentes
  - [ ] Buscar dados da aba "Bancos" e retornar JSON com nomes
  - [ ] Integrar handler /gasto para mostrar lista de bancos após seleção de pagamento

### 2. Sistema de Parcelas
- [ ] **Coleta de Parcelas**
  - [ ] Adicionar passo no fluxo /gasto para solicitar número de parcelas
  - [ ] Validar entrada (número inteiro ≥ 1)
- [ ] **Lógica de Distribuição**
  - [ ] Implementar cálculo de distribuição de parcelas com base em:
    - Data da compra
    - Dia de fechamento do banco
    - Regra: compras antes do fechamento → mês atual; após → próximo mês
  - [ ] Gerar array com meses das parcelas (ex: 05/26, 06/26, etc.)
- [ ] **Gravação no Google Sheets**
  - [ ] Criar workflow n8n para processar gastos parcelados
  - [ ] Loop para gravar cada parcela na aba de mês correspondente
  - [ ] Formatar descrição das parcelas como "descricao (parcela X/Y)"
  - [ ] Criar abas automaticamente caso não existam (ex: 07/26)

### 3. Atualização de Workflows n8n
- [ ] **Webhook `/cadastrar_banco`**
  - [ ] Receber payload com nome, fechamento, user_id
  - [ ] Google Sheets → Append Row na aba "Bancos"
  - [ ] Telegram API → Confirmar cadastro ao usuário
- [ ] **Webhook `/listar_bancos`**
  - [ ] Google Sheets → Read Range aba "Bancos", coluna Nome
  - [ ] HTTP Response → JSON com array de bancos
- [ ] **Webhook `/processar_gasto` (atualizado)**
  - [ ] Receber payload com: valor, descricao, pagamento, banco, parcelas, data_compra
  - [ ] Distribuir parcelas conforme regra de fechamento
  - [ ] Gravar cada parcela na aba de mês correspondente
  - [ ] Telegram API → Confirmar gasto parcelado

### 4. Interface do Bot
- [ ] **Fluxo Completo `/gasto`**
  - [ ] `/gasto [valor] [descricao]` → Mostrar botões de pagamento
  - [ ] Selecionar pagamento → Mostrar lista de bancos + "Adicionar Novo"
  - [ ] Selecionar banco → Solicitar número de parcelas
  - [ ] Confirmar → Enviar para n8n → Exibir confirmação detalhada
- [ ] **Mensagens do Bot**
  - [ ] Respostas amigáveis para cada etapa
  - [ ] Exemplo: "✅ 12x de R$100 no Itaú (fechamento 15)"

### 5. Documentação
- [ ] **OBSIDIAN-NOTES.md**
  - [ ] Atualizar seção "Bancos" com estrutura da aba
  - [ ] Documentar fluxos de cadastro e seleção de banco
  - [ ] Incluir exemplos de payloads para cada webhook
  - [ ] Explicar lógica de fechamento e distribuição de parcelas
- [ ] **AGENTS.md**
  - [ ] Atualizar diagrama de handlers com novo fluxo
  - [ ] Documentar comandos: `/gasto`, `/cadastrar_banco`
  - [ ] Incluir próximos passos atualizados

### 6. Validações e Edge Cases
- [ ] **Validações de Dados**
  - [ ] Dia de fechamento entre 1-31
  - [ ] Número de parcelas ≥ 1
  - [ ] Data da compra válida
- [ ] **Cenários de Erro**
  - [ ] Banco não encontrado
  - [ ] Aba de mês não existe (criar automaticamente)
  - [ ] Payload inválido do n8n

---

## 🎯 Prioridades Sugeridas
1. **Prioridade 1**: Implementar comando `/cadastrar_banco` e aba "Bancos"
2. **Prioridade 2**: Criar webhooks n8n para listar bancos e processar gastos
3. **Prioridade 3**: Integrar seleção de banco no fluxo /gasto
4. **Prioridade 4**: Implementar lógica de distribuição de parcelas
5. **Prioridade 5**: Documentação final e testes

---

#teletony #n8n #ollama #telegram-bot #python #finanças #obsidian
