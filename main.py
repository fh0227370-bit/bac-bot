import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- الإعدادات ---
GEMINI_KEY = "AIzaSyCfnYs_OuYAnUaReQQZgYjqyGSxl39n_Tw"
TELEGRAM_TOKEN = "8662225579:AAFsF-b64L3NpLdLU6EUpDCshXUxyjx86kQ"

# روابط المواد الدراسية لطلاب البكالوريا في الجزائر
SUBJECTS = {
    "العلوم الطبيعية": "https://www.eddirasa.com/science-3as/",
    "الفيزياء": "https://www.eddirasa.com/physics-3as/",
    "الرياضيات": "https://www.eddirasa.com/math-3as/",
    "تقني رياضي ⚙️": "https://www.eddirasa.com/tech-math-3as/",
    "اللغات الأجنبية 🇫🇷🇬🇧": "https://www.eddirasa.com/le-3as/"
}

def get_gemini_response(user_text):
    # التصحيح هنا: استخدام المسار الكامل والمباشر لتجنب خطأ 404
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    headers = {'Content-Type': 'application/json'}
    
    # تنسيق البيانات المطلوب من جوجل
    payload = {
        "contents": [{
            "parts": [{"text": f"أنت أستاذ جزائري خبير في شهادة البكالوريا، أجب على هذا السؤال باختصار ووضوح: {user_text}"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        
        if response.status_code == 200:
            # استخراج النص من رد جوجل بنجاح
            return data['candidates'][0]['content']['parts'][0]['text']
        else:
            # طباعة الخطأ في سجلات Render لمعرفة السبب (Logs)
            print(f"📡 خطأ من جوجل: {response.status_code} - {data}")
            return "عذراً، أحتاج لثانية راحة. أعد إرسال سؤالك من فضلك."
            
    except Exception as e:
        print(f"❌ خطأ تقني: {e}")
        return "⚠️ حدث خطأ في الاتصال بالسيرفر، حاول لاحقاً."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # قائمة الأزرار لتسهيل الاستخدام على الطلاب
    keyboard = [
        ["العلوم الطبيعية", "الفيزياء"],
        ["الرياضيات", "تقني رياضي ⚙️"],
        ["اللغات الأجنبية 🇫🇷🇬🇧", "اسأل الأستاذ المساعد (AI) ✨"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "👋 أهلاً بك في بوت البكالوريا المطور!\n\n"
        "يمكنك الحصول على دروس الشعب العلمية والتقنية، أو طرح أي سؤال على الذكاء الاصطناعي.",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # إذا اختار المستخدم مادة من القائمة
    if text in SUBJECTS:
        await update.message.reply_text(f"🔗 إليك روابط مادة {text}:\n{SUBJECTS[text]}")
        return

    # إذا ضغط على زر المساعد
    if text == "اسأل الأستاذ المساعد (AI) ✨":
        await update.message.reply_text("أنا أسمعك، ما هو سؤالك العلمي أو الأدبي؟")
        return

    # إرسال النص إلى الذكاء الاصطناعي مع إظهار حالة "يكتب الآن..."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    response = get_gemini_response(text)
    await update.message.reply_text(response)

def main():
    print("🚀 البوت يعمل الآن على السيرفر...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # تشغيل البوت بنظام Polling
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
