from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot import repository


def _pagamento_label(pagamento, banco_id=None):
    labels = {
        "debito": "💳 Debito",
        "credito": "💳 Credito",
        "pix": "⚡ Pix",
    }
    label = labels.get(pagamento, pagamento)
    if banco_id:
        banco = repository.buscar_categoria_por_id(banco_id)
        if banco:
            label += f" - {banco[1]}"
    return label


def _barra_saldo(saldo):
    if saldo > 0:
        return f"🟢 Positivo"
    elif saldo < 0:
        return f"🔴 Negativo"
    return "⚪ Zero"


async def confirmacao_gasto(query, user, valor, descricao, categoria_id, pagamento, banco_id=None, parcelas=1):
    total_gastos = repository.total_gastos(user.id)
    total_rendas = repository.total_rendas(user.id)
    saldo = total_rendas - total_gastos
    hoje = repository.gastos_hoje(user.id)

    cat = repository.buscar_categoria_por_id(categoria_id) if categoria_id else None
    cat_text = f"{cat[2]} {cat[1]}" if cat else "📦 Outros"

    parc_text = ""
    if parcelas and parcelas > 1:
        parc_val = valor / parcelas
        parc_text = f"\n📦 {parcelas}x R$ {parc_val:.2f}"

    texto = (
        f"✅ Gasto registrado!\n\n"
        f"💰 R$ {valor:.2f}\n"
        f"📝 {descricao}\n"
        f"🏷️ {cat_text}\n"
        f"💳 {_pagamento_label(pagamento, banco_id)}{parc_text}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 Resumo\n"
        f"💰 Saldo: R$ {_format(saldo)} {_barra_saldo(saldo)}\n"
        f"💸 Gastos hoje: R$ {_format(hoje)}"
    )

    keyboard = [[
        InlineKeyboardButton("🏠 Inicio", callback_data="menu_voltar"),
        InlineKeyboardButton("💰 Outro gasto", callback_data="menu_gasto"),
    ]]
    await query.edit_message_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def confirmacao_renda(message, user, valor, descricao):
    total_gastos = repository.total_gastos(user.id)
    total_rendas = repository.total_rendas(user.id)
    saldo = total_rendas - total_gastos

    texto = (
        f"✅ Renda registrada!\n\n"
        f"💵 R$ {valor:.2f}\n"
        f"📝 {descricao}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 Resumo\n"
        f"💰 Saldo: R$ {_format(saldo)} {_barra_saldo(saldo)}"
    )

    keyboard = [[
        InlineKeyboardButton("🏠 Inicio", callback_data="menu_voltar"),
        InlineKeyboardButton("💵 Outra renda", callback_data="menu_renda"),
    ]]
    await message.reply_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def _format(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
