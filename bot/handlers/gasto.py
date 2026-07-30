import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot import repository
from bot.handlers.confirmacao import confirmacao_gasto

logger = logging.getLogger(__name__)

TIMEOUT = 30


def _expired(context):
    ts = context.user_data.get('gasto_ts', 0)
    return (time.time() - ts) > TIMEOUT


def _clear(context):
    for key in list(context.user_data):
        if key.startswith('gasto_'):
            del context.user_data[key]


def _header(valor=None, descricao=None):
    if valor and descricao:
        return f"💰 Gasto — R$ {valor:.2f} • {descricao}"
    if valor:
        return f"💰 Gasto — R$ {valor:.2f}"
    return "💰 Registrar gasto"


async def _edit(msg_id, chat_id, context, text, reply_markup=None):
    try:
        await context.bot.edit_message_text(
            text, chat_id=chat_id, message_id=msg_id,
            reply_markup=reply_markup,
        )
        return True
    except Exception:
        return False


async def gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _clear(context)
    context.user_data['gasto_step'] = 'valor'
    context.user_data['gasto_ts'] = time.time()
    msg = await update.message.reply_text(
        f"{_header()}\n\nEnvie o valor:",
    )
    context.user_data['gasto_msg_id'] = msg.message_id


async def gasto_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get('gasto_step')

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
            await update.message.reply_text("Valor invalido. Envie apenas numeros (ex: 30 ou 30,50)")
            return True

        if valor <= 0:
            _clear(context)
            await update.message.reply_text(
                "💰 Finn\nSeu assistente financeiro pessoal.",
                reply_markup=InlineKeyboardMarkup(_main_menu_keyboard()),
            )
            return True

        context.user_data['gasto_valor'] = valor
        context.user_data['gasto_step'] = 'descricao'
        context.user_data['gasto_ts'] = time.time()

        msg_id = context.user_data.get('gasto_msg_id')
        chat_id = update.message.chat_id

        if msg_id:
            await _edit(msg_id, chat_id, context,
                        f"{_header(valor)}\n\nQual a descricao?")
        else:
            msg = await update.message.reply_text(f"{_header(valor)}\n\nQual a descricao?")
            context.user_data['gasto_msg_id'] = msg.message_id

        await update.message.delete()
        return True

    if step == 'descricao':
        descricao = update.message.text.strip()
        context.user_data['gasto_descricao'] = descricao
        context.user_data['gasto_ts'] = time.time()

        valor = context.user_data['gasto_valor']
        msg_id = context.user_data.get('gasto_msg_id')
        chat_id = update.message.chat_id

        if context.user_data.get('gasto_pagamento') == 'credito':
            context.user_data['gasto_step'] = 'parcelas'
            if msg_id:
                await _edit(msg_id, chat_id, context,
                            f"{_header(valor, descricao)}\n\nEm quantas parcelas? (1-12)")
            else:
                msg = await update.message.reply_text(
                    f"{_header(valor, descricao)}\n\nEm quantas parcelas? (1-12)")
                context.user_data['gasto_msg_id'] = msg.message_id
            await update.message.delete()
            return True

        context.user_data['gasto_step'] = 'categoria'
        categorias = repository.listar_categorias()
        keyboard = _build_categoria_keyboard(categorias)

        if msg_id:
            await _edit(msg_id, chat_id, context,
                        f"{_header(valor, descricao)}\n\nSelecione a categoria:",
                        reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            msg = await update.message.reply_text(
                f"{_header(valor, descricao)}\n\nSelecione a categoria:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            context.user_data['gasto_msg_id'] = msg.message_id

        await update.message.delete()
        return True

    if step == 'parcelas':
        text = update.message.text.strip()
        try:
            parc = int(text)
        except ValueError:
            await update.message.reply_text("Envie um numero de 1 a 12.")
            return True
        if parc < 1 or parc > 12:
            await update.message.reply_text("Numero deve ser entre 1 e 12.")
            return True

        context.user_data['gasto_parcelas'] = parc
        context.user_data['gasto_step'] = None
        context.user_data['gasto_ts'] = time.time()

        valor = context.user_data.get('gasto_valor')
        descricao = context.user_data.get('gasto_descricao', '')

        bancos = repository.listar_bancos()

        if not bancos:
            categoria_id = context.user_data.pop('gasto_categoria_id', None)
            payment_type = context.user_data.pop('gasto_pagamento', 'credito')
            user = update.effective_user
            try:
                repository.inserir_transacao(
                    'gasto', valor, descricao, payment_type,
                    user.id, user.username, categoria_id, None, parc
                )
                parc_val = valor / parc
                parc_info = f"\n📦 {parc}x R$ {parc_val:.2f}" if parc > 1 else ""
                await update.message.reply_text(
                    f"✅ Gasto registrado!\n\n"
                    f"💰 R$ {valor:.2f}\n"
                    f"📝 {descricao}\n"
                    f"💳 Credito{parc_info}"
                )
            except Exception as e:
                logger.error(f"Erro ao registrar gasto: {e}")
                await update.message.reply_text("Erro ao registrar gasto. Tente novamente.")
            _clear(context)
            return True

        keyboard = []
        row = []
        for b in bancos:
            row.append(InlineKeyboardButton(b[1], callback_data=f"gasto_banco_{b[0]}"))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("Pular", callback_data="gasto_banco_0")])

        parc_val = valor / parc
        parc_info = f" ({parc}x R$ {parc_val:.2f})" if parc > 1 else ""

        msg_id = context.user_data.get('gasto_msg_id')
        chat_id = update.message.chat_id

        if msg_id:
            await _edit(msg_id, chat_id, context,
                        f"{_header(valor, descricao)}{parc_info}\n\nBanco:",
                        reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            msg = await update.message.reply_text(
                f"{_header(valor, descricao)}{parc_info}\n\nBanco:",
                reply_markup=InlineKeyboardMarkup(keyboard))
            context.user_data['gasto_msg_id'] = msg.message_id

        await update.message.delete()
        return True

    return False


def _build_categoria_keyboard(categorias):
    keyboard = []
    row = []
    for cat in categorias:
        label = f"{cat[2]} {cat[1]}" if cat[2] else cat[1]
        row.append(InlineKeyboardButton(label, callback_data=f"gasto_cat_{cat[0]}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("◀ Voltar", callback_data="gasto_cancelar")])
    return keyboard


async def gasto_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "gasto_cancelar":
        _clear(context)
        await _show_main_menu(query)
        return

    if data == "gasto_back_pag":
        await _show_categoria(update, context)
        return

    if data == "gasto_back_banco":
        pagamento = context.user_data.get('gasto_pagamento')
        if pagamento == 'credito':
            await _show_parcelas(update, context)
        else:
            await _show_pagamento(update, context)
        return

    if _expired(context):
        _clear(context)
        await query.edit_message_text("Interacao cancelada (timeout).")
        return

    valor = context.user_data.get('gasto_valor')
    descricao = context.user_data.get('gasto_descricao')

    if not valor or not descricao:
        _clear(context)
        await query.edit_message_text("Erro: dados do gasto nao encontrados. Tente novamente.")
        return

    if data.startswith("gasto_cat_"):
        categoria_id = int(data.replace("gasto_cat_", ""))
        context.user_data['gasto_categoria_id'] = categoria_id
        context.user_data['gasto_ts'] = time.time()
        await _show_pagamento(update, context)
        return

    if data in ("gasto_debito", "gasto_pix", "gasto_credito"):
        payment_type = data.replace("gasto_", "")
        context.user_data['gasto_pagamento'] = payment_type
        context.user_data['gasto_ts'] = time.time()

        if payment_type == 'credito':
            await _show_parcelas(update, context)
            return

        bancos = repository.listar_bancos()

        if not bancos:
            categoria_id = context.user_data.pop('gasto_categoria_id', None)
            user = update.effective_user
            try:
                repository.inserir_transacao(
                    'gasto', valor, descricao, payment_type,
                    user.id, user.username, categoria_id
                )
                await confirmacao_gasto(query, user, valor, descricao, categoria_id, payment_type)
            except Exception as e:
                logger.error(f"Erro ao registrar gasto: {e}")
                await query.edit_message_text("Erro ao registrar gasto. Tente novamente.")
            _clear(context)
            return

        await _show_banco(update, context, bancos)
        return

    if data.startswith("gasto_parc_"):
        parcelas = int(data.replace("gasto_parc_", ""))
        context.user_data['gasto_parcelas'] = parcelas
        context.user_data['gasto_ts'] = time.time()

        bancos = repository.listar_bancos()

        if not bancos:
            categoria_id = context.user_data.pop('gasto_categoria_id', None)
            payment_type = context.user_data.pop('gasto_pagamento', 'debito')
            parc = context.user_data.pop('gasto_parcelas', 1)
            user = update.effective_user
            try:
                repository.inserir_transacao(
                    'gasto', valor, descricao, payment_type,
                    user.id, user.username, categoria_id, None, parc
                )
                await confirmacao_gasto(query, user, valor, descricao, categoria_id, payment_type, None, parc)
            except Exception as e:
                logger.error(f"Erro ao registrar gasto: {e}")
                await query.edit_message_text("Erro ao registrar gasto. Tente novamente.")
            _clear(context)
            return

        await _show_banco(update, context, bancos)
        return

    if data.startswith("gasto_banco_"):
        banco_id = int(data.replace("gasto_banco_", ""))
        categoria_id = context.user_data.pop('gasto_categoria_id', None)
        payment_type = context.user_data.pop('gasto_pagamento', 'debito')
        parcelas = context.user_data.pop('gasto_parcelas', 1)
        user = update.effective_user
        banco_id_final = banco_id if banco_id != 0 else None

        desc_final = descricao
        if banco_id_final:
            bancos = repository.listar_bancos()
            for b in bancos:
                if b[0] == banco_id_final:
                    desc_final = f"{descricao} ({b[1]})"
                    break

        try:
            repository.inserir_transacao(
                'gasto', valor, desc_final, payment_type,
                user.id, user.username, categoria_id, banco_id_final, parcelas
            )
            await confirmacao_gasto(query, user, valor, desc_final, categoria_id, payment_type, banco_id_final, parcelas)
        except Exception as e:
            logger.error(f"Erro ao registrar gasto: {e}")
            await query.edit_message_text("Erro ao registrar gasto. Tente novamente.")

        _clear(context)
        return


async def _show_pagamento(update, context):
    query = update.callback_query
    valor = context.user_data.get('gasto_valor')
    descricao = context.user_data.get('gasto_descricao')

    keyboard = [
        [InlineKeyboardButton("Debito", callback_data="gasto_debito"),
         InlineKeyboardButton("Credito", callback_data="gasto_credito"),
         InlineKeyboardButton("Pix", callback_data="gasto_pix")],
        [InlineKeyboardButton("◀ Voltar", callback_data="gasto_back_pag")],
    ]

    context.user_data['gasto_ts'] = time.time()

    await query.edit_message_text(
        f"{_header(valor, descricao)}\n\nPagamento:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def _show_parcelas(update, context):
    query = update.callback_query
    valor = context.user_data.get('gasto_valor')
    descricao = context.user_data.get('gasto_descricao')

    context.user_data['gasto_step'] = 'parcelas'
    context.user_data['gasto_ts'] = time.time()

    await query.edit_message_text(
        f"{_header(valor, descricao)}\n\nEm quantas parcelas? (1-12)",
    )


async def _show_categoria(update, context):
    query = update.callback_query
    valor = context.user_data.get('gasto_valor')
    descricao = context.user_data.get('gasto_descricao')

    categorias = repository.listar_categorias()
    keyboard = _build_categoria_keyboard(categorias)

    context.user_data['gasto_ts'] = time.time()

    await query.edit_message_text(
        f"{_header(valor, descricao)}\n\nCategoria:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def _show_banco(update, context, bancos):
    query = update.callback_query
    valor = context.user_data.get('gasto_valor')
    descricao = context.user_data.get('gasto_descricao')

    keyboard = []
    row = []
    for b in bancos:
        row.append(InlineKeyboardButton(b[1], callback_data=f"gasto_banco_{b[0]}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("Pular", callback_data="gasto_banco_0")])
    keyboard.append([InlineKeyboardButton("◀ Voltar", callback_data="gasto_back_banco")])

    await query.edit_message_text(
        f"{_header(valor, descricao)}\n\nBanco:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


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


async def _show_main_menu(query):
    texto = "💰 Finn\nSeu assistente financeiro pessoal."
    await query.edit_message_text(
        texto, reply_markup=InlineKeyboardMarkup(_main_menu_keyboard()),
    )
