import pandas as pd

class Crypto:
    class Column:
        candle = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        bb = ['Date', 'SMA', 'Std', '+2σ', '-2σ']
        rsi = ['Date', 'Diff', '+Ave', '-Ave', 'RSI']
        macd = ['Date', 'ShortMA', 'LongMA', 'MACD', 'Signal', 'Hist', 'HistRSI']
        pal = ['Date', 'JPY', 'BTC', 'Total']

    def __init__(
        self,
        pair='BTCUSD',
        time_scale=1,
    ):
        self.pair = pair
        self.time_scale = time_scale
        self.candle = pd.DataFrame(columns=self.Column.candle)
        self.bb = pd.DataFrame(columns=self.Column.bb)
        self.rsi = pd.DataFrame(columns=self.Column.rsi)
        self.macd = pd.DataFrame(columns=self.Column.macd)
        self.pal = pd.DataFrame(columns=self.Column.pal)

    def add_pal(
        self,
        last_row
    ):  
        self.pal = self.pal.append(last_row, ignore_index=True)
        self.pal = self.pal.drop_duplicates()
        self.pal = self.pal[-179:]

    def add_candle(
        self,
        last_row,
    ):
        self.candle = self.candle.append(last_row, ignore_index=True)
        self.candle = self.candle.drop_duplicates()
        self.candle = self.candle[-179:]

    def calculate_bb(
        self,
        term=20,
        coefficient=2
    ):
        self.bb['Date'] = self.candle['Date']
        self.bb['SMA'] = self.candle['Close'].rolling(term).mean()
        self.bb['Std'] = self.candle['Close'].rolling(term).std()
        self.bb['+2σ'] = self.bb['SMA'] + coefficient*self.bb['Std']
        self.bb['-2σ'] = self.bb['SMA'] - coefficient*self.bb['Std']
        self.bb = self.bb[-179:]
        
    def calculate_rsi(
        self,
        term=14
    ):
        self.rsi['Date'] = self.candle['Date']
        self.rsi['Diff'] = self.candle['Close'].diff()
        up = self.rsi['Diff'].copy(); up[up < 0] = 0
        down = self.rsi['Diff'].copy(); down[down > 0] = 0
        self.rsi['+Ave'] = up.rolling(term).mean()
        self.rsi['-Ave'] = down.abs().rolling(term).mean()
        self.rsi['RSI'] = 100*self.rsi['+Ave']/(self.rsi['+Ave']+self.rsi['-Ave'])
        self.rsi = self.rsi[-179:]

    def calculate_macd(
        self,
        short_term=12, # 6,12,19
        long_term=26, # 19,26,39
        signal_term=9 # 4,9,12
    ):
        self.macd['Date'] = self.candle['Date']
        self.macd['ShortMA'] = self.candle['Close'].ewm(short_term).mean().round(3)
        self.macd['LongMA'] = self.candle['Close'].ewm(long_term).mean().round(3)
        self.macd['MACD'] = self.macd['ShortMA'] - self.macd['LongMA']
        self.macd['Signal'] = self.macd['MACD'].rolling(signal_term).mean().round(3)
        self.macd['Hist'] = self.macd['MACD'] - self.macd['Signal']
        diff = self.macd['Hist'].diff()
        up = diff.copy(); up[up < 0] = 0
        down = diff.copy(); down[down > 0] = 0
        self.pave = up.rolling(15).mean()
        self.mave = down.abs().rolling(15).mean()
        self.macd['HistRSI'] = 100*self.pave/(self.pave+self.mave)
        self.macd = self.macd[-179:]


