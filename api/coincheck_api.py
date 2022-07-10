import datetime
import time
import json
import hmac
import hashlib
import requests
import websocket
import threading
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib; matplotlib.use('Agg') #matplotlib.use('tkagg')
import warnings; warnings.simplefilter('ignore')
import os; cd=os.path.dirname(__file__); os.chdir(cd)
from .model import (
    account,
    crypto,
    order
)

account=account.Account(); aCol=account.Column()
crypto=crypto.Crypto(); cCol=crypto.Column()
order=order.Order(); oCol=order.Column()

class Path:
    rate='/api/exchange/orders/rate'
    trades='/api/trades'
    order='/api/exchange/orders'
    balance='/api/accounts/balance'
    transaction='/api/exchange/orders/transactions'
    cancel_status='/api/exchange/orders/cancel_status'
    unsettled_order='/api/exchange/orders/opens'

'''
class Orderer:
    def __init__(self):
        self.basic_price:float #基準値
        self.tolerance_pct:float #許容誤差比率
        self.upper_tolerance:float #許容上限値
        self.lower_tolerance:float #許容下限値
    
    def mainloop(self):    #スレッド③
        buy_execute=sell_execute=False
        possition='none'
        while len(self.trade) >= 15:
            time.sleep(15)
        while True:
            #ポジション無しの場合
            if possition == 'none':
                #口座情報取得
                possition='buy&sell'
            #両ポジションの場合
            elif possition == 'buy&sell':
                #約定履歴取得
                #両注文が約定
                if (sell_execute == True) and (buy_execute == True):
                    possition='none'
                elif sell_execute == True:
                    pass
                elif buy_execute == True:
                    pass
                time.sleep(5)
            #買いポジションの場合
            elif possition == 'buy':
                #約定履歴取得
                if sell_execute == True:
                    possition='none'
            #売りポジションの場合
            elif possition == 'sell':
                #約定履歴取得
                if buy_execute == True:
                    possition='none'
            print(possition)
            time.sleep(5)
'''

