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
        post=[
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
        self.post = pd.DataFrame(columns=self.Column.post)
        self.cancel = pd.DataFrame(columns=self.Column.cancel)
        self.unsettled = pd.DataFrame(columns=self.Column.unsettled)


