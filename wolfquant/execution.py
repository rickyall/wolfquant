import datetime.datetime as dt
from abc import ABCMeta, abstractmethod
from wolfquant.event import FillEvent


class ExecutionHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self, event):
        raise NotImplementedError('Should implement execute_order()')


class SimulatedExecutionHandler(ExecutionHandler):
    def __init__(self, events):
        self.events = events

    def execute_order(self, event):
        if event.type == 'ORDER':
            fill_event = FillEvent(dt.utcnow(), event.symbol, 'ARCA', event.quantity, event.direction, 1.3, None)
            self.events.put(fill_event)
