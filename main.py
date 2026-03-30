import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات (تأكد من بقاء المفاتيح كما هي) ---
GEMINI_KEY = "AIzaSyCfnYs_OuYAnUaReQQZgYjqyGSxl39n_Tw"
TELEGRAM_TOKEN = "8662225579:AAFsF-b64L3NpLdLU6EUpDCshXUxyjx86kQ"

# روابط المواد الدراسية (الجزائر)
SUBJECTS = {
    "العلوم الطبيعية": "https://www.eddirasa.com/science-3as/",
    "الفيزياء": "https://www.eddirasa.com/physics-3as/",
    "الرياضيات": "https://www.eddirasa.com/math-3as/",
    "تقني رياضي ⚙️": "https://www.eddirasa.com/tech-math-3as/",
    "اللغات الأجنبية 🇫🇷🇬🇧": "https://www.eddirasa.com/le-3as/"
}

def get_gemini_response(user_text):
    # استخدام الرابط المباشر v1beta لضمان التوافق مع الاستضافة الخارجية
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": f"أجب كأستاذ بكالوريا جزائري خبير، باختصار ووضوح: {user_text}"}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        if response.status_code == 200:
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            # طباعة الخطأ في سجلات السيرفر (Logs) للمراقبة
            print(f"📡 السيرفر رد بخطأ: {response.status_code}")
            return "عذراً، أواجه ضغطاً حالياً. أعد إرسال سؤالك."
    except Exception as e:
        print(f"❌ خطأ تقني: {e}")
        return "⚠️ حدث خطأ في الاتصال، حاول لاحقاً."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["العلوم الطبيعية", "الفيزياء"],
        ["الرياضيات", "تقني رياضي ⚙️"],
        ["اللغات الأجنبية 🇫🇷🇬🇧", "اسأل الأستاذ المساعد (AI) ✨"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🚀 أهلاً بك في بوت البكالوريا!\n"
        "تم ضبط الإعدادات لتعمل 24/7.\n"
        "اختر مادة أو اطرح سؤالك الدراسي.",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # 1. التحقق إذا كان المستخدم اختار مادة من القائمة
    if text in SUBJECTS:
        await update.message.reply_text(f"🔗 إليك روابط دروس {text}:\n{SUBJECTS[text]}")
        return

    # 2. التحقق من زر الذكاء الاصطناعي
    if text == "اسأل الأستاذ المساعد (AI) ✨":
        await update.message.reply_text("أنا معك، ما هو سؤالك العلمي أو الأدبي؟")
        return

    # 3. إرسال أي نص آخر إلى Gemini AI
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    answer = get_gemini_response(text)
    await update.message.reply_text(answer)

def main():
    print("🚀 البوت في طور التشغيل الآن...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # إضافة الأوامر
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # بدء العمل
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
