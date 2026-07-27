import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def bancos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        rows = repository.listar_bancos()
    except Exception as e:
        logger.error(f"Erro ao listar bancos: {e}")
        await update.message.reply_text("Erro ao listar bancos.")
        return

    if not rows:
        msg = "**Nenhum banco cadastrado.**"
    else:
        msg = "**Bancos Cadastrados:**\n\n"
        for row in rows:
            msg += f"{row[1]} - Venc: dia {row[2]} | Limite: R$ {row[3]:.2f}\n"

    keyboard = [
        [
            InlineKeyboardButton("Adicionar Banco", callback_data="bancos_adicionar"),
            InlineKeyboardButton("Remover Banco", callback_data="bancos_remover"),
        ]
    ]

    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def bancos_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "bancos_adicionar":
        await query.edit_message_text(
            "Para adicionar um banco, use:\n"
            "/cadastrar_banco [nome] [vencimento] [limite]\n\n"
            "Exemplo: /cadastrar_banco Itau 15 5000",
            parse_mode="Markdown"
        )
    elif query.data == "bancos_remover":
        await query.edit_message_text(
            "Para remover um banco, use:\n"
            "/remover_banco [nome]\n\n"
            "Exemplo: /remover_banco Itau",
            parse_mode="Markdown"
        )
