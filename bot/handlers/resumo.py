import logging
import calendar
from datetime import date
from telegram import Update
from telegram.ext import ContextTypes
from bot import repository

logger = logging.getLogger(__name__)


def _format(valor):
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _barra(pct):
    pct = min(pct, 100)
    preenchido = int(pct / 10)
    return "█" * preenchido + "░" * (10 - preenchido)


async def resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    hoje = date.today()

    if context.args and len(context.args) >= 2:
        try:
            mes = int(context.args[0])
            ano = int(context.args[1])
        except ValueError:
            await update.message.reply_text("Uso: /resumo [mes] [ano]\nEx: /resumo 07 2026")
            return
        if not (1 <= mes <= 12):
            await update.message.reply_text("Mes invalido. Use 1-12.")
            return
    else:
        mes = hoje.month
        ano = hoje.year

    total_g = repository.total_gastos_periodo(user_id, mes, ano)
    total_r = repository.total_rendas_periodo(user_id, mes, ano)
    saldo = total_r - total_g
    cat = repository.gasto_por_categoria(user_id, mes, ano)
    maior = repository.maior_gasto(user_id, mes, ano)
    dias = repository.dias_com_gastos(user_id, mes, ano)
    dias_no_mes = calendar.monthrange(ano, mes)[1]
    media = total_g / dias if dias > 0 else 0

    nome_mes = [
        "", "Janeiro", "Fevereiro", "Marco", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ][mes]

    texto = f"📊 Resumo — {nome_mes}/{ano}\n\n"
    texto += f"💰 Renda: R$ {_format(total_r)}\n"
    texto += f"💸 Gastos: R$ {_format(total_g)}\n"

    if total_r > 0:
        pct_gasto = (total_g / total_r * 100)
        texto += f"📉 Gasto/Renda: {pct_gasto:.0f}% {_barra(pct_gasto)}\n"

    texto += f"💳 Saldo: R$ {_format(saldo)}\n\n"

    if cat:
        texto += "📋 Por categoria:\n"
        for c in cat:
            nome, emoji, total = c[0], c[1], c[2]
            pct = (total / total_g * 100) if total_g > 0 else 0
            texto += f"  {emoji} {nome}: R$ {_format(total)} ({pct:.0f}%)\n"
        texto += "\n"

    if maior:
        m_valor, m_desc, m_data = maior
        texto += f"🏆 Maior gasto: R$ {_format(m_valor)} — {m_desc}"
        if m_data:
            texto += f" ({m_data.strftime('%d/%m')})"
        texto += "\n"

    texto += f"📅 Dias com gastos: {dias}/{dias_no_mes}\n"
    texto += f"📉 Media diaria: R$ {_format(media)}"

    await update.message.reply_text(texto)
