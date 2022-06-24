import pandas as pd

class Crypto:
    class Column:
        candle = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        bb = ['SMA', 'Std', '+2σ', '-2σ']
        rsi = ['Diff', '+Ave', '-Ave', 'RSI']
        macd = ['ShortMA', 'LongMA', 'MACD', 'Signal', 'Hist']

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

    def add_candle(
        self,
        last_row,
    ):
        self.candle = self.candle.append(last_row, ignore_index=True)

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


