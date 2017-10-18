from wolfquant.utils.api_utils import make_order_book_id, bytes2str


class DataDict(dict):
    def __init__(self, d=None):
        if d:
            super(DataDict, self).__init__(d)
        else:
            super(DataDict, self).__init__()

    def copy(self):
        return DataDict(super(DataDict, self).copy())

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)


class TickDict(DataDict):
    def __init__(self, data=None):
        super(TickDict, self).__init__()
        self.order_book_id = None
        self.date = None
        self.time = None
        self.open = None
        self.last = None
        self.low = None
        self.high = None
        self.prev_close = None
        self.volume = None
        self.total_turnover = None
        self.open_interest = None
        self.prev_settlement = None

        self.b1 = None
        self.b2 = None
        self.b3 = None
        self.b4 = None
        self.b5 = None

        self.b1_v = None
        self.b2_v = None
        self.b3_v = None
        self.b4_v = None
        self.b5_v = None

        self.a1 = None
        self.a2 = None
        self.a3 = None
        self.a4 = None
        self.a5 = None

        self.a1_v = None
        self.a2_v = None
        self.a3_v = None
        self.a4_v = None
        self.a5_v = None

        self.limit_down = None
        self.limit_up = None

        self.is_valid = False

        if data:
            self.update_data(data)

    def update_data(self, data):
        self.order_book_id = make_order_book_id(data.InstrumentID)
        try:
            self.date = int(data.TradingDay)
            self.time = int((bytes2str(data.UpdateTime).replace(':', ''))) * 1000 + int(data.UpdateMillisec)
            self.open = data.OpenPrice
            self.last = data.LastPrice
            self.low = data.LowestPrice
            self.high = data.HighestPrice
            self.prev_close = data.PreClosePrice
            self.volume = data.Volume
            self.total_turnover = data.Turnover
            self.open_interest = data.OpenInterest
            self.prev_settlement = data.SettlementPrice

            self.b1 = data.BidPrice1
            self.b2 = data.BidPrice2
            self.b3 = data.BidPrice3
            self.b4 = data.BidPrice4
            self.b5 = data.BidPrice5
            self.b1_v = data.BidVolume1
            self.b2_v = data.BidVolume2
            self.b3_v = data.BidVolume3
            self.b4_v = data.BidVolume4
            self.b5_v = data.BidVolume5
            self.a1 = data.AskPrice1
            self.a2 = data.AskPrice2
            self.a3 = data.AskPrice3
            self.a4 = data.AskPrice4
            self.a5 = data.AskPrice5
            self.a1_v = data.AskVolume1
            self.a2_v = data.AskVolume2
            self.a3_v = data.AskVolume3
            self.a4_v = data.AskVolume4
            self.a5_v = data.AskVolume5

            self.limit_up = data.UpperLimitPrice
            self.limit_down = data.LowerLimitPrice
            self.is_valid = True
        except ValueError:
            self.is_valid = False
