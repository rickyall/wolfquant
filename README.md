# wolfquant
重新构建集成交易、回测、建模的AI投资框架。
期货接口基于pyctp，使用语言python3.6，环境linux64/ubuntu

# 使用
## 交易接口调用
1.安装包
```shell
$ python setup.py
```
2.复制配置文件，更新配置信息
```shell
$ cp etc/config-default.json config.json
```
3.使用案例
```python
# 通过以下方式使用期货版API
>>>from wolfquant.api.future import ApiStruct, MdApi, TraderApi
```
4.运行测试案例
```shell
$ cd tests
$ python test_api.py
```
## 因子构建并采用机器学习模型训练
```python
import pandas as pd
import numpy as np
import tushare as ts
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.svm import LinearSVC, SVC
from sklearn.metrics import confusion_matrix
from wolfquant.utils.factor_utils import Factor_pipeline
from wolfquant.factors import trade_factors as tf

# 获取数据
datasets = ts.get_k_data('000300', start='2005-01-01', index=True).set_index('date')
datasets.index = pd.to_datetime(datasets.index, format='%Y-%m-%d')

# 构建特征
datasets = Factor_pipeline(datasets).add(tf.SMA, 50)\
                                    .add(tf.EWMA, 200)\
                                    .add(tf.BBANDS, 50)\
                                    .add(tf.CCI, 20)\
                                    .add(tf.ForceIndex, 1)\
                                    .add(tf.EVM, 14)\
                                    .add(tf.ROC, 5)\
                                    .add(tf.LAGRETURN, 0)\
                                    .data.dropna()

# 构建标签
datasets['direction'] = np.sign(datasets['LAGRETURN_0']).shift(-1)
datasets = datasets.dropna()

# 构建训练集和测试集
X = datasets[datasets.columns[6:-2]]
y = datasets['direction']
start_test = '2012-01-01'
X_train = X.loc[:start_test]
X_test = X.loc[start_test:]
y_train = y.loc[:start_test]
y_test = y.loc[start_test:]

# 构建模型
print('Hit rates/Confusion Matrices:\n')
models = [('LR', LogisticRegression()),
          ('LDA', LinearDiscriminantAnalysis()),
          ('QDA', QuadraticDiscriminantAnalysis()),
          ('LSVC', LinearSVC()),
          ('RSVM', SVC()),
          ('RF', RandomForestClassifier(n_estimators=1000))]

# 遍历模型
for m in models:
    # 训练模型
    m[1].fit(X_train, y_train)
    # 预测模型
    pred = m[1].predict(X_test)
    # 输出hit-rate和交叉验证结果
    print("%s:\n%0.3f" % (m[0], m[1].score(X_test, y_test)))
    print("%s\n" % confusion_matrix(pred, y_test))
```

## 运行策略回测
```python
import datetime
import numpy as np

from wolfquant.backtest import Backtest
from wolfquant.data import HistoricCSVDataHandler
from wolfquant.event import SignalEvent, OrderEvent
from wolfquant.execution import SimulatedExecutionHandler
from wolfquant.portfolio import NaivePortfolio
from wolfquant.strategy import Strategy

# 创建策略
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
                bar = self.bars.get_latest_bars(s)
                if bar is not None and bar != []:
                    if self.bought[s] is False:
                        signal = OrderEvent(s, 'MKT', 10, 'BUY')
                        self.event.put(signal)
                        self.bought[s] = True

# 运行策略
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
```


# 路线图
### 0.0.0
* 实现了期货python版的交易接接口
* 整理交易接口的使用文档
### 0.0.1
* 添加交易接口的测试案例
### 0.0.2
* 期货交易接口二次开发。
* 添加feature处理模块。
### 0.0.3
* 添加回测模块。
* 更新策略测试案例。
###
* 调整回测功能函数。
* 接受并保存期货高频行情数据。

# 附言
该项目会长期做，有志同道合的小伙伴，欢迎一起入坑，我的微信号wolfquant。
