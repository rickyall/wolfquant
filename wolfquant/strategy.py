from abc import ABCMeta, abstractmethod
from wolfquant.event import SignalEvent, OrderEvent


class Strategy(object):
    _metaclass_ = ABCMeta

    def __init__(self, bars, events, portfolio):
        self.strategy_id = 1
        self.bars = bars
        self.event = events
        self.portfolio = portfolio
        self.symbol_list = self.bars.symbol_list
        self.init()

    @abstractmethod
    def init(self):
        raise NotImplementedError("Should implement init()")

    @abstractmethod
    def handle_bar(self):
        raise NotImplementedError("Should implement handle_bar()")

    ###################################################
    # 一些成交方法
    ###################################################
    def order_shares(self, symbol, amount, style='MKT'):
        """按照数量下单
        args:
            symbol: 股票代码
            amount: 下单数量
            style: 下单方式
        """
        direction = 'LONG' if amount > 0 else 'SHORT'
        if self.checkout_tradeable(symbol):
            dt = self.bars.get_latest_bar_datetime(symbol)
            signal = SignalEvent(self.strategy_id, symbol, dt, direction, amount, style)
            self.event.put(signal)
        else:
            print("{}-{}-{}未成交".format(direction, symbol, amount))

    def checkout_tradeable(self, symbol):
        """检查一下当前的股票是否可以成交
        """
        bar = self.bars.get_latest_bars(symbol)
        if bar is not None and bar != []:
            return True
        else:
            return False
