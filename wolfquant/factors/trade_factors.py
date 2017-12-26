import pandas as pd
import talib as ta


#################################################################
# 滞后类指标
#################################################################
def LAGRETURN(data, ndays):
    """滞后类收入指标
    args:
        - data: 标准的行情时间序列数据
        - ndays: 移动平均的天数
    return:
        - data: 加入滞后类指标的数据
    """
    name = 'LAGRETURN_{}'.format(ndays)
    LAGRETURN = pd.Series(data['close'].shift(ndays).pct_change() * 100.0, name=name)
    data = data.join(LAGRETURN)
    return data


#################################################################
# 移动平均线指标
#################################################################
def SMA(data, ndays):
    """SMA: 简单的移动平均线
    args:
        - data: 标准的行情时间序列数据
        - ndays: 移动平均的天数
    return:
        - data: 加入移动平均指标的数据
    """
    name = 'SMA_{}'.format(ndays)
    SMA = pd.Series(data['close'].rolling(ndays).mean(), name=name)
    data = data.join(SMA)
    return data


def EWMA(data, ndays):
    """EWMA: 指数加权移动平均线
    args:
        - data: 标准的行情时间序列数据
        - ndays: 移动平均的天数
    return:
        - data: 加入移动平均指标的数据
    """
    name = 'EWMA_{}'.format(ndays)
    EMA = pd.Series(data['close'].ewm(span=ndays, min_periods=ndays - 1).mean(), name=name)
    data = data.join(EMA)
    return data


def MACD(data, fastperiod=12, slowperiod=26, signalperiod=9):
    """MACD指标：指数平滑移动平均线
    """
    macd, macdsignal, macdhist = ta.MACD(data['close'].values, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
    data['macd'] = macd
    data['macdsignal'] = macdsignal
    data['macdhist'] = macdhist
    return data


#################################################################
# 布林线指标
#################################################################
def BBANDS(data, ndays):
    """BBANDS: 布林线指标
    args:
        - data: 标准的行情时间序列数据
        - ndays: 移动平均的天数
    return:
        - data: 加入BBANDS指标的数据
    """
    MA = pd.Series(data['close'].rolling(ndays).mean(), name='MA_{}'.format(ndays))
    SD = pd.Series(data['close'].rolling(ndays).std())
    b1 = pd.Series(MA + (2 * SD), name='Upper_BollingBond')
    b2 = pd.Series(MA - (2 * SD), name='Lower_BollingBond')
    data = data.join(MA).join(b1).join(b2)
    return data


#################################################################
# 趋势类指标
#################################################################
def CCI(data, ndays):
    """CCI: 属于超买和超卖的指标
    args:
        - data: 标准的行情时间序列数据
        - ndays: 移动平均的天数
    return:
        - data: 加入CCI指标的数据
    """
    TP = (data['high'] + data['low'] + data['close']) / 3
    CCI = pd.Series((TP - TP.rolling(ndays).mean()) / (0.015 * TP.rolling(ndays).std()), name='CCI')
    data = data.join(CCI)
    return data


def ForceIndex(data, ndays):
    """ForceIndex: 强力指标，该指标用来表示上升或下降趋势的力量大小，在零线上下移动来表示趋势的强弱。
    args:
        - data: 标准的行情时间序列数据
        - ndays: 移动平均的天数
    return:
        - data: 加入ForceIndex指标的数据
    """
    FI = pd.Series(data['close'].diff(ndays) * data['volume'], name='ForceIndex')
    data = data.join(FI)
    return data


#################################################################
# 波动类指标
#################################################################
def EVM(data, ndays):
    """EVM: 简易波动指标，将价格与成交量的变化结合成为一个波动指标来反映股价或指数的变动情况。
    args:
        - data: 标准的行情时间序列数据
        - ndays: 移动平均的天数
    return:
        - data: 加入EVM指标的数据
    """
    dm = (data['high'] + data['low']) / 2 - (data['high'].shift(1) + data['low'].shift(1)) / 2
    br = (data['volume'] / 100000000) / (data['high'] - data['low'])
    EVM = dm / br
    EVM_MA = pd.Series(EVM.rolling(ndays).mean(), name='EVM')
    data = data.join(EVM_MA)
    return data


def ROC(data, ndays):
    """ROC: 变动率指标，今天的收盘价比较其N天前的收盘价的差除以N天前的收盘，以比率表示之。
    args:
        - data: 标准的行情时间序列数据
        - ndays: 移动平均的天数
    return:
        - data: 加入ROC指标的数据
    """
    N = data['close'].diff(ndays)
    D = data['close'].shift(ndays)
    ROC = pd.Series(N / D, name='ROC')
    data = data.join(ROC)
    return data


#################################################################
# 相对强弱指标
#################################################################
def RSI(data, ndays):
    """RSI: 相对强弱指标，相对强弱指数RSI是根据一定时期内上涨点数和涨跌点数之和的比率制作出的一种技术曲线。
    args:
        - data: 标准的行情时间序列数据
        - ndays: 时间窗口
    return:
        - data: 加入RSI指标的数据
    """
    RSI = pd.Series(ta.RSI(data['close'].values, timeperiod=ndays), name='RSI')
    data = data.join(RSI)
    return data
