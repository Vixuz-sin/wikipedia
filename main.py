import sys
import telebot
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import os
import logging

# Loglashni sozlash
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Muhit o'zgaruvchilarini yuklash
load_dotenv()

# Bot konfiguratsiyasi
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Foydalanuvchilar til sozlamalari
user_language = {}
SUPPORTED_LANGUAGES = {
    'uz': 'Uzbek',
    'en': 'English',
    'ru': 'Russian'
}

# Tillar va bayroqlar
lang_flags = {
    'uz': '🇺🇿',
    'en': '🇬🇧',
    'ru': '🇷🇺'
}

# Start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(
        telebot.types.KeyboardButton("🇺🇿 Uzbek"),
        telebot.types.KeyboardButton("🇬🇧 English"),
        telebot.types.KeyboardButton("🇷🇺 Russian")
    )
    text = "Assalomu alaykum! Tarjimon botga xush kelibsiz.\nTarjima qilish tilini tanlang:"
    bot.send_message(message.chat.id, text, reply_markup=markup)
    logger.info(f"Foydalanuvchi {message.chat.id} botni ishga tushirdi")

# Til sozlash komandasi
@bot.message_handler(commands=["setlang"])
def set_language(message: telebot.types.Message):
    """Handle language setting command"""
    try:
        args = message.text.split()

        if len(args) < 2:
            bot.reply_to(message, "⚠️ Please enter a language code!\nExample: /setlang en")
            return

        lang_code = args[1].lower()
        if lang_code not in SUPPORTED_LANGUAGES:
            valid_codes = ", ".join(SUPPORTED_LANGUAGES.keys())
            bot.reply_to(message, f"❌ Invalid language code! Supported languages:\n{valid_codes}")
            return

        user_id = message.from_user.id
        user_language[user_id] = lang_code
        lang_name = SUPPORTED_LANGUAGES[lang_code]
        bot.reply_to(message, f"✅ Translation language changed to {lang_name}!")

    except Exception as e:
        logger.error("Error in set_language: %s", e, exc_info=True)
        bot.reply_to(message, "❌ An error occurred while changing language. Please try again.")

# Matnni qayta ishlash
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id

    # Tilni o'zgartirish
    if message.text in ["🇺🇿 Uzbek", "🇬🇧 English", "🇷🇺 Russian"]:
        if message.text == "🇺🇿 Uzbek":
            user_language[chat_id] = 'uz'
            response = "Tarjima qilish tili 🇺🇿 Uzbek o'zgartirildi"
        elif message.text == "🇬🇧 English":
            user_language[chat_id] = 'en'
            response = "Tarjima qilish tili 🇬🇧 English o'zgartirildi"
        else:
            user_language[chat_id] = 'ru'
            response = "Tarjima qilish tili 🇷🇺 Russian o'zgartirildi"

        bot.send_message(chat_id, response)
        logger.info(f"Foydalanuvchi {chat_id} tilni {user_language[chat_id]} ga o'zgartirdi")

    # Matnni tarjima qilish
    else:
        target_lang = user_language.get(chat_id, 'uz')
        try:
            translated = GoogleTranslator(source='auto', target=target_lang).translate(message.text)
            flag = lang_flags.get(target_lang, '🇺🇿')
            bot.reply_to(message, f"{flag} Tarjima:\n{translated}")
            logger.info(f"Tarjima qilindi: {message.text} -> {translated} ({target_lang})")
        except Exception as e:
            bot.reply_to(message, f"Xato yuz berdi: {e}\nQayta urinib ko'ring.")
            logger.error(f"Xato: {str(e)}")


# Botni ishga tushirish
if __name__ == "__main__":
    logger.info("Bot ishga tushdi...")
    bot.polling(none_stop=True)
