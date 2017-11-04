from wolfquant.backtest import Backtest
from wolfquant.data import TushareDataHandler
from wolfquant.event import SignalEvent, OrderEvent
from wolfquant.execution import SimulatedExecutionHandler
from wolfquant.portfolio import NaivePortfolio


def run_backtest(strategy, config):
    """进行回测
    """
    backtest = Backtest(config['symbol_list'],
                        config['init_cash'],
                        config['start'],
                        config['end'],
                        TushareDataHandler,
                        SimulatedExecutionHandler,
                        NaivePortfolio,
                        strategy)
    backtest.simulate_trading()
