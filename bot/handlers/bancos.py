import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)

TIMEOUT = 120


def _expired(context):
    ts = context.user_data.get('banco_ts', 0)
    return (time.time() - ts) > TIMEOUT


def _clear(context):
    for key in list(context.user_data):
        if key.startswith('banco_'):
            del context.user_data[key]


def _main_menu_keyboard():
    return [
        [InlineKeyboardButton("💰 Gasto", callback_data="menu_gasto"),
         InlineKeyboardButton("💵 Renda", callback_data="menu_renda")],
        [InlineKeyboardButton("📋 Extrato", callback_data="menu_extrato"),
         InlineKeyboardButton("💳 Saldo", callback_data="menu_saldo")],
         [InlineKeyboardButton("🏦 Bancos", callback_data="bancos_menu"),
         InlineKeyboardButton("📊 Metas", callback_data="menu_metas")],
        [InlineKeyboardButton("❓ Ajuda", callback_data="menu_ajuda")],
    ]


def _bancos_listagem(rows):
    if not rows:
        return "🏦 Bancos\n\nNenhum banco cadastrado."
    msg = "🏦 Seus bancos\n\n"
    for b in rows:
        msg += f"💳 {b[1]}\n   📅 Fecha dia {b[2]} | Limite: R$ {b[3]:.2f}\n\n"
    return msg


async def bancos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = repository.listar_bancos()
    texto = _bancos_listagem(rows)
    keyboard = [
        [InlineKeyboardButton("➕ Adicionar", callback_data="bancos_adicionar")],
    ]
    if rows:
        keyboard.append([InlineKeyboardButton("➖ Remover", callback_data="bancos_remover")])
    keyboard.append([InlineKeyboardButton("◀ Voltar", callback_data="menu_voltar")])
    await update.message.reply_text(
        texto, reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def bancos_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "bancos_menu":
        rows = repository.listar_bancos()
        texto = _bancos_listagem(rows)
        keyboard = [
            [InlineKeyboardButton("➕ Adicionar", callback_data="bancos_adicionar")],
        ]
        if rows:
            keyboard.append([InlineKeyboardButton("➖ Remover", callback_data="bancos_remover")])
        keyboard.append([InlineKeyboardButton("◀ Voltar", callback_data="menu_voltar")])
        await query.edit_message_text(
            texto, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data == "bancos_adicionar":
        _clear(context)
        context.user_data['banco_step'] = 'nome'
        context.user_data['banco_ts'] = time.time()
        await query.edit_message_text("Qual o nome do banco?")
        return

    if data == "bancos_remover":
        rows = repository.listar_bancos()
        if not rows:
            await query.edit_message_text("Nenhum banco para remover.")
            return
        keyboard = []
        for b in rows:
            keyboard.append([InlineKeyboardButton(f"❌ {b[1]}", callback_data=f"bancos_del_{b[0]}")])
        keyboard.append([InlineKeyboardButton("◀ Voltar", callback_data="bancos_menu")])
        await query.edit_message_text(
            "Selecione o banco para remover:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data.startswith("bancos_del_"):
        banco_id = int(data.replace("bancos_del_", ""))
        rows = repository.listar_bancos()
        banco_nome = None
        for b in rows:
            if b[0] == banco_id:
                banco_nome = b[1]
                break

        if banco_nome:
            repository.remover_banco(banco_nome)

        rows = repository.listar_bancos()
        texto = _bancos_listagem(rows) + "\n✅ Banco removido!"
        keyboard = [
            [InlineKeyboardButton("➕ Adicionar", callback_data="bancos_adicionar")],
        ]
        if rows:
            keyboard.append([InlineKeyboardButton("➖ Remover", callback_data="bancos_remover")])
        keyboard.append([InlineKeyboardButton("◀ Voltar", callback_data="menu_voltar")])
        await query.edit_message_text(
            texto, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return


async def banco_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('banco_step')

    if not step:
        return False

    if _expired(context):
        _clear(context)
        await update.message.reply_text("Interacao cancelada (timeout).")
        return True

    text = update.message.text.strip()

    if step == 'nome':
        if not text:
            await update.message.reply_text("Nome invalido. Tente novamente.")
            return True
        context.user_data['banco_nome'] = text
        context.user_data['banco_step'] = 'fechamento'
        context.user_data['banco_ts'] = time.time()
        await update.message.reply_text(f"📅 Dia de fechamento da fatura de {text}? (1-31)")
        return True

    if step == 'fechamento':
        try:
            dia = int(text)
        except ValueError:
            await update.message.reply_text("Envie um numero de 1 a 31.")
            return True
        if dia < 1 or dia > 31:
            await update.message.reply_text("Dia deve ser entre 1 e 31.")
            return True
        context.user_data['banco_dia'] = dia
        context.user_data['banco_step'] = 'limite'
        context.user_data['banco_ts'] = time.time()
        nome = context.user_data['banco_nome']
        await update.message.reply_text(f"💰 Limite do {nome}? (ex: 5000)")
        return True

    if step == 'limite':
        try:
            limite = float(text.replace(',', '.').replace('R$', '').strip())
        except ValueError:
            await update.message.reply_text("Valor invalido. Envie apenas numeros.")
            return True

        nome = context.user_data['banco_nome']
        dia = context.user_data['banco_dia']

        try:
            repository.inserir_banco(nome, dia, limite)
            keyboard = [
                [InlineKeyboardButton("➕ Adicionar outro", callback_data="bancos_adicionar")],
                [InlineKeyboardButton("◀ Voltar", callback_data="bancos_menu")],
            ]
            await update.message.reply_text(
                f"✅ Banco cadastrado!\n\n"
                f"💳 {nome}\n"
                f"📅 Fecha dia {dia}\n"
                f"💰 Limite: R$ {limite:.2f}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Erro ao cadastrar banco: {e}")
            await update.message.reply_text("Erro ao cadastrar banco. Tente novamente.")

        _clear(context)
        return True

    return False
