#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 共通
from pybit.inverse_perpetual import HTTP
import sys, enum
import csv, json
import time, datetime
# HttpClientのみ利用
import hmac
import hashlib
import requests
# WebsockClientのみ利用
import websocket
import concurrent.futures
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class HttpClient():
    def __init__(self):
        #self.url = 'https://api.bybit.com'
        self.url = 'https://api-testnet.bybit.com'
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.symbol = 'BTCUSD'
        self.session = None
        self.candle = pd.DataFrame(columns=columns['candle'])
        self.ew = pd.DataFrame(columns=columns['ew'])
        self.bb = pd.DataFrame(columns=columns['bb'])
        self.rsi = pd.DataFrame(columns=columns['rsi'])
        self.macd = pd.DataFrame(columns=columns['macd'])
        self.traded = pd.DataFrame(columns=columns['traded'])
        
    def auth(self, api_key, api_secret):
        self.session = HTTP(
            self.url,
            api_key=api_key,
            api_secret=api_secret
        )
    
    def request_order(self, side, qty, order_type='Market', time_in_force='GoodTillCancel'):
        result = self.session.place_active_order(
            symbol=self.symbol,
            side=side,
            order_type=order_type,
            qty=qty,
            time_in_force=time_in_force
        )
        result = {
            'Date': result['time_now'],
            'ID': result['result']['order_id'],
            'Side': result['result']['side'],
            'Price': result['result']['price'],
            'Amount': result['result']['qty']
        }
        return result

    def cancel_order(
        self,
        order_id
    ):
        self.session.cancel_active_order(
            symbol=self.symbol,
            #order_id="3bd1844f-f3c0-4e10-8c25-10fea03763f6"
        )
    
    def gain_candle(
        self,
        interval,
        from_time
    ):
        response = self.session.query_kline(
            symbol=self.symbol,
            interval=interval,
            from_time=from_time
        )
        results = list(response['result'])
        for counter in range(len(results)):
            result = results[counter]
            dt = datetime.datetime.fromtimestamp(result['open_time'])
            request = {
                'Date':dt,
                'Open':float(result['open']),
                'High':float(result['high']),
                'Low':float(result['low']),
                'Close':float(result['close']),
                'Volume':int(result['volume'])
            }
            self.candle = self.candle.append(request, ignore_index=True)
        #print(self.candle)

    def calc_bb(
        self,
        term=20
    ):
        self.bb['Date'] = self.candle['Date']
        self.bb['SMA'] = self.candle['Close'].rolling(term).mean()
        self.bb['Std'] = self.candle['Close'].rolling(term).std()
        self.bb['+2σ'] = self.bb['SMA'] + 2*self.bb['Std']
        self.bb['-2σ'] = self.bb['SMA'] - 2*self.bb['Std']
        
    def calc_rsi(
        self,
        term=14
    ):
        self.rsi['Date'] = self.candle['Date']
        self.rsi['Diff'] = self.candle['Close'].diff()
        #self.rsi['Diff'][0] = 0
        up = self.rsi['Diff'].copy(); up[up < 0] = 0
        down = self.rsi['Diff'].copy(); down[down > 0] = 0
        self.rsi['+Ave'] = up.rolling(term).mean()
        self.rsi['-Ave'] = down.abs().rolling(term).mean()
        self.rsi['RSI'] = (100*self.rsi['+Ave']+0.5)/(self.rsi['+Ave']+self.rsi['-Ave']+1)

    def calc_macd(
        self,
        short_term=12,#6,12,19
        long_term=26,#19,26,39
        signal_term=9#4,9,12
    ):
        self.macd['Date'] = self.candle['Date']
        self.macd['ShortMA'] = self.candle['Close'].ewm(short_term).mean().round(3)
        self.macd['LongMA'] = self.candle['Close'].ewm(long_term).mean().round(3)
        self.macd['MACD'] = self.macd['ShortMA'] - self.macd['LongMA']
        self.macd['Signal'] = self.macd['MACD'].rolling(signal_term).mean().round(3)
        self.macd['Hist'] = self.macd['MACD'] - self.macd['Signal']
        #print(self.macd)



class WebsocketConnector():
    def __init__(self):
        #self.url = 'wss://stream.bybit.com/realtime'
        self.url = 'wss://stream-testnet.bybit.com/realtime'
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.session = HTTP()
        self.candle = pd.DataFrame(columns=columns['candle'])
    
    def connect(self):
        self.status = 'connect'; print(self.status)
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open = self.__on_open,
            on_close = self.__on_close,
            on_error = self.__on_error,
            on_message = self.__on_message,
        )
        self.executor.submit(self.ws.run_forever)

    def __reconnect(self):
        self.status = 'reconnect'; print(self.status)
        self.__exit()
        time.sleep(3)
        self.connect()
    
    def __exit(self):
        self.status = 'exit'; print(self.status)
        self.ws.close()

    def __on_open(self, ws):
        self.status = 'open'; print(self.status)
        self.__request = {
            "op":"subscribe",
            "args":["klineV2.5.BTCUSD"]
        }
        self.ws.send(json.dumps(self.__request))
        self.__opened = True
    
    def __on_error(self, ws, error):
        self.status = 'error'; print(self.status)
        self.__reconnect()
    
    def __on_close(self):
        self.status = 'close'; print(self.status)
    
    def __on_message(self, ws, message):
        message = self.__form_message(message)
    
    def __form_message(self, message):
        message = json.loads(message)
        try:
            elements = list(message['data'])
            length = len(elements)
            for counter in range(length):
                rec = elements[counter - 1]
                cc = columns['candle']
                dt = datetime.datetime.fromtimestamp(rec['start'])
                record = {
                    cc[0]:dt,
                    cc[1]:rec['open'],
                    cc[2]:rec['close'],
                    cc[3]:rec['high'],
                    cc[4]:rec['low'],
                    cc[5]:rec['volume']
                }
                self.candle = self.candle.append(record, ignore_index=True)
                #print(self.candle.values[-1:][0])
                #dt = datetime.datetime.fromtimestamp(record['trade_time_ms'])
                #print(dt)
        except:
            print(message)
            print('incorrect')
        time.sleep(0.05)
        return message

