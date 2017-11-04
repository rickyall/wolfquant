import os
import tushare as ts
import pandas as pd
from abc import ABCMeta, abstractmethod
from wolfquant.event import MarketEvent
from wolfquant.utils.db_utils import get_daily_data_from_db_new


class DataHandler(object):
    __metaclass__ = ABCMeta

    def __init__(self, events, symbol_list, start_date, end_date, csv_dir=None):
        self.csv_dir = csv_dir
        self.events = events
        self.symbol_list = symbol_list
        self.start_date = start_date
        self.end_date = end_date
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self.init_data()

    @abstractmethod
    def init_data(self):
        raise NotImplementedError('Should implement init_data()')

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        raise NotImplementedError('Should implement get_latest_bars()')

    @abstractmethod
    def update_bars(self):
        raise NotImplementedError('Should implement update_bars()')

    def get_latest_bars_dict(self, symbol_list, N=1):
        """获取多个证券的bar
        """
        bar_dict = {}
        for symbol in symbol_list:
            bar_dict[symbol] = self.get_latest_bars(symbol, N=N)
        return bar_dict

    def get_latest_bars_values(self, symbol, column, N=1):
        bar_columns = ['symbol', 'datetime', 'open', 'close', 'high', 'low', 'volume']
        bar_list = self.get_latest_bars(symbol, N=N)
        return [bar[bar_columns.index(column)] for bar in bar_list]

    def get_latest_bar_datetime(self, symbol):
        """获取最新的bar的执行日期
        """
        bar_list = self.get_latest_bars(symbol)
        return bar_list[0][1]

    def get_data_number(self, symbol):
        return len(self.latest_symbol_data[symbol])


class HistoricDataHandler(DataHandler):
    def init_data(self):
        comb_index = None
        for s in self.symbol_list:
            self.symbol_data[s] = self.history(s)
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index = comb_index.union(self.symbol_data[s].index)
            self.latest_symbol_data[s] = []

        # 选取指定时间段的数据，并重置索引
        comb_index = comb_index[(comb_index >= self.start_date) * (comb_index <= self.end_date)]
        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index).fillna(0.0).iterrows()

    def history(self, symbol):
        """获取历史数据
        """
        pass

    def __get_new_bar(self, symbol):
        for b in self.symbol_data[symbol]:
            yield tuple([symbol, b[0], b[1][0], b[1][1], b[1][2], b[1][3], b[1][4]])

    def get_latest_bars(self, symbol, N=1):
        try:
            bar_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the historical data set.")
        else:
            return bar_list[-N:]

    def update_bars(self):
        for s in self.symbol_list:
            try:
                bar = self.__get_new_bar(s).__next__()
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())


class CsvDataHandler(HistoricDataHandler):
    def history(self, symbol):
        """获取历史数据
        """
        return pd.io.parsers.read_csv(os.path.join(self.csv_dir, '%s.csv' % symbol), header=0, index_col=0, names=['datetime', 'open', 'close', 'high', 'low', 'volume'], parse_dates=True)


class TushareDataHandler(HistoricDataHandler):
    def history(self, symbol):
        """获取历史数据
        """
        data = ts.get_k_data(symbol.split('.')[0], start=self.start_date, end=self.end_date).set_index('date')[[
            'open', 'close', 'high', 'low', 'volume'
        ]]
        data.index = pd.to_datetime(data.index, format='%Y-%m-%d')
        return data


class DataBaseDataHandler(HistoricDataHandler):
    def history(self, symbol):
        """获取历史护具
        """
        return get_daily_data_from_db_new(symbol, self.start_date, self.end_date)