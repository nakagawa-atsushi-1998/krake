import os
from dotenv import load_dotenv

load_dotenv()

class PATH:
    LOG = 'stream/.log'
    DB = 'external/.db'

class KEY:
    COINCHECK_API_ACCESS=os.getenv('COINCHECK_API_ACCESS')
    COINCHECK_API_SECRET=os.getenv('COINCHECK_API_SECRET')
    BYBIT_API_ACCESS=os.getenv('BYBIT_API_ACCESS')
    BYBIT_API_SECRET=os.getenv('BYBIT_API_SECRET')
    LINE_API_TOKEN=os.getenv('LINE_API_TOKEN')

class FORM:
    class COLOR:
        candle = ['#5F5', '#F55', '#55F', '#888']
        bb = ['#AAA', '#BBB', '#CCC', '#DDD']
        rsi = ['#22C', '#33D', '#44E', '#55F']
        macd = ['#738', '#849', '#95A', '#A6B']
    alpha = [7/10, 3/10, 2/10, 1/10]
    label = ['Open','Close','BB2σ','MACD','RSI','EW'],


