import os
from telebot import types
from config import TEMP_DIR
from utils.file_manager import cleanup_files

# Dictionary to store user states (Shared across this module)
user_data = {}

def register_handlers(bot, api_client):
    
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        welcome_text = """
🤖 Welcome to PDF Converter Bot!

I can help you with various PDF operations:

📄 /compress - Compress PDF files
🔄 /convert - Convert Office files to PDF
🖼️ /imagetopdf - Convert images to PDF
📑 /merge - Merge multiple PDFs
✂️ /split - Split PDF into pages
🔓 /unlock - Remove PDF password
🔒 /protect - Add password to PDF
💧 /watermark - Add watermark to PDF
🔢 /pagenumbers - Add page numbers
📝 /pdftojpg - Convert PDF to JPG
🔄 /rotate - Rotate PDF pages
🔧 /repair - Repair damaged PDF

Send me a file and choose an operation!
"""
        bot.reply_to(message, welcome_text)

    # Command handlers (compress, convert, etc.)
    @bot.message_handler(commands=['compress'])
    def compress_pdf(message):
        bot.reply_to(message, "📄 Send me a PDF file to compress.")
        user_data[message.chat.id] = {'action': 'compress', 'files': []}

    @bot.message_handler(commands=['convert'])
    def convert_to_pdf(message):
        bot.reply_to(message, "🔄 Send me an Office file (Word, Excel, PowerPoint) to convert to PDF.")
        user_data[message.chat.id] = {'action': 'officepdf', 'files': []}

    @bot.message_handler(commands=['imagetopdf'])
    def image_to_pdf(message):
        bot.reply_to(message, "🖼️ Send me image files to convert to PDF. Send /done when finished.")
        user_data[message.chat.id] = {'action': 'imagepdf', 'files': []}

    # ... بقیه دستورات (merge, split, unlock, ...) دقیقاً مشابه کد خودتان اینجا قرار می‌گیرد ...
    # برای جلوگیری از طولانی شدن، منطق کلی را حفظ کنید:
    @bot.message_handler(commands=['merge'])
    def merge_pdfs(message):
        bot.reply_to(message, "📑 Send me multiple PDF files to merge. Send /done when finished.")
        user_data[message.chat.id] = {'action': 'merge', 'files': []}

    @bot.message_handler(commands=['done'])
    def process_files_cmd(message):
        chat_id = message.chat.id
        if chat_id not in user_data:
            bot.reply_to(message, "❌ No operation in progress. Use a command first!")
            return
        
        action = user_data[chat_id].get('action')
        files = user_data[chat_id].get('files', [])
        
        if action in ['merge', 'imagepdf'] and len(files) < 2:
            bot.reply_to(message, f"❌ Please send at least 2 files for {action}.")
            return
        
        if not files:
            bot.reply_to(message, "❌ No files uploaded yet!")
            return
        
        process_files(message, action, files)

    @bot.message_handler(content_types=['document'])
    def handle_document(message):
        chat_id = message.chat.id
        if chat_id not in user_data:
            bot.reply_to(message, "Please select an operation first using the commands above.")
            return
        
        action = user_data[chat_id].get('action')
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        filename = f"{chat_id}_{len(user_data[chat_id]['files'])}_{message.document.file_name}"
        file_path = os.path.join(TEMP_DIR, filename)
        
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        
        user_data[chat_id]['files'].append(file_path)
        
        if action in ['merge', 'imagepdf']:
            bot.reply_to(message, f"✅ File added! Total: {len(user_data[chat_id]['files'])}\nSend more or /done to process.")
        else:
            process_files(message, action, [file_path])

    @bot.message_handler(content_types=['photo'])
    def handle_photo(message):
        chat_id = message.chat.id
        if chat_id not in user_data or user_data[chat_id].get('action') != 'imagepdf':
            bot.reply_to(message, "Please use /imagetopdf first.")
            return
        
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        filename = f"{chat_id}_{len(user_data[chat_id]['files'])}__image.jpg"
        file_path = os.path.join(TEMP_DIR, filename)
        
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        
        user_data[chat_id]['files'].append(file_path)
        bot.reply_to(message, f"✅ Image added! Total: {len(user_data[chat_id]['files'])}\nSend more or /done to convert.")

    def process_files(message, tool, files):
        chat_id = message.chat.id
        status_msg = bot.reply_to(message, f"⏳ Processing your {tool} request...\nThis may take a moment.")
        
        try:
            task_id = api_client.start_task(tool)
            if not task_id:
                bot.edit_message_text("❌ Failed to start task. Please check API credentials.", chat_id, status_msg.message_id)
                cleanup_files(files, chat_id, user_data)
                return

            bot.edit_message_text(f"⏳ Uploading {len(files)} file(s)...", chat_id, status_msg.message_id)
            uploaded_files = []
            for file_path in files:
                upload_result = api_client.upload_file(task_id, file_path)
                uploaded_files.append({'server_filename': upload_result.get('server_filename'), 'filename': os.path.basename(file_path)})

            bot.edit_message_text("⏳ Processing files...", chat_id, status_msg.message_id)
            params = {} # تنظیمات پارامترها دقیقاً مثل کد خودتان (compress, split, etc.)
            if tool == 'compress': params['compression_level'] = 'recommended'
            # ... بقیه شروط پارامترها ...

            process_result = api_client.process_task(task_id, tool, uploaded_files, params)
            
            bot.edit_message_text("⏳ Downloading result...", chat_id, status_msg.message_id)
            output_path = os.path.join(TEMP_DIR, f"{chat_id}_output_{tool}.pdf")
            
            if api_client.download_file(task_id, output_path):
                bot.edit_message_text("✅ Processing complete! Sending file...", chat_id, status_msg.message_id)
                with open(output_path, 'rb') as f:
                    bot.send_document(chat_id, f, caption=f"✨ Your {tool} result is ready!")
                if os.path.exists(output_path): os.remove(output_path)
            else:
                bot.edit_message_text("❌ Failed to download result.", chat_id, status_msg.message_id)
            
            cleanup_files(files, chat_id, user_data)
        except Exception as e:
            bot.edit_message_text(f"❌ Error: {str(e)}", chat_id, status_msg.message_id)
            cleanup_files(files, chat_id, user_data)