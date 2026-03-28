#!/usr/bin/env python3
import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("bot_token", "")
ADMIN_USERNAME = "@avtomentor_admin"
KARTA = "9860100126865797"

SALOM_MATNI = """👋 Assalomu alaykum!

🚗 <b>Avtomentor</b> ga xush kelibsiz!

Avtotest imtihonidan o'ta olmayapsizmi?
Biz sizga yordam beramiz! ✅

Quyidagilardan birini tanlang:"""

KURS_HAQIDA_MATNI = """🎓 <b>AVTOTEST KURSI — TO'LIQ MA'LUMOT</b>

📅 <b>Dars vaqti:</b> Har kuni (Du-Sha)
🕗 <b>Soat:</b> 20:00 — 22:00
📹 <b>Format:</b> Google Meet (jonli dars)

✅ <b>Kurs davomiyligi:</b> 14 kun
🏆 <b>Kafolat:</b> Barcha vazifani bajarsangiz — 100% o'tasiz!

📚 <b>Nimalar kiradi:</b>
• Har kungi video dars
• avtomentorpro.uz da test ishlash
• Natijalar avtomatik tekshiriladi
• Guruh a'zoligi

💵 <b>Narx:</b> 600,000 so'm
🎁 <b>1-dars bepul</b> — yoqmasa pul qaytariladi!"""

BEPUL_DARS_MATNI = """🎁 <b>BEPUL DARS — IMTIHON SIRLARI</b>

Avtotest imtihonida ko'p xato qilinadigan <b>3 ta muhim narsa:</b>

1️⃣ <b>Vaqt bosimi</b>
Ko'pchilik shoshib noto'g'ri javob bosadi.
👉 Yechim: Har bir savolga max 30 soniya ajrating

2️⃣ <b>O'xshash savollar</b>
Ba'zi savollar deyarli bir xil, lekin javobi boshqa.
👉 Yechim: Kalit so'zlarga e'tibor bering

3️⃣ <b>Asab va hayajon</b>
Bilsangiz ham hayajondan unutasiz.
👉 Yechim: Kamida 100 ta test ishlang!

💡 <b>Bizning kursda bularning barchasi o'rgatiladi!</b>"""

NATIJALAR_MATNI = """🏆 <b>O'QUVCHILAR NATIJALARI</b>

✅ Bizning kursdan o'tgan o'quvchilar:

👤 <i>"14 kunda o'tdim, 3 marta urinib ko'rgan edim oldin"</i>
👤 <i>"Kafolat haqiqat ekan, test ishlagandan keyin oson bo'ldi"</i>
👤 <i>"Online format juda qulay, uydan turib tayyorlandim"</i>

📊 <b>Statistika:</b>
• 500+ o'quvchi
• 95%+ muvaffaqiyat darajasi
• 14 kun — minimal vaqt"""

YOZILISH_MATNI = f"""✅ <b>KURSGA YOZILISH</b>

1️⃣ Kartaga to'lov qiling:
💳 <code>{KARTA}</code>
💵 Summa: <b>600,000 so'm</b>

2️⃣ To'lov chekini (skrinshot) adminga yuboring:
👉 {ADMIN_USERNAME}

3️⃣ Admin sizni guruhga qo'shadi!

❓ Savollar bo'lsa: {ADMIN_USERNAME}"""

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Kurs haqida", callback_data="kurs"),
         InlineKeyboardButton("🎁 Bepul dars", callback_data="bepul")],
        [InlineKeyboardButton("🏆 Natijalar", callback_data="natija"),
         InlineKeyboardButton("✅ Yozilish", callback_data="yozil")],
        [InlineKeyboardButton("📞 Admin", url="https://t.me/avtomentor_admin")],
    ])

def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Kursga yozilish", callback_data="yozil")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="bosh")],
    ])

def yozilish_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Adminga yozish", url="https://t.me/avtomentor_admin")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="bosh")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(SALOM_MATNI, parse_mode="HTML", reply_markup=main_keyboard())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "kurs":
        await q.edit_message_text(KURS_HAQIDA_MATNI, parse_mode="HTML", reply_markup=back_keyboard())
    elif q.data == "bepul":
        await q.edit_message_text(BEPUL_DARS_MATNI, parse_mode="HTML", reply_markup=back_keyboard())
    elif q.data == "natija":
        await q.edit_message_text(NATIJALAR_MATNI, parse_mode="HTML", reply_markup=back_keyboard())
    elif q.data == "yozil":
        await q.edit_message_text(YOZILISH_MATNI, parse_mode="HTML", reply_markup=yozilish_keyboard())
    elif q.data == "bosh":
        await q.edit_message_text(SALOM_MATNI, parse_mode="HTML", reply_markup=main_keyboard())

async def text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(SALOM_MATNI, parse_mode="HTML", reply_markup=main_keyboard())

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text))
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
