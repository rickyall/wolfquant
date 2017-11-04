import numpy as np
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
        if self.checkout_tradeable(symbol):
            direction = 'LONG' if amount > 0 else 'SHORT'
            cost = self.bars.get_latest_bars(symbol)[0][2]
            cash = self.portfolio.current_holdings['cash']
            current_holding = self.portfolio.current_holdings[symbol]
            dt = self.bars.get_latest_bar_datetime(symbol)
            target_value = cost * amount
            if target_value > cash:
                print("因资金不足未创建订单")
            elif target_value <= cash and target_value + current_holding > 0:
                signal = SignalEvent(self.strategy_id, symbol, dt, direction, amount, style)
                self.event.put(signal)
                print("创建订单{}-{}-{}-{}-{}".format(dt, direction, symbol, abs(amount), cost))
            elif target_value + current_holding < 0:
                self.clear_position(symbol, style=style)
                print("订单金额超过所持有股票市值，对该股票进行清仓")
        else:
            print("{}-{}-{}未成交".format(direction, symbol, amount))

    def clear_position(self, symbol, style='MKT'):
        """清空仓位
        """
        dt = self.bars.get_latest_bar_datetime(symbol)
        signal = SignalEvent(self.strategy_id, symbol, dt, 'EXIT', None, style)
        self.event.put(signal)

    def order_value(self, symbol, value, style='MKT'):
        """按照资金下单
        """
        if self.checkout_tradeable(symbol):
            cost = self.bars.get_latest_bars(symbol)[0][2]
            target_amount = np.int(value // cost)  # 获取目标数量
            self.order_shares(symbol, target_amount)  # 下订单

    def order_percent(self, symbol, percent, style='MKT'):
        """按照一定的百分比进行下单
        """
        if self.checkout_tradeable(symbol):
            # 判断仓位是否是小于1
            if percent < 0 or percent > 1:
                raise ValueError("percent should between 0 and 1")
            target_value = self.portfolio.current_holdings['total'] * percent
            self.order_value(symbol, target_value, style=style)

    def order_target_percent(self, symbol, percent, style='MKT'):
        """按照目标仓位下单
        """
        if self.checkout_tradeable(symbol):
            # 判断仓位是否是小于1
            if percent < 0 or percent > 1:
                raise ValueError("percent should between 0 and 1")

            current_percent = self.portfolio.current_holdings[symbol] / self.portfolio.current_holdings['total']
            target_percent = percent - current_percent
            self.order_percent(symbol, target_percent, style=style)

    def checkout_tradeable(self, symbol):
        """检查一下当前的股票是否可以成交
        """
        bar = self.bars.get_latest_bars(symbol)
        if bar is not None and bar != []:
            return True
        else:
            return False
