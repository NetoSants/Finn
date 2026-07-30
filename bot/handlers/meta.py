import logging
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def meta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    hoje = date.today()

    if context.args and len(context.args) >= 2:
        try:
            categoria_nome = context.args[0]
            limite = float(context.args[1].replace(',', '.'))
        except ValueError:
            await update.message.reply_text("Uso: /meta [categoria] [limite]\nEx: /meta alimentação 800")
            return

        cat = repository.buscar_categoria_por_nome(categoria_nome)
        if not cat:
            await update.message.reply_text(f"Categoria '{categoria_nome}' nao encontrada.\nUse /categorias para ver as disponiveis.")
            return

        repository.definir_meta(cat[0], hoje.month, hoje.year, limite, user.id)

        await update.message.reply_text(
            f"Meta definida!\n"
            f"{cat[2]} {cat[0]}: R$ {limite:.2f}/{hoje.month:02d}/{hoje.year}"
        )
        return

    metas = repository.listar_metas(hoje.month, hoje.year, user.id)

    if not metas:
        await update.message.reply_text(
            "Nenhuma meta definida para este mes.\n\n"
            "Use: /meta [categoria] [limite]\n"
            "Ex: /meta alimentação 800"
        )
        return

    lines = [f"📊 Metas de {hoje.month:02d}/{hoje.year}\n"]
    for m in metas:
        nome, emoji, limite, gasto = m[1], m[2], m[3], m[4]
        pct = (gasto / limite * 100) if limite > 0 else 0
        barra = _barra_progresso(pct)
        status = "✅" if gasto <= limite else "⚠️"
        lines.append(f"{status} {emoji} {nome}")
        lines.append(f"   R$ {gasto:.2f} / R$ {limite:.2f} ({pct:.0f}%)")
        lines.append(f"   {barra}")
        lines.append("")

    keyboard = [[InlineKeyboardButton("◀ Voltar", callback_data="menu_voltar")]]
    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def _barra_progresso(pct):
    pct = min(pct, 100)
    preenchido = int(pct / 10)
    vazio = 10 - preenchido
    return "█" * preenchido + "░" * vazio
