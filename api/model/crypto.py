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
            'Volume',#出来高
            'Diff'
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


