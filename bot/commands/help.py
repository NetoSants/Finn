from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """🤖 *Comandos do TeleTony*

/financas - Menu financeiro
  ├ /gasto [valor] [desc] - Registrar gasto
  ├ /renda [valor] [desc] - Registrar renda
  ├ /saldo - Consultar saldo
  └ /extrato - Ver extrato

/ping - Testar integração
/help - Esta ajuda
/start - Iniciar bot"""
    await update.message.reply_text(help_text, parse_mode="Markdown")
