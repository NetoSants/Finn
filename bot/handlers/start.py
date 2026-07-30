from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    await update.message.reply_text(
        texto,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
