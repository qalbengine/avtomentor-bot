#!/usr/bin/env python3
"""
Avtotest Online Kurs — Telegram Bot
=====================================
Vazifalar:
  1. Yangi a'zo qo'shilganda xush kelibsiz xabari (guruhga)
  2. Yangi a'zoga 14 kunlik shaxsiy onboarding xabarlari (DM)
  3. Darsga 30 daqiqa qolganda guruhga eslatma
  4. Admin /dars buyrug'i bilan dars qo'shadi
"""

import logging
import json
import os
from datetime import datetime, timedelta

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update, ChatMember
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ChatMemberHandler,
    ContextTypes,
)

# ═══════════════════════════════════════════════════════
#  SOZLAMALAR
# ═══════════════════════════════════════════════════════

BOT_TOKEN       = os.environ["BOT_TOKEN"]
GURUH_ID        = int(os.environ["GURUH_ID"])
ADMIN_USERNAME  = "@avtomentor_admin"
TIMEZONE        = "Asia/Tashkent"
DARSLAR_FILE    = "darslar.json"
ONBOARDING_FILE = "onboarding.json"

# Onboarding xabarlari yuborilish vaqti (har kuni)
ONBOARDING_SOAT   = 9
ONBOARDING_DAQIQA = 0

# ═══════════════════════════════════════════════════════
#  14 KUNLIK ONBOARDING XABARLARI
# ═══════════════════════════════════════════════════════

