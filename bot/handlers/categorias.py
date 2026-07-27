import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cats = repository.listar_categorias()

    if not cats:
        await update.message.reply_text("Nenhuma categoria cadastrada.")
        return

    lines = ["📂 Categorias disponíveis:\n"]
    for cat in cats:
        emoji = cat[2] if cat[2] else ""
        lines.append(f"  {emoji} {cat[1]}")

    lines.append("\nUse: /gasto [valor] [descricao]")
    lines.append("A categoria sera selecionada por botoes apos o comando.")

    await update.message.reply_text("\n".join(lines))
