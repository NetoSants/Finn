from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ola! Eu sou o **Finn**, seu assistente financeiro via Telegram.\n\n"
        "**O que eu faco?**\n"
        "Gerencio seus gastos, rendas, bancos e parcelas.\n\n"
        "**Comandos disponiveis:**\n"
        "/gasto [valor] [descricao] - Registra um gasto\n"
        "/renda [valor] [descricao] - Registra uma renda\n"
        "/saldo - Consulta saldo\n"
        "/extrato - Mostra extrato\n"
        "/bancos - Lista bancos cadastrados\n"
        "/cadastrar_banco [nome] [venc] [limite] - Cadastra um banco\n"
        "/remover_banco [nome] - Remove um banco\n"
        "/parcelas - Lista parcelas\n"
        "/parcelar [valor] [parc] [dia] [desc] - Cadastra parcela\n"
        "/help - Mostra esta ajuda\n"
        "/ping - Status do bot",
        parse_mode="Markdown"
    )
