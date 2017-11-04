import queue
import pprint
import time
import sys


class Backtest(object):
    """进行Bactest的组件和配置
    """
    def __init__(
        self,
        csv_dir,
        symbol_list,
        initial_capital,
        heartbeat,
        start_date,
        end_date,
        data_handler,
        execution_handler,
        portfolio,
        strategy
    ):
        self.csv_dir = csv_dir  # 读取的数据的路径
        self.symbol_list = symbol_list  # 交易列表
        self.initial_capital = initial_capital  # 初始本金
        self.heartbeat = heartbeat  # 心跳
        self.start_date = start_date  # 开始日期
        self.end_date = end_date  # 结束日期

        self.data_handler_cls = data_handler  # 行情数据
        self.execution_handler_cls = execution_handler  # 交易
        self.portfolio_cls = portfolio  # 组合
        self.strategy_cls = strategy  # 策略

        self.events = queue.Queue()

        self.signals = 0  # 信号数
        self.orders = 0  # 订单数
        self.fills = 0  # 成交数

        self.__generate_trading_instances()

    def __generate_trading_instances(self):
        """生成交易实例对象
        """
        print("=====================\n开始进行回测...\n=====================")
        self.data_handler = self.data_handler_cls(self.events, self.csv_dir, self.symbol_list, self.start_date, self.end_date)
        self.portfolio = self.portfolio_cls(self.data_handler, self.events, self.start_date, self.initial_capital)
        self.strategy = self.strategy_cls(self.data_handler, self.events, self.portfolio)
        self.execution_handler = self.execution_handler_cls(self.events)  # 生成交易实例

    def __run_backtest(self):
        """执行回测
        """
        i = 0
        while True:
            sys.stdout.write('\r运行第{}个交易日..'.format(i))
            i += 1
            # 更新市场Bar
            if self.data_handler.continue_backtest is True:  # 如果可以继续进行回测，就更细bar
                self.data_handler.update_bars()
            else:
                break

            # 处理事件
            while True:
                try:
                    event = self.events.get(False)  # 获取事件队列的第一个元素
                except queue.Empty:  # 如果事件队列空了，就进入下一个bar
                    break
                else:
                    if event is not None:
                        if event.type == 'MARKET':  # 如果事件类型是行情，就计算交易信号
                            bar_dict = self.data_handler.get_latest_bars_dict(self.symbol_list)
                            self.strategy.handle_bar(bar_dict)  # 运行策略
                            self.portfolio.update_timeindex(event)  # 更新时间戳
                        elif event.type == 'SIGNAL':  # 如果事件类型是交易信号，就根据交易信号生成订单
                            self.signals += 1
                            self.portfolio.update_signal(event)
                        elif event.type == 'ORDER':  # 如果事件类型是订单信号，就执行交易
                            self.orders += 1
                            self.execution_handler.execute_order(event)
                        elif event.type == 'FILL':  # 如果事件类型是成交，就更新portfolio
                            self.fills += 1
                            self.portfolio.update_fill(event)

            time.sleep(self.heartbeat)

    def __output_performance(self):
        """输出策略的表现
        """
        self.portfolio.create_equity_curve_dataframe()  # 交易结束后，创建portfolio的历史序列数据
        print("\n=====================\n创建统计描述...\n=====================")
        stats = self.portfolio.output_summary_stats()
        for name, value in stats:
            print('{}: {}'.format(name, value))

        print('交易信号数: {}'.format(self.signals))
        print("下单数: {}".format(self.orders))
        print('成交数: {}'.format(self.fills))

    def simulate_trading(self):
        """模拟回测并输出结果
        """
        self.__run_backtest()
        self.__output_performance()
