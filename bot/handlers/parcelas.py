import logging
from datetime import date, timedelta
import calendar
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def parcelas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        rows = repository.listar_parcelas(user_id)
    except Exception as e:
        logger.error(f"Erro ao listar parcelas: {e}")
        await update.message.reply_text("Erro ao listar parcelas.")
        return

    if not rows:
        await update.message.reply_text(
            "Nenhuma parcela cadastrada.\n\n"
            "Use /parcelar [valor] [parcelas] [dia] [desc] para adicionar."
        )
        return

    msg = "**Parcelas:**\n\n"
    for row in rows:
        id_, desc, valor_total, valor_parc, num_parc, parc_atual, pago, data = row
        status = "OK" if pago else "  "
        msg += f"{status} {desc}\n"
        msg += f"   R$ {valor_parc:.2f} x {parc_atual}/{num_parc} (Total: R$ {valor_total:.2f})\n"
        msg += f"   Primeira: {data.strftime('%d/%m/%Y')}\n\n"

    keyboard = [
        [InlineKeyboardButton("Nova Parcela", callback_data="parcelas_adicionar")]
    ]

    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def parcelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 4:
        await update.message.reply_text(
            "Uso: /parcelar [valor] [parcelas] [dia] [descricao]\n"
            "Ex: /parcelar 100 10 25 Geladeira"
        )
        return

    try:
        valor = float(context.args[0].replace(',', '.'))
        parcelas_total = int(context.args[1])
        dia = int(context.args[2])
        descricao = ' '.join(context.args[3:])
    except ValueError:
        await update.message.reply_text("Valores invalidos.")
        return

    if dia < 1 or dia > 31:
        await update.message.reply_text("Dia deve ser entre 1 e 31.")
        return

    valor_parcela = valor / parcelas_total
    user = update.effective_user

    today = date.today()
    try:
        primeira_data = date(today.year, today.month, dia)
    except ValueError:
        ultimo_dia = calendar.monthrange(today.year, today.month)[1]
        primeira_data = date(today.year, today.month, min(dia, ultimo_dia))

    if primeira_data < today:
        mes = today.month + 1
        ano = today.year
        if mes > 12:
            mes = 1
            ano += 1
        try:
            primeira_data = date(ano, mes, dia)
        except ValueError:
            ultimo_dia = calendar.monthrange(ano, mes)[1]
            primeira_data = date(ano, mes, min(dia, ultimo_dia))

    try:
        repository.inserir_parcela(descricao, valor, valor_parcela, parcelas_total, primeira_data, user.id, user.username)
        await update.message.reply_text(
            f"Parcela cadastrada!\n\n"
            f"{descricao}\n"
            f"R$ {valor_parcela:.2f} x {parcelas_total}\n"
            f"Primeira em: {primeira_data.strftime('%d/%m/%Y')}"
        )
    except Exception as e:
        logger.error(f"Erro ao cadastrar parcela: {e}")
        await update.message.reply_text("Erro ao cadastrar parcela.")
