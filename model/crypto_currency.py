#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

COLUMNS = {
    'candle': ['Date', 'Open', 'High', 'Low', 'Close', 'Volume'],
    'ew': ['Date', 'Direction', 'EW'],
    'bb': ['Date', 'SMA', 'Std', '+2σ', '-2σ'],
    'rsi': ['Date', 'Diff', '+Ave', '-Ave', 'RSI'],
    'macd': ['Date', 'ShortMA', 'LongMA', 'MACD', 'Signal', 'Hist'],
    'traded': ['Date', 'Side', 'Price', 'Amount']
}

class CryptoCurrency:
    def __init__(self):
        self.candle = pd.DataFrame(columns=COLUMNS['candle'])


