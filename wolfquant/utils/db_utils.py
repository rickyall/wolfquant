import numpy as np
import pandas as pd
import pandas.io.sql as psql
import pymysql as mdb

db_host = 'localhost'
db_user = 'sec_user'
db_pass = 'Yutian630403'
db_name = 'securities_master'


def get_daily_data_from_db_new(ticker, start_date,  end_date):
    con = mdb.connect(db_host,  db_user,  db_pass,  db_name)
    sql = """SELECT dp.price_date, open_price, high_price, low_price, close_price, volume, adj_close_price
             FROM symbol AS sym
             INNER JOIN daily_price AS dp
             ON dp.symbol_id = sym.id
             WHERE sym.ticker = '%s'
             AND dp.price_date> = '%s'
             AND dp.price_date <= '%s'
             ORDER BY dp.price_date ASC;""" % (ticker, start_date, end_date)
    data = psql.read_sql(sql, con=con, index_col='price_date')
    return data


def get_daily_data_from_db(ticker, data_type, start_date, end_date):
    con = mdb.connect(db_host,  db_user,  db_pass,  db_name)
    data_type = 'dp.' + data_type
    sql = """SELECT dp.price_date, %s
             FROM symbol AS sym
             INNER JOIN daily_price AS dp
             ON dp.symbol_id = sym.id
             WHERE sym.ticker = '%s'
             AND dp.price_date> = '%s'
             AND dp.price_date< = '%s'
             ORDER BY dp.price_date ASC;""" % (data_type, ticker, start_date, end_date)
    data = psql.read_sql(sql, con=con, index_col='price_date')
    return data


def simulate(start_date, end_date, tickers, initial_allocation):
    adj_close_price = {ticker: get_daily_data_from_db(ticker, 'adj_close_price', start_date, end_date) for ticker in tickers}
    adj_close_price_comb = pd.concat(adj_close_price, axis=1)
    ret = adj_close_price_comb.pct_change()
    ret_port = (ret*initial_allocation).sum(axis=1)
    ret_avg_port = ret_port.mean()
    vol_port = ret_port.std()
    rf = 0
    sharp_ratio_port = np.sqrt(252)*(ret_avg_port-rf)/vol_port
    return(sharp_ratio_port)


def optimize(start_date, end_date, tickers):
    adj_close_price = {ticker: get_daily_data_from_db(ticker, 'adj_close_price', start_date, end_date) for ticker in tickers}
    adj_close_price_comb = pd.concat(adj_close_price, axis=1)
    ret = adj_close_price_comb.pct_change()
    ret_avg = np.mat(ret.mean().as_matrix()).T
    rf = 0
    cov = np.mat(ret.cov().as_matrix())
    cov_inv = np.linalg.inv(cov)
    A = (ret_avg-rf).T*cov_inv*(ret_avg-rf)
    lmd = -1/A.item(0)
    w = -lmd*cov_inv*(ret_avg-rf)
    x = w/w.sum()
    return x.flatten().tolist()[0]


def get_snp_500_tickers():
    con = mdb.connect(db_host,  db_user,  db_pass,  db_name)
    sql = """SELECT ticker FROM symbol;"""
    data = psql.read_sql(sql, con=con, columns='ticker')
    return data['ticker'].tolist()
