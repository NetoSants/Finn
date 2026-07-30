import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot import repository
from bot.handlers.confirmacao import confirmacao_renda

logger = logging.getLogger(__name__)

TIMEOUT = 30


def _expired(context):
    ts = context.user_data.get('renda_ts', 0)
    return (time.time() - ts) > TIMEOUT


def _clear(context):
    for key in list(context.user_data):
        if key.startswith('renda_'):
            del context.user_data[key]


async def renda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and len(context.args) >= 2:
        try:
            valor = float(context.args[0].replace(',', '.'))
        except ValueError:
            await update.message.reply_text("Valor invalido. Use numeros (ex: 500 ou 500,50)")
            return

        descricao = ' '.join(context.args[1:])
        user = update.effective_user

        try:
            repository.inserir_renda(valor, descricao, user.id, user.username)
            await confirmacao_renda(update.message, user, valor, descricao)
        except Exception as e:
            logger.error(f"Erro ao registrar renda: {e}")
            await update.message.reply_text("Erro ao registrar renda. Tente novamente.")
        return

    _clear(context)
    context.user_data['renda_step'] = 'valor'
    context.user_data['renda_ts'] = time.time()
    await update.message.reply_text("Qual o valor da renda?")


async def renda_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('renda_step')

    if not step:
        return False

    if _expired(context):
        _clear(context)
        await update.message.reply_text("Interacao cancelada (timeout).")
        return True

    if step == 'valor':
        text = update.message.text.strip().replace(',', '.').replace('R$', '').strip()
        try:
            valor = float(text)
        except ValueError:
            await update.message.reply_text("Valor invalido. Envie apenas numeros (ex: 500 ou 500,50)")
            return True

        if valor <= 0:
            _clear(context)
            keyboard = [
                [InlineKeyboardButton("💰 Gasto", callback_data="menu_gasto"),
                 InlineKeyboardButton("💵 Renda", callback_data="menu_renda")],
                [InlineKeyboardButton("📋 Extrato", callback_data="menu_extrato"),
                 InlineKeyboardButton("💳 Saldo", callback_data="menu_saldo")],
                [                 InlineKeyboardButton("🏦 Bancos", callback_data="bancos_menu"),
                 InlineKeyboardButton("📊 Metas", callback_data="menu_metas")],
                [InlineKeyboardButton("❓ Ajuda", callback_data="menu_ajuda")],
            ]
            await update.message.reply_text(
                "💰 Finn\nSeu assistente financeiro pessoal.",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return True

        context.user_data['renda_valor'] = valor
        context.user_data['renda_step'] = 'descricao'
        context.user_data['renda_ts'] = time.time()
        await update.message.reply_text("Qual a descricao?")
        return True

    if step == 'descricao':
        descricao = update.message.text.strip()
        user = update.effective_user
        valor = context.user_data['renda_valor']

        try:
            repository.inserir_renda(valor, descricao, user.id, user.username)
            await confirmacao_renda(update.message, user, valor, descricao)
        except Exception as e:
            logger.error(f"Erro ao registrar renda: {e}")
            await update.message.reply_text("Erro ao registrar renda. Tente novamente.")

        _clear(context)
        return True

    return False
