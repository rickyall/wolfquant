import queue
import pprint
import time


class Backtest(object):
    """进行Bactest的组件和配置
    """
    def __init__(
        self, csv_dir, symbol_list, initial_capital,
        heartbeat, start_date, data_handler,
        execution_handler, portfolio, strategy
    ):
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date

        self.data_handler_cls = data_handler
        self.execution_handler_cls = execution_handler
        self.portfolio_cls = portfolio
        self.strategy_cls = strategy

        self.events = queue.Queue()

        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1

        self.__generate_trading_instances()

    def __generate_trading_instances(self):
        """生成交易实例对象
        """
        print("Creating DataHandler, Strategy, Portfolio and ExecutionHandler")
        self.data_handler = self.data_handler_cls(self.events, self.csv_dir, self.symbol_list)
        self.strategy = self.strategy_cls(self.data_handler, self.events)
        self.portfolio = self.portfolio_cls(self.data_handler, self.events)
        self.execution_handler = self.execution_handler_cls(self.events)

    def __run_backtest(self):
        """执行回测
        """
        i = 0
        while True:
            i += 1
            print(i)
            # 更新市场Bar
            if self.data_handler.continue_backtest is True:
                self.data_handler.update_bars()
            else:
                break

            # 处理事件
            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'MARKET':
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_timeindex(event)
                        elif event.type == 'SIGNAL':
                            self.signals += 1
                            self.portfolio.update_signal(event)
                        elif event.type == 'ORDER':
                            self.orders += 1
                            self.execution_handler.execute_order(event)
                        elif event.type == 'FILL':
                            self.fills += 1
                            self.portfolio.update_fill(event)

            time.sleep(self.heartbeat)

    def __output_performance(self):
        """输出策略的表现
        """
        self.portfolio.create_equity_curve_dataframe()

        print("创建统计描述...")
        stats = self.portfolio.output_summary_stats()

        print('创建走势...')
        print(self.portfolio.equity_curve.tail(10))
        pprint.pprint(stats)

        print('交易：{}'.format(self.signals))
        print("下单：{}".format(self.orders))
        print('Fills: {}'.format(self.fills))

    def simulate_trading(self):
        """模拟回测并输出结果
        """
        self.__run_backtest()
        self.__output_performance()
