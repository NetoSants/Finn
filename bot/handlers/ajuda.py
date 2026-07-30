from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def ajuda_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "ajuda_gastos":
        texto = (
            "💰 Registrar gastos\n\n"
            "Use o comando:\n"
            "  /gasto - fluxo passo a passo\n\n"
            "Ou direto:\n"
            "  /gasto 50 almoco debito\n\n"
            "O bot vai perguntar:\n"
            "1 Valor\n"
            "2 Descricao\n"
            "3 Categoria\n"
            "4 Forma de pagamento"
        )

    elif data == "ajuda_renda":
        texto = (
            "💵 Registrar renda\n\n"
            "Use o comando:\n"
            "  /renda - fluxo passo a passo\n\n"
            "Ou direto:\n"
            "  /renda 2000 salario"
        )

    elif data == "ajuda_bancos":
        texto = (
            "🏦 Gerenciar bancos\n\n"
            "/bancos - lista e gerencia seus bancos\n"
            "Use o menu interativo para adicionar ou remover."
        )

    elif data == "ajuda_metas":
        texto = (
            "📊 Metas mensais\n\n"
            "Defina um limite por categoria:\n"
            "  /meta [categoria] [limite]\n"
            "  Ex: /meta alimentacao 800\n\n"
            "Veja o progresso com barras visuais:\n"
            "  Dentro do limite\n"
            "  Ultrapassou o limite"
        )

    elif data == "ajuda_resumo":
        texto = (
            "📈 Resumo mensal\n\n"
            "Veja insights automaticos:\n"
            "  Gastos por categoria\n"
            "  Maior gasto do mes\n"
            "  Media diaria\n"
            "  Ratio gasto/renda\n\n"
            "  /resumo - mes atual\n"
            "  /resumo 07 2026 - mes especifico"
        )

    elif data == "ajuda_exportar":
        texto = (
            "📁 Exportar CSV\n\n"
            "Exporta todas as transacoes:\n"
            "  /exportar - tudo\n"
            "  /exportar 07 2026 - mes especifico\n\n"
            "Gera um arquivo .csv compativel\n"
            "com Excel, Google Sheets, etc."
        )

    else:
        return

    keyboard = [[InlineKeyboardButton("◀ Voltar", callback_data="menu_ajuda")]]
    await query.edit_message_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
