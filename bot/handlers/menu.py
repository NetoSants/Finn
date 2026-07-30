import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "menu_gasto":
        from bot.handlers.gasto import gasto, _clear
        import time
        _clear(context)
        context.user_data['gasto_step'] = 'valor'
        context.user_data['gasto_ts'] = time.time()
        context.user_data['gasto_msg_id'] = query.message.message_id
        await query.edit_message_text("💰 Vamos registrar um gasto.\n\nEnvie o valor:")

    elif data == "menu_renda":
        from bot.handlers.renda import _clear
        import time
        _clear(context)
        context.user_data['renda_step'] = 'valor'
        context.user_data['renda_ts'] = time.time()
        await query.edit_message_text("💵 Vamos registrar uma renda.\n\nQual o valor?")

    elif data == "menu_extrato":
        user_id = update.effective_user.id
        rows = repository.listar_transacoes(user_id)

        if not rows:
            await query.edit_message_text("Nenhuma transacao encontrada.")
            return

        msg = "Extrato (ultimas 20):\n\n"
        for row in rows:
            tipo, valor, descricao, pagamento, data_transacao, cat_nome, cat_emoji = row
            emoji = "G" if tipo == "gasto" else "R"
            cat = f" {cat_emoji}" if cat_emoji else ""
            pago = f" ({pagamento})" if pagamento else ""
            data_str = data_transacao.strftime('%d/%m') if data_transacao else "??/??"
            msg += f"{emoji} {data_str}: R$ {valor:.2f} - {descricao}{cat}{pago}\n"

        keyboard = [[InlineKeyboardButton("◀ Voltar", callback_data="menu_voltar")]]
        await query.edit_message_text(
            msg, reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "menu_saldo":
        user_id = update.effective_user.id
        total_gastos = repository.total_gastos(user_id)
        total_rendas = repository.total_rendas(user_id)
        saldo_valor = total_rendas - total_gastos

        keyboard = [[InlineKeyboardButton("◀ Voltar", callback_data="menu_voltar")]]
        await query.edit_message_text(
            f"💳 Saldo\n\n"
            f"💵 Rendas: R$ {total_rendas:.2f}\n"
            f"💰 Gastos: R$ {total_gastos:.2f}\n\n"
            f"📊 Saldo: R$ {saldo_valor:.2f}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "menu_metas":
        from datetime import date
        hoje = date.today()
        user_id = update.effective_user.id
        metas = repository.listar_metas(hoje.month, hoje.year, user_id)

        if not metas:
            await query.edit_message_text(
                "📊 Metas\n\nNenhuma meta definida para este mes.\n\n"
                "Use /meta para definir."
            )
            return

        texto = f"📊 Metas de {hoje.month:02d}/{hoje.year}\n\n"
        for m in metas:
            nome, emoji, limite, gasto = m[1], m[2], m[3], m[4]
            pct = (gasto / limite * 100) if limite > 0 else 0
            barra = _barra_progresso(pct)
            status = "✅" if gasto <= limite else "⚠️"
            texto += f"{status} {emoji} {nome}\n"
            texto += f"   R$ {gasto:.2f} / R$ {limite:.2f} ({pct:.0f}%)\n"
            texto += f"   {barra}\n\n"

        keyboard = [[InlineKeyboardButton("◀ Voltar", callback_data="menu_voltar")]]
        await query.edit_message_text(
            texto,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "menu_ajuda":
        texto = (
            "❓ Ajuda do Finn\n\n"
            "Escolha um topico:"
        )
        keyboard = [
            [InlineKeyboardButton("💰 Gastos", callback_data="ajuda_gastos")],
            [InlineKeyboardButton("💵 Renda", callback_data="ajuda_renda")],
            [InlineKeyboardButton("🏦 Bancos", callback_data="ajuda_bancos")],
            [InlineKeyboardButton("📊 Metas", callback_data="ajuda_metas")],
            [InlineKeyboardButton("📈 Resumo", callback_data="ajuda_resumo")],
            [InlineKeyboardButton("📁 Exportar", callback_data="ajuda_exportar")],
            [InlineKeyboardButton("◀ Voltar", callback_data="menu_voltar")],
        ]
        await query.edit_message_text(
            texto,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data == "menu_voltar":
        texto = (
            "💰 Finn\n"
            "Seu assistente financeiro pessoal."
        )
        keyboard = [
            [InlineKeyboardButton("💰 Gasto", callback_data="menu_gasto"),
             InlineKeyboardButton("💵 Renda", callback_data="menu_renda")],
            [InlineKeyboardButton("📋 Extrato", callback_data="menu_extrato"),
             InlineKeyboardButton("💳 Saldo", callback_data="menu_saldo")],
             [InlineKeyboardButton("🏦 Bancos", callback_data="bancos_menu"),
             InlineKeyboardButton("📊 Metas", callback_data="menu_metas")],
            [InlineKeyboardButton("❓ Ajuda", callback_data="menu_ajuda")],
        ]
        await query.edit_message_text(
            texto,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


def _barra_progresso(pct):
    pct = min(pct, 100)
    preenchido = int(pct / 10)
    vazio = 10 - preenchido
    return "█" * preenchido + "░" * vazio