ONBOARDING_XABARLARI = {
    1: (
        "👋 <b>1-kun: Xush kelibsiz!</b>\n\n"
        "Siz <b>Avtotest Online Kursiga</b> qo'shildingiz! 🎉\n\n"
        "Kurs davomida siz:\n"
        "  ✅ Avtomobilni professional boshqarishni o'rganasiz\n"
        "  ✅ Yo'l qoidalarini mukammal bilasiz\n"
        "  ✅ Imtihonga ishonch bilan kirasiz\n\n"
        "Bugun birinchi darsimizni kutib turing! 🚗"
    ),
    2: (
        "📚 <b>2-kun: Dars jadvali haqida</b>\n\n"
        "Darslar har kuni belgilangan vaqtda o'tkaziladi.\n\n"
        "⏰ Darsdan <b>30 daqiqa oldin</b> guruhda eslatma keladi — "
        "o'sha vaqtda tayyor bo'ling!\n\n"
        "Savol bo'lsa guruhda yozing yoki {admin}ga murojaat qiling 👆"
    ),
    3: (
        "🚦 <b>3-kun: Yo'l belgilari</b>\n\n"
        "Bugun yo'l belgilarini o'rganamiz!\n\n"
        "Bilasizmi? O'zbekistonda <b>4 ta asosiy toifa</b> yo'l belgisi bor:\n"
        "  🔴 Taqiqlovchi — to'xtatadi\n"
        "  🔵 Buyruqchi — majburiylashtiradi\n"
        "  🟡 Ogohlantirishchi — xavf haqida bildiradi\n"
        "  🟢 Ko'rsatkich — yo'nalish beradi\n\n"
        "Bugungi darsda batafsil o'rganamiz! 💪"
    ),
    4: (
        "🚗 <b>4-kun: Haydovchi hujjatlari</b>\n\n"
        "Avtomobil boshqarishda <b>doimo yoningizda</b> bo'lishi kerak:\n\n"
        "  📄 Haydovchilik guvohnomasi\n"
        "  📋 Texnik passport\n"
        "  🛡️ Majburiy sug'urta polisi (OSAGO)\n\n"
        "Hujjatlardan biri yo'q bo'lsa — jarima! Ehtiyot bo'ling 🙏"
    ),
    5: (
        "⛽ <b>5-kun: Yoqilg'i va avtomobil holati</b>\n\n"
        "Har safar yo'lga chiqishdan oldin tekshiring:\n\n"
        "  ✅ Yoqilg'i miqdori\n"
        "  ✅ Shinalar bosimi\n"
        "  ✅ Tormoz suyuqligi\n"
        "  ✅ Chiroqlar ishlashi\n\n"
        "Bu oddiy tekshiruv ko'p muammolarning oldini oladi! 🔧"
    ),
    6: (
        "🅿️ <b>6-kun: To'xtash va park qilish qoidalari</b>\n\n"
        "Ko'pchilik xato qiladigan joy — park qilish!\n\n"
        "Qayerda park qilish <b>MUMKIN EMAS</b>:\n"
        "  ❌ Piyodalar o'tish joyidan 5m yaqin\n"
        "  ❌ Svetofor yaqinida\n"
        "  ❌ Avtobus to'xtash joyida\n"
        "  ❌ Yo'l kesishmasidan 15m yaqin\n\n"
        "Bugungi darsda batafsil! 📍"
    ),
    7: (
        "🎯 <b>7-kun: Birinchi hafta yakuni!</b>\n\n"
        "Bir haftadan beri o'qib kelmoqdasiz — zo'r! 💪\n\n"
        "Shu hafta o'rgandingiz:\n"
        "  ✅ Yo'l belgilari\n"
        "  ✅ Haydovchi hujjatlari\n"
        "  ✅ Avtomobil holati tekshiruvi\n"
        "  ✅ Park qilish qoidalari\n\n"
        "Keyingi hafta yanada qiziqarli mavzular! 🚀\n\n"
        "Savol bo'lsa: {admin}"
    ),
    8: (
        "🛣️ <b>8-kun: Tezlik chegaralari</b>\n\n"
        "O'zbekistonda ruxsat etilgan tezliklar:\n\n"
        "  🏙️ Shahar ichida — <b>70 km/soat</b>\n"
        "  🏘️ Aholi punktida — <b>60 km/soat</b>\n"
        "  🛤️ Magistral yo'llarda — <b>100 km/soat</b>\n"
        "  🚧 Ta'mirlash zonasida — <b>40 km/soat</b>\n\n"
        "Tezlikni oshirish — jarima emas, xavf! ⚠️"
    ),
    9: (
        "🔄 <b>9-kun: Aylanma harakat</b>\n\n"
        "Ko'pchilik chalkashadigan mavzu!\n\n"
        "Aylanma harakatda asosiy qoida:\n"
        "  ➡️ Aylanmada harakatlanayotgan transport <b>ustunlikka ega</b>\n"
        "  🔴 Kirishda yo'l bering\n"
        "  ↪️ Chiqishda o'ng chiroqni yoqing\n\n"
        "Amaliyotda ko'p foydasi tegadi! 🎯"
    ),
    10: (
        "🌧️ <b>10-kun: Yomon ob-havoda haydash</b>\n\n"
        "Yomg'ir, tuman, qor — har birida o'z qoidalari bor:\n\n"
        "  🌧️ Yomg'irda: tezlikni <b>20-30%</b> kamaytiring\n"
        "  🌫️ Tumanda: tumanli chiroqlar, <b>50 km/soat</b> dan oshirmang\n"
        "  ❄️ Qorda: qish shinalar, keskin tormozlamang\n\n"
        "Ob-havo — bahona emas, mas'uliyat! ☔"
    ),
    11: (
        "🚑 <b>11-kun: Birinchi tibbiy yordam</b>\n\n"
        "Haydovchi sifatida bilishingiz shart:\n\n"
        "  🩹 Avtomobilda doimo <b>aptechka</b> bo'lsin\n"
        "  📞 Favqulodda vaziyatda: <b>103</b> (tez yordam)\n"
        "  🚒 Yong'in: <b>101</b>\n"
        "  👮 Yo'l politsiyasi: <b>102</b>\n\n"
        "Raqamlarni telefoningizga saqlang! 📱"
    ),
    12: (
        "📝 <b>12-kun: Imtihon haqida</b>\n\n"
        "Imtihon ikki bosqichdan iborat:\n\n"
        "  1️⃣ <b>Nazariy</b> — 20 ta savol, 18 ta to'g'ri javob kerak\n"
        "  2️⃣ <b>Amaliy</b> — maydonda va shahar bo'ylab haydash\n\n"
        "💡 Maslahat: Har kuni kamida <b>20 ta test</b> ishlang!\n\n"
        "Imtihon sanangiz qachon? Guruhda yozing! 📅"
    ),
    13: (
        "💪 <b>13-kun: Kurs deyarli tugadi!</b>\n\n"
        "Ertaga oxirgi kun — siz juda ko'p narsani o'rgandingiz!\n\n"
        "Imtihonga tayyormisiz? Quyidagilarni tekshiring:\n\n"
        "  ✅ Barcha darslarni ko'rdingizmi?\n"
        "  ✅ Testlarni ishlangizmi?\n"
        "  ✅ Savollarga javob oldingizmi?\n\n"
        "Yo'q bo'lsa — {admin}ga yozing! ⏳"
    ),
    14: (
        "🏆 <b>14-kun: Tabriklaymiz!</b>\n\n"
        "Siz <b>Avtotest Online Kursini</b> muvaffaqiyatli yakunladingiz! 🎉\n\n"
        "Endi:\n"
        "  🚗 Imtihonga ishonch bilan boring\n"
        "  📝 Barcha hujjatlarni tayyorlang\n"
        "  💪 O'zingizga ishoning!\n\n"
        "Imtihon natijangizni guruhda ulashing! 🙌\n\n"
        "Har doim yordam beramiz: {admin}"
    ),
}

