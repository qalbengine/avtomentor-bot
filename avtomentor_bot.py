#!/usr/bin/env python3
"""
Avtomentor Telegram Bot
Avtotest kursi uchun avtomatik sotish boti
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# =============================================
# TOKEN — Railway environment variable dan olinadi
# =============================================
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Admin Telegram username (@ siz)
ADMIN_USERNAME = "@avtomentor_admin"

# Kursga yozilish linki
KURS_LINK = "https://t.me/avtomentor_admin"

# To'lov karta raqami
KARTA = "9860100126865797"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================
# MATNLAR
# =============================================

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
🎁 <b>1-dars bepul</b> — yoqmasa pul qaytariladi!

Kursga yozilish uchun tugmani bosing 👇"""

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
👉 Yechim: Kamida 100 ta test ishlang — mashq qiling!

━━━━━━━━━━━━━━━
💡 <b>Bizning kursda bularning barchasi o'rgatiladi!</b>

14 kun ichida kafolat bilan o'ting 👇"""

YOZILISH_MATNI = """✅ <b>KURSGA YOZILISH</b>

Quyidagi bosqichlarni bajaring:

1️⃣ Kartaga to'lov qiling:
💳 <code>{karta}</code>
💵 Summa: <b>600,000 so'm</b>

2️⃣ To'lov chekini (skrinshot) adminga yuboring:
👉 {admin}

3️⃣ Admin sizni guruhga qo'shadi va darslar boshlanadi!

━━━━━━━━━━━━━━━
❓ Savollar bo'lsa: {admin}""".format(karta=KARTA, admin=ADMIN_USERNAME)

NATIJALAR_MATNI = """🏆 <b>O'QUVCHILAR NATIJALARI</b>

✅ Bizning kursdan o'tgan o'quvchilar:

👤 <i>"14 kunda o'tdim, 3 marta urinib ko'rgan edim oldin"</i>
👤 <i>"Kafolat haqiqat ekan, test ishlagandan keyin oson bo'ldi"</i>
👤 <i>"Online format juda qulay, uydan turib tayyorlandim"</i>

📊 Statistika:
• 500+ o'quvchi
• 95%+ muvaffaqiyat darajasi
• 14 kun — minimal vaqt

Siz ham qo'shiling! 👇"""

# =============================================
# TUGMALAR
# =============================================

def main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📚 Kurs haqida", callback_data="kurs_haqida"),
            InlineKeyboardButton("🎁 Bepul dars", callback_data="bepul_dars"),
        ],
        [
            InlineKeyboardButton("🏆 Natijalar", callback_data="natijalar"),
            InlineKeyboardButton("✅ Yozilish", callback_data="yozilish"),
        ],
        [
            InlineKeyboardButton("📞 Admin bilan bog'lanish", url=f"https://t.me/avtomentor_admin"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_keyboard():
    keyboard = [
        [InlineKeyboardButton("✅ Kursga yozilish", callback_data="yozilish")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga")],
    ]
    return InlineKeyboardMarkup(keyboard)

def yozilish_keyboard():
    keyboard = [
        [InlineKeyboardButton("📞 Adminga yozish", url="https://t.me/avtomentor_admin")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="orqaga")],
    ]
    return InlineKeyboardMarkup(keyboard)

# =============================================
# HANDLERLAR
# =============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Yangi foydalanuvchi: {user.first_name} (@{user.username})")
    
    await update.message.reply_text(
        SALOM_MATNI,
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "kurs_haqida":
        await query.edit_message_text(
            KURS_HAQIDA_MATNI,
            parse_mode="HTML",
            reply_markup=back_keyboard()
        )
    
    elif query.data == "bepul_dars":
        await query.edit_message_text(
            BEPUL_DARS_MATNI,
            parse_mode="HTML",
            reply_markup=back_keyboard()
        )
    
    elif query.data == "natijalar":
        await query.edit_message_text(
            NATIJALAR_MATNI,
            parse_mode="HTML",
            reply_markup=back_keyboard()
        )
    
    elif query.data == "yozilish":
        await query.edit_message_text(
            YOZILISH_MATNI,
            parse_mode="HTML",
            reply_markup=yozilish_keyboard()
        )
    
    elif query.data == "orqaga":
        await query.edit_message_text(
            SALOM_MATNI,
            parse_mode="HTML",
            reply_markup=main_keyboard()
        )

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Har qanday matn kelsa - asosiy menyuni ko'rsatish"""
    await update.message.reply_text(
        SALOM_MATNI,
        parse_mode="HTML",
        reply_markup=main_keyboard()
    )

# =============================================
# ISHGA TUSHIRISH
# =============================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    print("✅ Avtomentor bot ishga tushdi!")
    print("To'xtatish uchun: Ctrl+C")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
