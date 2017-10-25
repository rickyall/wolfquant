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