# ═══════════════════════════════════════════════════════
#  LOGGING
# ═══════════════════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

TZ = pytz.timezone(TIMEZONE)
scheduler = AsyncIOScheduler(timezone=TZ)

# ═══════════════════════════════════════════════════════
#  DARSLAR — JSON fayl orqali saqlash
# ═══════════════════════════════════════════════════════

def darslarni_yukla() -> list:
    if os.path.exists(DARSLAR_FILE):
        with open(DARSLAR_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []

def darslarni_saqla(darslar: list):
    with open(DARSLAR_FILE, "w", encoding="utf-8") as f:
        json.dump(darslar, f, ensure_ascii=False, indent=2)

# ═══════════════════════════════════════════════════════
#  ONBOARDING — JSON fayl orqali saqlash
# ═══════════════════════════════════════════════════════

def onboardingni_yukla() -> dict:
    if os.path.exists(ONBOARDING_FILE):
        with open(ONBOARDING_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def onboardingni_saqla(data: dict):
    with open(ONBOARDING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def onboarding_qosh(user_id: int, ism: str):
    """Yangi a'zoni onboarding ro'yxatiga qo'shadi."""
    data = onboardingni_yukla()
    user_key = str(user_id)
    if user_key not in data:
        data[user_key] = {
            "ism": ism,
            "boshlangan": datetime.now(TZ).isoformat(),
            "yuborilgan_kunlar": [],
        }
        onboardingni_saqla(data)
        log.info(f"Onboarding boshlandi: {ism} (ID: {user_id})")

def onboarding_belgila(user_id: int, kun: int):
    """Kun yuborilgandan so'ng belgilaydi."""
    data = onboardingni_yukla()
    user_key = str(user_id)
    if user_key in data and kun not in data[user_key]["yuborilgan_kunlar"]:
        data[user_key]["yuborilgan_kunlar"].append(kun)
        onboardingni_saqla(data)

# ═══════════════════════════════════════════════════════
#  ONBOARDING XABAR YUBORISH
# ═══════════════════════════════════════════════════════

async def onboarding_xabar_yuborish(bot, user_id: int, kun: int, ism: str):
    """Foydalanuvchiga DM orqali kunlik onboarding xabarini yuboradi."""
    xabar = ONBOARDING_XABARLARI.get(kun)
    if not xabar:
        return

    xabar = xabar.replace("{admin}", ADMIN_USERNAME)

    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"📅 <b>Avtotest Online Kurs — {kun}-kun</b>\n\n" + xabar,
            parse_mode="HTML",
        )
        onboarding_belgila(user_id, kun)
        log.info(f"Onboarding {kun}-kun yuborildi: {ism} ({user_id})")
    except Exception as e:
        # Foydalanuvchi botni bloklagan bo'lishi mumkin — bu normal holat
        log.warning(f"Onboarding yuborilmadi {ism} ({user_id}): {e}")

async def barcha_onboarding_tekshir(bot):
    """
    Har kuni ONBOARDING_SOAT:ONBOARDING_DAQIQA da ishga tushadi.
    Har bir a'zo uchun qaysi kun xabari yuborilishi kerakligini hisoblaydi.
    """
    data = onboardingni_yukla()
    hozir = datetime.now(TZ)
    log.info(f"Onboarding tekshiruvi boshlandi: {len(data)} ta a'zo")

    for user_id_str, info in data.items():
        user_id = int(user_id_str)
        boshlangan = datetime.fromisoformat(info["boshlangan"])
        o_tgan_kunlar = (hozir - boshlangan).days + 1

        for kun in range(1, min(o_tgan_kunlar + 1, 15)):
            if kun not in info["yuborilgan_kunlar"]:
                await onboarding_xabar_yuborish(bot, user_id, kun, info["ism"])

# ═══════════════════════════════════════════════════════
#  GURUH XABARLARI SHABLONI
# ═══════════════════════════════════════════════════════

def xush_kelibsiz_xabari(ism: str, user_id: int) -> str:
    mention = f'<a href="tg://user?id={user_id}">{ism}</a>'
    return (
        f"👋 Xush kelibsiz, {mention}!\n\n"
        f"Siz <b>Avtotest Online Kursiga</b> qo'shildingiz 🎉\n\n"
        f"📅 Kurs davomida <b>14 kun</b> sizga yordam berishga tayyormiz!\n\n"
        f"❓ Savol yoki muammo bo'lsa:\n"
        f"  • Guruhda yozing — hamkorlar yordam beradi\n"
        f"  • Adminga murojaat qiling: {ADMIN_USERNAME}\n\n"
        f"🚗 Muvaffaqiyatli o'qishlar!"
    )

def eslatma_xabari(dars_nomi: str, dars_vaqti: str) -> str:
    return (
        f"⏰ <b>Eslatma!</b>\n\n"
        f"📚 <b>{dars_nomi}</b> darsiga <b>30 daqiqa</b> qoldi!\n"
        f"🕐 Boshlanish vaqti: <b>{dars_vaqti}</b>\n\n"
        f"Tayyorlaning va o'z vaqtida ulaning 👆"
    )

# ═══════════════════════════════════════════════════════
#  YANGI A'ZO — xush kelibsiz + onboarding boshlash
# ═══════════════════════════════════════════════════════

async def yangi_avo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Guruhga yangi a'zo qo'shilganda ishlaydi."""
    natija = update.chat_member
    if natija is None:
        return

    eski_holat = natija.old_chat_member.status
    yangi_holat = natija.new_chat_member.status

    if eski_holat in (ChatMember.LEFT, ChatMember.BANNED) and \
       yangi_holat in (ChatMember.MEMBER, ChatMember.ADMINISTRATOR):

        foydalanuvchi = natija.new_chat_member.user
        ism = foydalanuvchi.full_name
        user_id = foydalanuvchi.id

        log.info(f"Yangi a'zo: {ism} (ID: {user_id})")

        # 1. Guruhga xush kelibsiz xabari (mention bilan)
        try:
            await ctx.bot.send_message(
                chat_id=GURUH_ID,
                text=xush_kelibsiz_xabari(ism, user_id),
                parse_mode="HTML",
            )
        except Exception as e:
            log.error(f"Guruh xabari xatosi: {e}")

        # 2. Onboarding ro'yxatiga qo'shish
        onboarding_qosh(user_id, ism)

        # 3. 1-kun xabarini darhol DM ga yuborish
        await onboarding_xabar_yuborish(ctx.bot, user_id, 1, ism)

# ═══════════════════════════════════════════════════════
#  ADMIN BUYRUQLARI
# ═══════════════════════════════════════════════════════

async def dars_qosh(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/dars <sana> <vaqt> <dars nomi>"""
    foydalanuvchi = update.effective_user
    try:
        admin_info = await ctx.bot.get_chat_member(GURUH_ID, foydalanuvchi.id)
        if admin_info.status not in (ChatMember.ADMINISTRATOR, ChatMember.OWNER):
            await update.message.reply_text("❌ Faqat adminlar uchun!")
            return
    except Exception:
        await update.message.reply_text("❌ Xato. Bot guruhda admin bo'lishi kerak.")
        return

    if not ctx.args or len(ctx.args) < 3:
        await update.message.reply_text(
            "❗ <b>Foydalanish:</b>\n/dars 2024-12-25 14:00 Dars nomi",
            parse_mode="HTML",
        )
        return

    sana_str  = ctx.args[0]
    vaqt_str  = ctx.args[1]
    dars_nomi = " ".join(ctx.args[2:])

    try:
        dars_dt = TZ.localize(datetime.strptime(f"{sana_str} {vaqt_str}", "%Y-%m-%d %H:%M"))
    except ValueError:
        await update.message.reply_text("❌ Format: <b>YYYY-MM-DD HH:MM</b>", parse_mode="HTML")
        return

    if dars_dt <= datetime.now(TZ):
        await update.message.reply_text("❌ O'tib ketgan vaqt!")
        return

    eslatma_dt = dars_dt - timedelta(minutes=30)
    dars_id = f"dars_{int(dars_dt.timestamp())}"
    darslar = darslarni_yukla()
    darslar.append({
        "id": dars_id,
        "nomi": dars_nomi,
        "vaqt": dars_dt.isoformat(),
        "eslatma_vaqt": eslatma_dt.isoformat(),
    })
    darslarni_saqla(darslar)

    if eslatma_dt > datetime.now(TZ):
        scheduler.add_job(
            eslatma_yuborish,
            trigger="date",
            run_date=eslatma_dt,
            args=[ctx.bot, dars_nomi, dars_dt.strftime("%H:%M")],
            id=dars_id,
            replace_existing=True,
        )

    await update.message.reply_text(
        f"✅ <b>Dars qo'shildi!</b>\n\n"
        f"📚 {dars_nomi}\n"
        f"🕐 {dars_dt.strftime('%Y-%m-%d %H:%M')}\n"
        f"⏰ Eslatma: {eslatma_dt.strftime('%H:%M')} da",
        parse_mode="HTML",
    )

async def darslar_royxati(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    darslar = darslarni_yukla()
    hozir = datetime.now(TZ)
    kelgusi = [d for d in darslar if datetime.fromisoformat(d["vaqt"]) > hozir]

    if not kelgusi:
        await update.message.reply_text("📭 Rejalashtirilgan dars yo'q.")
        return

    qatorlar = ["📅 <b>Kelgusi darslar:</b>\n"]
    for i, d in enumerate(sorted(kelgusi, key=lambda x: x["vaqt"]), 1):
        dt = datetime.fromisoformat(d["vaqt"])
        qatorlar.append(
            f"{i}. 📚 <b>{d['nomi']}</b>\n"
            f"   🕐 {dt.strftime('%Y-%m-%d %H:%M')}\n"
            f"   🆔 <code>{d['id']}</code>"
        )
    await update.message.reply_text("\n\n".join(qatorlar), parse_mode="HTML")

async def dars_ochir(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    foydalanuvchi = update.effective_user
    try:
        admin_info = await ctx.bot.get_chat_member(GURUH_ID, foydalanuvchi.id)
        if admin_info.status not in (ChatMember.ADMINISTRATOR, ChatMember.OWNER):
            await update.message.reply_text("❌ Faqat adminlar uchun!")
            return
    except Exception:
        return

    if not ctx.args:
        await update.message.reply_text("❗ /ochir <dars_id>")
        return

    dars_id = ctx.args[0]
    darslar = darslarni_yukla()
    yangi = [d for d in darslar if d["id"] != dars_id]

    if len(yangi) == len(darslar):
        await update.message.reply_text("❌ Topilmadi.")
        return

    darslarni_saqla(yangi)
    if scheduler.get_job(dars_id):
        scheduler.remove_job(dars_id)
    await update.message.reply_text(f"✅ O'chirildi: <code>{dars_id}</code>", parse_mode="HTML")

async def onboarding_holati(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """/onboarding — admin uchun onboarding holatini ko'rsatadi."""
    foydalanuvchi = update.effective_user
    try:
        admin_info = await ctx.bot.get_chat_member(GURUH_ID, foydalanuvchi.id)
        if admin_info.status not in (ChatMember.ADMINISTRATOR, ChatMember.OWNER):
            await update.message.reply_text("❌ Faqat adminlar uchun!")
            return
    except Exception:
        return

    data = onboardingni_yukla()
    if not data:
        await update.message.reply_text("📭 Hech kim onboardingda yo'q.")
        return

    hozir = datetime.now(TZ)
    qatorlar = [f"👥 <b>Onboarding ({len(data)} kishi):</b>\n"]
    for user_id_str, info in list(data.items())[:20]:
        boshlangan = datetime.fromisoformat(info["boshlangan"])
        o_tgan = (hozir - boshlangan).days + 1
        yuborilgan = len(info["yuborilgan_kunlar"])
        belgi = "✅" if yuborilgan >= 14 else "📅"
        qatorlar.append(f"  {belgi} <b>{info['ism']}</b> — {yuborilgan}/14 xabar")

    await update.message.reply_text("\n".join(qatorlar), parse_mode="HTML")

# ═══════════════════════════════════════════════════════
#  ESLATMA YUBORISH
# ═══════════════════════════════════════════════════════

async def eslatma_yuborish(bot, dars_nomi: str, dars_vaqti: str):
    try:
        await bot.send_message(
            chat_id=GURUH_ID,
            text=eslatma_xabari(dars_nomi, dars_vaqti),
            parse_mode="HTML",
        )
        log.info(f"Eslatma yuborildi: {dars_nomi}")
    except Exception as e:
        log.error(f"Eslatma xatosi: {e}")

# ═══════════════════════════════════════════════════════
#  UMUMIY BUYRUQLAR
# ═══════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>Avtotest Online Kurs Boti</b>\n\n"
        "📌 <b>Admin buyruqlari:</b>\n"
        "  /dars 2024-12-25 14:00 Nomi — dars qo'shish\n"
        "  /darslar — kelgusi darslar\n"
        "  /ochir &lt;id&gt; — darsni o'chirish\n"
        "  /onboarding — a'zolar onboarding holati\n\n"
        "📌 <b>Hammaga ochiq:</b>\n"
        "  /darslar — darslar jadvali\n"
        "  /yordam — admin bilan bog'lanish",
        parse_mode="HTML",
    )

async def yordam(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"❓ <b>Yordam kerakmi?</b>\n\n"
        f"Admin bilan bog'laning: {ADMIN_USERNAME}\n"
        f"yoki guruhda savolingizni yozing 👇",
        parse_mode="HTML",
    )

# ═══════════════════════════════════════════════════════
#  SAQLANGAN DARSLARNI SCHEDULERGA YUKLASH
# ═══════════════════════════════════════════════════════

def saqlangan_darslarni_yukla(bot):
    darslar = darslarni_yukla()
    hozir = datetime.now(TZ)
    qoshildi = 0
    for d in darslar:
        eslatma_dt = datetime.fromisoformat(d["eslatma_vaqt"])
        if eslatma_dt > hozir:
            dars_dt = datetime.fromisoformat(d["vaqt"])
            scheduler.add_job(
                eslatma_yuborish,
                trigger="date",
                run_date=eslatma_dt,
                args=[bot, d["nomi"], dars_dt.strftime("%H:%M")],
                id=d["id"],
                replace_existing=True,
            )
            qoshildi += 1
    log.info(f"Saqlangan {qoshildi} ta dars yuklandi.")

# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",      start))
    app.add_handler(CommandHandler("yordam",     yordam))
    app.add_handler(CommandHandler("dars",       dars_qosh))
    app.add_handler(CommandHandler("darslar",    darslar_royxati))
    app.add_handler(CommandHandler("ochir",      dars_ochir))
    app.add_handler(CommandHandler("onboarding", onboarding_holati))
    app.add_handler(ChatMemberHandler(yangi_avo, ChatMemberHandler.CHAT_MEMBER))

    saqlangan_darslarni_yukla(app.bot)

    # Onboarding: har kuni soat 09:00 da tekshirish
    scheduler.add_job(
        barcha_onboarding_tekshir,
        trigger="cron",
        hour=ONBOARDING_SOAT,
        minute=ONBOARDING_DAQIQA,
        args=[app.bot],
        id="onboarding_kunlik",
        replace_existing=True,
    )

    scheduler.start()
    log.info("✅ Bot ishga tushdi!")

    app.run_polling(
        allowed_updates=["message", "chat_member"],
        drop_pending_updates=True,
    )

if __name__ == "__main__":
    main()
