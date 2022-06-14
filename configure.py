import os
import dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(verbose=True)
dotenv.load_dotenv(dotenv_path)

BIBIT_API_ACCESS = os.environ.get("BIBIT_API_ACCESS")
BYBIT_API_SECRET = os.environ.get("BYBIT_API_SECRET")
COINCHECK_API_ACCESS = os.environ.get("COINCHECk_API_ACCESS")
COINCHECK_API_SECRET = os.environ.get("COINCHECK_API_SECRET")
LINE_API_TOKEN = os.environ.get("LINE_API_TOKEN")