class HttpClient:
    def __init__(
        self,
        pair='btc_jpy',
        price=0,
        amount=0
    ):
        self.URL='https://coincheck.com'
        self.pair:str=pair
        self.price:float=price
        self.amount:float=amount

    def authenticate(
        self,
        access_key,
        secret_key
    ):
        self.__access_key=access_key
        self.__secret_key=secret_key

    def gain_signature(
        self,
        message
    ):
        signature=hmac.new(
            bytes(self.__secret_key.encode('ascii')),
            bytes(message.encode('ascii')),
            hashlib.sha256
        ).hexdigest()
        return signature

    def gain_header(
        self,
        nonce,
        signature
    ):
        header = {
            'ACCESS-KEY':self.__access_key,
            'ACCESS-NONCE':nonce,
            'ACCESS-SIGNATURE':signature,
            'Content-Type':'application/json'
        }
        return header

    def get(self, path, params=None):
        if params != None:
            params=json.dumps(params)
        else:
            params=''
        nonce=str(int(time.time()))
        message=nonce+self.URL+path+params
        signature=self.gain_signature(message)
        headers=self.gain_header(nonce, signature)
        return requests.get(
            self.URL+path,
            headers=headers
        ).json()

    def post(self, path, params):
        params=json.dumps(params)
        nonce=str(int(time.time()))
        message=nonce+self.URL+path+params
        signature=self.gain_signature(message)
        headers=self.gain_header(nonce, signature)
        return requests.post(
            self.URL+path,
            data=params,
            headers=headers
        ).json()

    def delete(self, path):
        nonce=str(int(time.time()))
        message=nonce+self.URL+path
        signature=self.gain_signature(message)
        headers=self.gain_header(nonce, signature)
        return requests.delete(
            self.URL+path,
            headers=headers
        ).json()

    def get_unsettled_order(self):
        path=Path.unsettled_order
        return self.get(path)

    def get_cancel_status(self, _id=None):
        path=Path.cancel_status+'?id='+str(_id)
        return self.get(path)

    def get_transaction(self):
        path=Path.transaction
        return self.get(path)

    def get_balance(self):
        path=Path.balance
        return self.get(path)

    def get_rate(self):
        path='/api/rate/'+self.pair
        return requests.get(
            self.host+path
        ).json()

    def get_amount(
        self,
        order_type:str,
        price=None
    ):
        path=Path.rate
        params={
            'order_type':order_type,
            'pair':self.pair,
            'price':price
        }
        return requests.get(
            self.URL+path,
            params=params
        ).json()

    def get_price(
        self,
        order_type:str,
        amount=None,
    ):
        path=Path.rate
        params={
            'order_type':order_type,
            'pair':self.pair,
            'amount':amount
        }
        return requests.get(
            self.URL+path,
            params=params
        ).json()
    
    def get_trades(
        self,
        limit=None,
        order='desc',
        starting_after=None,
        ending_before=None
    ):
        path=Path.trades
        params={
            'limit':limit,
            'starting_before':starting_after,
            'ending_after':ending_before,
            'order':order,
            'pair':self.pair
        }
        return requests.get(
            self.URL+path,
            params=params
        ).json()['data']
    
    def form_trades(
        self,
        trades,
    ):
        trade_df=pd.DataFrame(columns=oCol.post)
        for trade in reversed(trades):
            trade_dict={
                'ID':int(trade['id']), #int
                'Datetime':datetime.datetime.strptime(trade['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')+datetime.timedelta(hours=9),
                'Rate':trade['rate'],
                'Amount':trade['amount'],
                'Type':trade['order_type']
            }
            trade_df=trade_df.append(
                trade_dict,
                ignore_index=True)
        start_id=trade_df['ID'].iloc[0]
        end_id=trade_df['ID'].iloc[-1]
        return trade_df, start_id, end_id

    def split_trades_into_ohlcv(
        self,
        trades
    ):
        while True:
            if len(trades) == 0:
                break
            dt=trades['Datetime'].iloc[0]
            start_time=datetime.datetime(
                year=dt.year, month=dt.month, day=dt.day,
                hour=dt.hour, minute=dt.minute, second=0)
            end_time=start_time+datetime.timedelta(minutes=1)
            today_trades=trades.query('@start_time <= Datetime < @end_time')
            trades=trades.query('@end_time <= Datetime')
            print(today_trades)
            trades.reset_index()

    def post_order_buy(
        self,
        rate,
        amount,
        order_type='buy',
        #stop_loss_rate=None,
    ):
        path=Path.order
        params={
            'pair':self.pair,
            'order_type':order_type,
            'rate':rate,
            'amount':amount
        }
        return self.post(
            path,
            params)

    def post_order_sell(
        self,
        rate,
        amount,
        order_type='sell',
        #stop_loss_rate=None
    ):
        path=Path.order
        params={
            'pair':self.pair,
            'order_type':order_type,
            'rate':rate,
            'amount':amount
        }
        return self.post(
            path,
            params)

    def post_market_buy(
        self,
        market_buy_amount, #金額
        order_type='market_buy'
    ):
        path=Path.order
        params = {
            'pair':self.pair,
            'order_type':order_type,
            'market_buy_amount':market_buy_amount,
        }
        return self.post(
            path,
            params)

    def post_market_sell(
        self,
        amount, #量
        order_type='sell',
        #stop_loss_rate=None
    ):
        path=Path.order
        params={
            'pair':self.pair,
            'order_type':order_type,
            'amount':amount
        }
        return self.post(
            path,
            params)

    def post_order(
        self,
        order_type=None,
        rate=None,
        amount=None,
        market_buy_amount=None,
        #stop_loss_rate=None
    ):
        path = Path.order
        if (rate != None) and (amount != None):
            params = {
                'pair':self.pair,
                'order_type':order_type,
                'rate':rate,
                'amount':amount,
            }
        elif market_buy_amount != None:
            params = {
                'pair':self.pair,
                'order_type':order_type,
                'market_buy_amount':market_buy_amount,
            }
        elif amount != None:
            params = {
                'pair':self.pair,
                'order_type':order_type,
                'amount':amount
            }
        return self.post(
            path,
            params
        )

    def delete_order(self, _id=None):
        path = Path.balancepath.order + str(_id)
        return self.delete(path)



class WebsocketClient:
    def __init__(
        self,
        pair='btc_jpy',
        time_scale_list=[1,5,15,30]
        
    ):
        self.URL='wss://ws-api.coincheck.com/'
        self.pair=pair
        self.storage_term=60 #保存期間

        self.request_json = json.dumps({
            'type':'subscribe', 
            'channel':pair+'-trades'
        })
        self.lock=threading.Lock()
        self.figure,self.axes=plt.subplots(
            3, 1, figsize=(7.0, 8.0))
        self.trade=pd.DataFrame(columns=oCol.post)
        self.ohlcv=pd.DataFrame(columns=cCol.ohlcv)
        self.bb=pd.DataFrame(columns=cCol.bb)
        self.rsi=pd.DataFrame(columns=cCol.rsi)

    def connect(self):  #スレッド①
        self.session=websocket.WebSocketApp(
            self.URL,
            on_open=self.__on_open,
            on_close=self.__on_close,
            on_error=self.__on_error,
            on_message=self.__on_message,
        )
        print('session connect.')
        self.session.run_forever()

    #接続
    def __on_open(self, ws):
        self.__opened=True
        self.session.send(
            self.request_json)
        print('opened.')

    #接続エラー
    def __on_error(self, ws, error):
        print('incorrect.')
        self.__reconnect()

    #再接続
    def __reconnect(self):
        self.__exit()
        time.sleep(1)
        self.connect()

    #離脱時
    def __exit(self):
        self.session.close()

    #切断時
    def __on_close(self, ws):
        print('session closed.')
    
    #メッセージ受信時
    def __on_message(self, ws, message):
        trade_dict=self.form_trade(message)
        self.trade=self.trade.append(
            trade_dict,
            ignore_index=True
        )
        print(self.trade.values[-1])
        
    def form_trade(
        self,
        message
    ):
        datetime_=datetime.datetime.now()
        element=message.strip('[ ]').replace('"', '').split(',')
        trade_dict={
            'Datetime':datetime_,
            'ID':int(element[0]),
            'Rate':float(element[2]),
            'Amount':float(element[3]),
            'Type':element[4],
        }
        time.sleep(1/5)
        return trade_dict

    def collect(self):  #スレッド②
        while True:
            now=datetime.datetime.now()
            self.start_time=datetime.datetime(
                now.year, now.month, now.day,
                now.hour, now.minute, 0
            )
            self.end_time=datetime.datetime(
                now.year, now.month, now.day,
                now.hour, now.minute, 0
            )+datetime.timedelta(minutes=1)
            print(self.start_time)
            while datetime.datetime.now() < self.end_time:
                time.sleep(1)
                print('.', end='')
            self.calculate_ohlcv()
            self.lock.acquire() #施錠
            self.plot_graph()
            self.lock.release() #解錠
            #if len(self.ohlcv) >= 15:
            #    self.calculate_bb()
            #    print(self.bb)

    def forget_trade(self):
        self.trade=pd.DataFrame(columns=COLUMN.trade)
        
    def calculate_ohlcv(self):
        datetime_=self.start_time
        if len(self.trade) == 0:
            print('incorrect at calculate_ohlcv')
            self.ohlcv_dict={
                'Datetime':datetime_,
                'Open':None,
                'High':None,
                'Low':None,
                'Close':None,
                'Volume':None,
                'Diff':None
            }
        else:
            open_=self.trade['Rate'].iloc[0]
            close_=self.trade['Rate'].iloc[-1]
            high_=self.trade['Rate'].max()
            low_=self.trade['Rate'].min()
            volume_=self.trade['Amount'].sum()
            diff_=close_-open_
            #if close_ >= open_:
                #direction_=1
            #else:
                #direction_=-1
            self.ohlcv_dict={
                'Datetime':datetime_,
                'Open':open_,
                'High':high_,
                'Low':low_,
                'Close':close_,
                'Volume':volume_,
                'Diff':diff_
            }
        self.lock.acquire() #施錠
        self.ohlcv=self.ohlcv.append(
            self.ohlcv_dict,
            ignore_index=True)
        self.forget_trade()
        self.lock.release() #解錠
        print(self.ohlcv)

    def calculate_bb(
        self,
        term=20,
        coefficient=2
    ):
        datetime_ = self.start_time
        close_list = self.ohlcv['Close'][-term:]
        sma = close_list.mean()
        std = close_list.std()
        p_bb = sma+coefficient*std
        m_bb = sma-coefficient*std
        bb_dict = {
            'Datetime':datetime_,
            'SMA':sma,
            'Std':std,
            'pBB':p_bb,
            'mBB':m_bb,
        }
        self.bb = self.bb.append(bb_dict, ignore_index=True)

    def plot_graph(self):
        print(1)
        self.fig=plt.figure()
        print(2)
        self.ax=self.fig.add_subplot(1,1,1)
        print(3)
        self.ax.plot(
            self.ohlcv['Datetime'],
            self.ohlcv['Close'],
            color="#808080")
        print(4)
        self.fig.canvas.draw()
        print(5)
        self.fig.savefig(str(cd)+'/figure/latest.png')
        print(6)


