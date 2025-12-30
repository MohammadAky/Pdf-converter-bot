import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ILOVE_PUBLIC_KEY = os.getenv('ILOVE_PUBLIC_KEY')
ILOVE_SECRET_KEY = os.getenv('ILOVE_SECRET_KEY')
TEMP_DIR = 'temp_files'