import numpy as np
from abc import ABCMeta, abstractmethod
from event import SignalEvent


class Strategy(object):
    _metaclass_ = ABCMeta

    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError("Should implement calculate_signals()")


class BuyAndHoldStrategy(Strategy):
    def __init__(self, bars, events):
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.event = events
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        bought = {}
        for s in self.symbol_list:
            bought[s] = False
        return bought

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for s in self.symbol_list:
                bar = self.bars.get_latest_bars(s, N=1)
                if bar is not None and bar != []:
                    if self.bought[s] == False:
                        signal = SignalEvent(bar[0][0], bar[0][1], 'LONG')
                        self.event.put(signal)
                        self.bought[s] = True


class MovingAverageCrossStrategy(Strategy):
    def __init__(self, bars, events, short_window=100, long_window=400):
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.event = events
        self.short_window = short_window
        self.long_window = long_window
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        bought = {}
        for s in self.symbol_list:
            bought[s] = 0
        return bought

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for s in self.symbol_list:
                if self.bars.get_data_number(s) > self.long_window + 1:
                    bar = self.bars.get_latest_bars(s, N=self.long_window + 1)
                    adj_close = [bar[k][7] for k in range(len(bar))]
                    long_prev = np.mean(adj_close[:-1])
                    long_curr = np.mean(adj_close[1:])
                    short_prev = np.mean(
                        adj_close[-(self.short_window + 1):-1])
                    short_curr = np.mean(adj_close[-self.short_window:])
                    if(short_prev < long_prev and short_curr > long_curr):
                        if self.bought[s] == 0:
                            signal = SignalEvent(bar[0][0], bar[0][1], 'LONG')
                            self.event.put(signal)
                            self.bought[s] = 1
                        elif self.bought[s] == -1:
                            signal = SignalEvent(bar[0][0], bar[0][1], 'EXIT')
                            self.event.put(signal)
                            self.bought[s] = 0
                    elif(short_prev > long_prev and short_curr < long_curr):
                        if self.bought[s] == 0:
                            signal = SignalEvent(bar[0][0], bar[0][1], 'SHORT')
                            self.event.put(signal)
                            self.bought[s] = -1
                        elif self.bougth[s] == 1:
                            signal = SignalEvent(bar[0][0], bar[0][1], 'EXIT')
                            self.event.put(signal)
                            self.bought[s] = 0
