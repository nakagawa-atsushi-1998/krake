import datetime
import numpy as np
import pandas as pd

class Order:
    class Column:
        new=[
            'Datetime',
            'ID',
            'Type',
            'Rate',
            'Amount',
        ] #新規注文
        past=[
            'Datetime',
            'ID',
            'Type',
            'Rate',
            'Amount',
        ] #注文履歴
        cancel=[
            'Datetime',
            'ID',
        ] #キャンセル
        unsettled=[
            'Datetime',
            'ID',
            'Type',
            'Rate',
            'Amount',
        ] #未決済注文

    def __init__(
        self,
    ):
        self.new = pd.DataFrame(columns=self.Column.new)
        self.past = pd.DataFrame(columns=self.Column.past)
        self.cancel = pd.DataFrame(columns=self.Column.cancel)
        self.unsettled = pd.DataFrame(columns=self.Column.unsettled)


