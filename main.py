import telebot
from config import BOT_TOKEN, ILOVE_PUBLIC_KEY, ILOVE_SECRET_KEY, TEMP_DIR
from services.ilovepdf_service import ILovePDFClient
from bot.handlers import register_handlers
from utils.file_manager import ensure_temp_dir

# Initialize
bot = telebot.TeleBot(BOT_TOKEN)
api_client = ILovePDFClient(ILOVE_PUBLIC_KEY, ILOVE_SECRET_KEY)

# Create temp directory
ensure_temp_dir(TEMP_DIR)

# Register all handlers
register_handlers(bot, api_client)

if __name__ == '__main__':
    print("🤖 Bot is starting...")
    if api_client.get_token():
        print("✅ Bot is ready and running!")
        bot.infinity_polling()
    else:
        print("❌ Failed to authenticate with iLovePDF!")