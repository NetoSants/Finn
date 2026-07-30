import io
import csv
import logging
from datetime import date
from telegram import Update
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


async def exportar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    hoje = date.today()

    if context.args and len(context.args) >= 2:
        try:
            mes = int(context.args[0])
            ano = int(context.args[1])
        except ValueError:
            await update.message.reply_text("Uso: /exportar [mes] [ano]\nEx: /exportar 07 2026")
            return
        if not (1 <= mes <= 12):
            await update.message.reply_text("Mes invalido. Use 1-12.")
            return
        rows = repository.listar_transacoes_periodo(user_id, mes, ano, limite=500)
        nome_mes = f"{mes:02d}_{ano}"
    else:
        rows = repository.listar_transacoes_csv(user_id)
        nome_mes = f"tudo_{hoje.strftime('%Y%m%d')}"

    if not rows:
        await update.message.reply_text("Nenhuma transacao para exportar.")
        return

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Tipo", "Valor", "Descricao", "Pagamento", "Data", "Categoria", "Emoji"])

    for row in rows:
        tipo, valor, descricao, pagamento, data_transacao, cat_nome, cat_emoji = row[:7]
        data_str = data_transacao.strftime('%d/%m/%Y') if data_transacao else ""
        writer.writerow([tipo, f"{valor:.2f}", descricao or "", pagamento or "", data_str, cat_nome or "", cat_emoji or ""])

    output.seek(0)
    bio = io.BytesIO(output.getvalue().encode('utf-8-sig'))
    bio.name = f"finn_{nome_mes}.csv"

    await update.message.reply_document(
        document=bio,
        caption=f"📊 Exportacao Finn — {len(rows)} transacoes"
    )
