import tushare as ts
from wolfquant.factors import trade_factors
import matplotlib.pyplot as plt


def test_trade_factors(factors):
    data = ts.get_k_data('000300', index=True)
    data = factors(data, 5).dropna().set_index('date')
    # 画图
    fig = plt.figure(figsize=(7, 5))
    ax = fig.add_subplot(2, 1, 1)
    ax.set_xticklabels([])
    data['close'].plot(lw=1)
    plt.title('hs300')
    plt.ylabel('close_price')
    plt.grid(True)
    fig.add_subplot(2, 1, 2)
    data[data.columns[-1]].plot(color='k', lw=0.75, linestyle='-', label='factor')
    plt.legend(loc=2, prop={'size': 9})
    plt.ylabel('factor values')
    plt.grid(True)
    plt.setp(plt.gca().get_xticklabels(), rotation=30)
    plt.show()


if __name__ == '__main__':
    test_trade_factors(trade_factors.ROC)
