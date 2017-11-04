import datetime
import numpy as np

from wolfquant.backtest import Backtest
from wolfquant.data import HistoricCSVDataHandler
from wolfquant.event import SignalEvent, OrderEvent
from wolfquant.execution import SimulatedExecutionHandler
from wolfquant.portfolio import NaivePortfolio
from wolfquant.strategy import Strategy


class MovingAverageCrossStrategy(Strategy):
    """
    Carries out a basic Moving Average Crossover strategy with a
    short/long simple weighted moving average. Default short/long
    windows are 100/400 periods respectively.
    results:
        Total Return: 6.05%
        Sharpe Ratio: 1.22
        Max Drawdown: 1.80%
        Drawdown Duration: 353
        交易信号数: 3
        下单数: 3
        成交数: 3
    """
    def init(self):
        self.short_window = 100
        self.long_window = 400
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to 'OUT'.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = 'OUT'
        return bought

    def handle_bar(self, bar_dict):
        """
        Generates a new set of signals based on the MAC
        SMA with the short window crossing the long window
        meaning a long entry and vice versa for a short entry.

        Parameters:
            bar_dict: 不同symbol的行情信息
        """
        for symbol in self.symbol_list:
            bars = self.bars.get_latest_bars_values(
                symbol, "close", N=self.long_window)

            if bars is not None and bars != []:
                short_sma = np.mean(bars[-self.short_window:])
                long_sma = np.mean(bars[-self.long_window:])
                quantity = 10

                if short_sma > long_sma and self.bought[symbol] == "OUT":
                    self.order_percent(symbol, 0.5)
                    self.bought[symbol] = 'LONG'

                elif short_sma < long_sma and self.bought[symbol] == "LONG":
                    self.order_shares(symbol, -quantity)
                    self.bought[symbol] = 'OUT'


class BuyAndHoldStrategy(Strategy):
    """一直持有策略
    results:
    Total Return: -2.74%
    Sharpe Ratio: -0.05
    Max Drawdown: 25.00%
    Drawdown Duration: 584
    交易信号数: 1
    下单数: 1
    成交数: 1
    """
    def init(self):
        self.bought = dict([(symbol, False) for symbol in self.symbol_list])

    def handle_bar(self, bar_dict):
        for s in self.symbol_list:
            if self.bought[s] is False:
                self.order_percent(s, 1)
                self.bought[s] = True


if __name__ == "__main__":
    csv_dir = 'data/'
    symbol_list = ['hs300']
    initial_capital = 100000.0
    start_date = datetime.datetime(2015, 4, 8, 0, 0, 0)
    end_date = datetime.datetime(2017, 10, 27, 0, 0, 0)
    heartbeat = 0.0

    backtest = Backtest(csv_dir,
                        symbol_list,
                        initial_capital,
                        heartbeat,
                        start_date,
                        end_date,
                        HistoricCSVDataHandler,
                        SimulatedExecutionHandler,
                        NaivePortfolio,
                        MovingAverageCrossStrategy)

    backtest.simulate_trading()
