import os
import glob
from dotenv import load_dotenv

load_dotenv()

class PATH:
    LOG = 'interface/log'
    
class KEY:
    COINCHECK_API_ACCESS=os.getenv('COINCHECK_API_ACCESS')
    COINCHECK_API_SECRET=os.getenv('COINCHECK_API_SECRET')
    BYBIT_API_ACCESS=os.getenv('BYBIT_API_ACCESS')
    BYBIT_API_SECRET=os.getenv('BYBIT_API_SECRET')
    LINE_API_TOKEN=os.getenv('LINE_API_TOKEN')
