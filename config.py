import os
from dotenv import load_dotenv

# Загрузка переменных из файла .env в окружение
load_dotenv()

# Переменные для WB
WB_API_TOKEN: str = os.getenv('WB_API_TOKEN')

# Переменные для Google Sheets
credentials_file: str = os.getenv('GOOGLE_CREDENTIALS_FILE')
spreadsheet_name: str = 'WB products'

