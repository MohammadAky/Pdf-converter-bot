import os
import shutil

def cleanup_files(files, chat_id, user_data):
    """Clean up temporary files and user data"""
    for file_path in files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
    
    if chat_id in user_data:
        del user_data[chat_id]

def ensure_temp_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)