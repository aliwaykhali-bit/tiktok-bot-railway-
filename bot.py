import os
import re
import logging
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", 8828210338:"AAHFEzHiYWrcfXQ0A7_rFF6oA8m9-UwY7kk")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بك في بوت تحميل TikTok!\n\n"
        "📌 أرسل لي رابط فيديو TikTok وأنا أحمله لك بدون علامة مائية."
    )

def is_tiktok_url(text: str) -> bool:
    patterns = [
        r"https?://(www\.)?tiktok\.com/@[\w.-]+/video/\d+",
        r"https?://vm\.tiktok\.com/\w+",
        r"https?://vt\.tiktok\.com/\w+",
    ]
    return any(re.search(p, text) for p in patterns)

def extract_tiktok_video(url: str):
    try:
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            title = info.get('title', 'TikTok Video')
            if video_url:
                return {"success": True, "video_url": video_url, "title": title}
            else:
                return {"success": False, "error": "لم أجد رابط الفيديو"}
    except Exception as e:
        logger.error(f"yt-dlp error: {e}")
        return {"success": False, "error": "خطأ في استخراج الفيديو"}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if not is_tiktok_url(text):
        await update.message.reply_text("❌ رابط TikTok غير صحيح!")
        return
    
    processing_msg = await update.message.reply_text("⏳ جاري التحميل...")
    
    try:
        result = extract_tiktok_video(text)
        if not result["success"]:
            await processing_msg.edit_text(f"❌ {result['error']}")
            return
        
        await processing_msg.edit_text("📤 جاري الإرسال...")
        
        await update.message.reply_video(
            video=result["video_url"],
            caption=f"✅ {result['title'][:200]}\n\n🤖 بوت تحميل TikTok",
            supports_streaming=True
        )
        await processing_msg.delete()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await processing_msg.edit_text("❌ حدث خطأ، جرب رابط آخر")

def main():
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN غير موجود!")
        return
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ البوت يعمل...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
