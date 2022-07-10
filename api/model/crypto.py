from xml.sax.handler import property_dom_node
from xmlrpc.client import _datetime_type
import numpy as np
import pandas as pd

class Crypto:
    class Column:
        trade = [
            'Datetime',
            'ID',
            'Rate',
            'Amount',
            'Type'
        ]
        ohlcv = [
            'Datetime', #日時
            'Open', #始値
            'High', #高音
            'Low',  #安値
            'Close',#終値
            'Volume'#出来高
        ] #OHLCV
        candle = [
            'Datetime', #日時
            'Direction',#方向性
            'Body',     #実体
            'pShadow',  #上ヒゲ
            'mShadow',  #下ヒゲ
        ] #ローソク足
        bb = [
            'Datetime', #日時
            'SMA',  #単純移動平均
            'Std',  #標準偏差
            'pBB',  #上部ボリンジャーバンド(+σ)
            'mBB'   #下部ボリンジャーバンド(-σ)
        ] #ボリンジャーバンド
        ps = [
            'Datetime', #日時
            'EP',       #極大値
            'AF',       #加速因数
            'SAR',      #トレンド転換点
        ] #パラボリックSAR
        dmi = [
            'Datetime', #日時
            'pDM',  #
            'mDM',  #
            'TR'    #変動幅
            'pDI',  #正の方向性指数
            'mDI',  #負の方向性指数
            'DX',   #方向性指数
            'ADX',  #平均方向性指数
        ] #方向性指数
        rsi = [
            'Datetime', #日時
            'Diff', #前日差分
            'pDiff',#正の前日差分
            'mDiff',#負の前日差分
            'pAve', #正の平均
            'mAve', #負の平均
            'RSI'   #相対力指数
        ] #相対力指数
        rci = [
            'Datetime', #日時
            'TimeRank', #日付順位
            'PriceRank',#価格順位
            'RankSquare',#順位差の2乗
            'd',        #
            'RCI',      #
        ]
        macd = [
            'Datetime', #日時
            'ShortEMA', #短期指数平滑移動平均
            'LongEMA',  #長期指数平滑移動平均
            'MACD',     #移動平均収束拡散
            'Signal',   #シグナル
            'Hist',     #ヒストグラム
            'Crossover' #交差
        ] #移動平均収束拡散

    def __init__(
        self,
        time_scale=1,
    ):
        self.time_scale = time_scale #時間足　
        self.ohlcv = pd.DataFrame(columns=self.Column.ohlcv)
        self.candle = pd.DataFrame(columns=self.Column.candle)
        self.bb = pd.DataFrame(columns=self.Column.bb)
        self.ps = pd.DataFrame(columns=self.Column.ps)
        self.dmi = pd.DataFrame(columns=self.Column.dmi)
        self.rsi = pd.DataFrame(columns=self.Column.rsi)
        self.rci = pd.DataFrame(columns=self.Column.rci)
        self.macd = pd.DataFrame(columns=self.Column.macd)

    def add_ohlcv(
        self,
        ohlcv_dict,
    ):
        self.ohlcv = self.ohlcv.append(ohlcv_dict, ignore_index=True)

    def initialize_bb(
        self,
        term=20,
        coefficient=2
    ):
        self.bb['Datetime'] = self.ohlcv['Datetime']
        self.bb['SMA'] = self.ohlcv['Close'].rolling(term).mean()
        self.bb['Std'] = self.ohlcv['Close'].rolling(term).std()
        self.bb['pBB'] = self.bb['SMA'] + coefficient*self.bb['Std']
        self.bb['mBB'] = self.bb['SMA'] - coefficient*self.bb['Std']

    def calculate_bb(
        self,
        term=20,
        coefficient=2
    ):
        datetime_ = self.ohlcv['Datetime'].iloc[-1]
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
        self.bb = self.ohlcv.append(bb_dict, ignore_index=True)

    def initialize_ps(
        self,
        max_af=0.2,
    ):
        self.bull = True
        high_ = self.ohlcv['High'].iloc[0]
        low_ = self.ohlcv['Low'].iloc[0]
        self.ep = high_
        self.af = self.initial_af = 0.02
        self.ep_list = [self.ep]
        self.af_list = [self.af]
        self.sar_list = [low_]
        for counter in range(len(self.ohlcv)):
            high_ = self.ohlcv['High'].iloc[counter]
            low_ = self.ohlcv['Low'].iloc[counter]
            parabolic_ = self.sar_list[-1]
            if ((self.bull == True) and (parabolic_ > low_)) or\
                ((self.bull != True) and (parabolic_ < high_)):
                self.ps_is_touched = True
            else:
                self.ps_is_touched = False
            
            if self.ps_is_touched == True:
                self.sar = self.ep
                self.af = self.initial_af
                if self.bull:
                    self.bull = False
                    self.ep = low_
                else:
                    self.bull = True
                    self.ep = high_
            else:
                if self.bull and self.ep < high_:
                    self.ep = high_
                    self.af = min(self.af + self.initial_af, max_af)
                elif not self.bull and self.ep > low_:
                    self.ep = low_
                    self.af = min(self.af + self.initial_af, max_af)
                self.sar = self.sar_list[-1] + self.af * (self.ep - self.sar_list[-1])      
            if counter == 0:
                self.ep_list[-1] = self.ep
                self.af_list[-1] = self.af
                self.sar_list[-1] = self.sar
            else:
                self.ep_list.append(self.ep)
                self.af_list.append(self.af)
                self.sar_list.append(self.sar)
        self.ps['Datetime'] = self.ohlcv['Datetime']
        self.ps['EP'] = self.ep_list
        self.ps['AF'] = self.af_list
        self.ps['SAR'] = self.sar_list

    def calculate_ps(
        self,
        max_af=0.2,
    ):
        datetime_ = self.ohlcv['Datetime'].iloc[-1]
        high_ = self.ohlcv['High'].iloc[-1]
        low_ = self.ohlcv['Low'].iloc[-1]
        parabolic_ = self.sar_list[-1]
        if (self.bull == True) and (parabolic_ > low_): #強気相場かつパラボリックが安値以上
            self.ps_is_touched=  True
        elif (self.bull != True) and (parabolic_ < high_): #弱気相場かつパラボリックが高値以下
            self.ps_is_touched = True
        else:
            self.ps_is_touched = False

        if self.ps_is_touched == True: #パラボリックが触れた場合
            self.sar_list = self.ep
            self.af = self.initial_af
            if self.bull: #強気相場の場合
                self.bull = False
                self.ep = low_
            else: #弱気相場の場合
                self.bull = True
                self.ep = high_
        else: #パラボリックが触れていない場合
            if self.bull and self.ep < high_: #強気相場かつ極大値が高値以下の場合
                self.ep = high_
                self.af = min(self.af + self.initial_af, max_af)
            elif not self.bull and self.ep > low_: #弱気相場かつ極大値以上の場合
                self.ep = low_
                self.af = min(self.af + self.initial_af, max_af)
            self.sar = self.sar + self.af * (self.ep - self.sar)        
        ps_dict = {
            'Datetime':datetime_,
            'EP':self.ep,
            'AF':self.af,
            'SAR':self.sar,
        }
        self.ps = self.ps.append(ps_dict, ignore_index=True)

    def initialize_rsi(
        self,
        term=14
    ):
        self.rsi['Datetime'] = self.ohlcv['Datetime']
        self.rsi['Diff'] = self.ohlcv['Close'].diff()
        up = self.rsi['Diff'].copy(); up[up < 0] = 0
        down = self.rsi['Diff'].copy(); down[down > 0] = 0
        self.rsi['pAve'] = up.rolling(term).mean()
        self.rsi['mAve'] = down.abs().rolling(term).mean()
        self.rsi['RSI'] = 100*self.rsi['pAve']/(self.rsi['pAve']+self.rsi['mAve'])

    def initialize_macd(
        self,
        short_term=12,
        long_term=26,
        signal_term=9
    ):
        self.macd['Datetime'] = self.ohlcv['Datetime']
        self.macd['ShortMA'] = self.ohlcv['Close'].ewm(short_term).mean()
        self.macd['LongMA'] = self.ohlcv['Close'].ewm(long_term).mean()
        self.macd['MACD'] = self.macd['ShortMA'] - self.macd['LongMA']
        self.macd['Signal'] = self.macd['MACD'].rolling(signal_term).mean()
        self.macd['Hist'] = self.macd['MACD'] - self.macd['Signal']
        diff = self.macd['Hist'].diff()
        up = diff.copy(); up[up < 0] = 0
        down = diff.copy(); down[down > 0] = 0
        self.pave = up.rolling(15).mean()
        self.mave = down.abs().rolling(15).mean()
        self.macd['HistRSI'] = 100*self.pave/(self.pave+self.mave)

    def calculate_candle(self):
        datetime_ = self.ohlcv['Datetime'].iloc[-1]
        open_ = self.ohlcv['Open'].iat[-1]
        high_ = self.ohlcv['High'].iat[-1]
        low_ = self.ohlcv['Low'].iat[-1]
        close_ = self.ohlcv['Close'].iat[-1]
        if open_ > close_:
            direction = -1
            body = open_ - close_
            p_shadow = high_ - open_
            m_shadow = close_ - low_
        elif open_ < close_:
            dirrection = 1
            body = close_ - open_
            p_shadow = high_ - close_
            m_shadow = open_ - low_
        else:
            dirrection = 0
            body = 0
            p_shadow = high_ - open_
            m_shadow = open_ - low_
        candle_dict = {
            'Datetime': datetime_,
            'Dirrection': direction,
            'Body': body,
            'uShadow': p_shadow,
            'mShadow': m_shadow,
        }
        self.candle = self.ohlcv.append(candle_dict, ignore_index=True)



    def calculate_dmi(
        self,
        term=14,
    ):
        datetime_ = self.ohlcv['Datetime'].iloc[-1]
        high_list = self.ohlcv['High'][-term:]
        low_list = self.ohlcv['Low'][-term:]
        #close_list = self.ohlcv['Close'][-term:]
        close_list_shifted = self.ohlcv['Close'][-(term+1):].shift(1)[-term:]
        p_dm = (high_list.iloc[-1] - high_list.iloc[-2])
        m_dm = (low_list.iloc[-2] - low_list.iloc[-1])
        if p_dm < 0:
            p_dm = 0
        elif (p_dm-m_dm) < 0:
            p_dm = 0
        if m_dm < 0:
            m_dm = 0
        elif (m_dm-p_dm) < 0:
            m_dm = 0
        a = (high_list - close_list_shifted).abs()
        b = (close_list_shifted - low_list).abs()
        c = (high_list - low_list).abs()
        tr = pd.concat([a, b, c], axis=1).max(axis=1)
        p_di = p_dm.sum()/100*tr.sum()
        m_di = m_dm.sum()/100*tr.sum()
        dx = (p_di-m_di).abs()/100*(p_di+m_di)
        dx = dx.fillna(0)
        adx = dx.ewm(span=term).mean()
        dmi_dict = {
            'Datetime':datetime_,
            'pDM':p_dm,
            'mDM':m_dm,
            'TR':tr,
            'pDI':p_di,
            'mDI':m_di,
            'DX':dx,
            'ADX':adx,
        }
        self.dmi = self.ohlcv.append(dmi_dict, ignore_index=True)

    def calculate_rsi(
        self,
        term=14,
    ):
        datetime_ = self.ohlcv['Datetime'].iloc[-1]
        diff_ = self.ohlcv['Close'].iloc[-2] - self.ohlcv['Close'].iloc[-1]
        if diff_ >= 0:
            p_diff = diff_
            m_diff = 0
        elif diff_ < 0:
            p_diff = 0
            m_diff = diff_
        p_diff_list = self.rsi['pDiff'][-(term-1):].to_list()
        m_diff_list = self.rsi['mDiff'][-(term-1):].to_list()
        p_diff_list = p_diff_list.append(
            p_diff,
            #index=['pDiff'],
            #ignore_index=True
        )
        m_diff_list = m_diff_list.append(
            m_diff,
            #index=['mDiff'],
            #ignore_index=True
        )
        p_ave = pd.DataFrame(p_diff_list).mean()
        m_ave = pd.DataFrame(m_diff_list).abs().mean()
        rsi = 100*p_ave/(p_ave+m_ave)
        rsi_dict = {
            'Datetime':datetime_,
            'Diff':diff_,
            'pDiff':p_diff,
            'mDiff':m_diff,
            'pAve':p_ave,
            'mAve':m_ave,
            'RSI':rsi,
        }
        self.rsi = self.rsi.append(rsi_dict, ignore_index=True)

    def calculate_rci(
        self,
        term=14,
    ):
        pass

    def calculate_macd(
        self,
        short_term=12, # 6,12,19
        long_term=26, # 19,26,39
        signal_term=9, # 4,9,12
    ):
        datetime_ = self.ohlcv['Datetime'].iloc[-1]
        close_list = self.ohlcv['Close']
        short_ema = close_list.ewm(short_term).mean().iloc[-1]
        long_ema = close_list.ewm(long_term).mean().iloc[-1]
        macd = short_ema - long_ema
        macd_list = self.macd['MACD'][-signal_term:].to_list()
        print(short_ema)
        print(long_ema)
        print(macd_list)
        macd_list = macd_list.append(macd)
        signal = pd.DataFrame(macd_list).mean()
        hist = macd - signal
        before_hist = self.macd['Hist'].iloc[-1]
        #if hist > before_hist:
        #    crossover = 1
        #elif hist < before_hist:
        #    crossover = -1
        #else:
        #    crossover = 0
        macd_dict = {
            'Datetime':datetime_,
            'ShortEMA':short_ema,
            'LongEMA':long_ema,
            'MACD':macd,
            'Signal':signal,
            'Hist':hist,
            #'Crossover':crossover,
        }
        self.macd = self.macd.append(macd_dict, ignore_index=True)

    def trim(
        self,
        df,
        term
    ):
        if term < len(df):
            df = df.drop_duplicates()
            df = df[-(term-1):]
        return df


