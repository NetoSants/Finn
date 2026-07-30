from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comandos do Finn\n\n"
        "Financeiro:\n"
        "/gasto [valor] [descricao] - Registra um gasto\n"
        "  Ex: /gasto 30 almoco\n\n"
        "/renda [valor] [descricao] - Registra uma renda\n"
        "  Ex: /renda 500 salario\n\n"
        "/saldo - Consulta saldo atual\n"
        "/extrato - Mostra extrato\n\n"
        "Organizacao:\n"
        "/categorias - Lista categorias\n"
        "/meta [cat] [limite] - Define meta mensal\n"
        "  Ex: /meta alimentacao 800\n\n"
        "Bancos:\n"
        "/bancos - Lista e gerencia bancos\n\n"
        "Parcelas:\n"
        "/parcelas - Lista parcelas\n"
        "/parcelar [valor] [parc] [dia] [desc]\n\n"
        "Outros:\n"
        "/start - Inicia o bot\n"
        "/help - Mostra esta ajuda\n"
        "/ping - Status do bot"
    )
