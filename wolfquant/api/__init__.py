import sys
import logging
from time import sleep
from queue import Queue, Empty
from wolfquant.utils.api_utils import str2bytes
from wolfquant.api.future import ApiStruct, MdApi
from wolfquant.utils.data_utils import TickDict


class CtpMdApi(MdApi):
    def __init__(self, gateway, brokerID, userID, password, register_front):
        super(CtpMdApi, self).__init__()
        self.gateway = gateway
        self.requestID = 0
        self.brokerID = str2bytes(brokerID)
        self.userID = str2bytes(userID)
        self.password = str2bytes(password)
        self.register_front = str2bytes(register_front)
        self._req_id = 0
        self.logged_in = False
        self.connected = False

    def connect(self):
        """连接接口
        """
        if not self.connected:
            self.Create()
            self.RegisterFront(self.register_front)
            self.Init()
        else:
            self.login()

    def login(self):
        """登录
        """
        if not self.logged_in:
            req = ApiStruct.ReqUserLogin(BrokerID=self.brokerID,
                                         UserID=self.userID,
                                         Password=self.register_front)
            req_id = self.req_id
            self.ReqUserLogin(req, req_id)
            return req_id

    def subscribe(self, ins_id_list):
        """订阅合约"""
        if len(ins_id_list) > 0:
            ins_id_list = [str2bytes(i) for i in ins_id_list]
            self.SubscribeMarketData(ins_id_list)

    @property
    def req_id(self):
        self._req_id += 1
        return self._req_id

    def RegisterFront(self, front):
        front = str2bytes(front)
        if isinstance(front, bytes):
            return MdApi.RegisterFront(self, front)
        for front in front:
            MdApi.RegisterFront(self, front)

    def OnFrontConnected(self):
        """服务器连接
        """
        self.connected = True
        self.login()

    def OnFrontDisconnected(self, nReason):
        """服务器失去连接
        """
        self.connected = False
        self.logged_in = False
        self.gateway.on_debug('服务器断开，将自动重连。')

    def OnHeartBeatWarning(self, nTimeLapse):
        self.gateway.on_debug('OnHeartBeatWarning:', nTimeLapse)

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        """登录反馈
        """
        print('用户登录:{}'.format(pRspInfo))
        if pRspInfo.ErrorID == 0:
            self.logged_in = True
            print('交易日期:', self.GetTradingDay())
        else:
            self.gateway.on_err(pRspInfo, sys._getframe().f_code.co_name)

    def OnRspSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        print('连接市场数据:', pRspInfo)

    def OnRspUnSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        print('OnRspUnSubMarketData:', pRspInfo)

    def OnRspError(self, pRspInfo, nRequestID, bIsLast):
        print('OnRspError:', pRspInfo)

    def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
        """登出反馈
        """
        if pRspInfo.ErrorID == 0:
            self.logged_in = False
        else:
            self.gateway.on_err(pRspInfo, sys._getframe().f_code.co_name)

    def OnRtnDepthMarketData(self, pDepthMarketData):
        """行情推送
        """
        tick_dict = TickDict(pDepthMarketData)
        if tick_dict.is_valid:
            self.gateway.on_tick(tick_dict)


class MdGateway(object):
    def __init__(self, retry_times=5, retry_interval=1):
        self._md_api = None
        self._retry_times = retry_times
        self._retry_interval = retry_interval
        self._snapshot_cache = {}
        self._tick_que = Queue()
        self.subscribed = []

    def connect(self, user_id, password, broker_id, md_address, instrument_ids):
        self._md_api = CtpMdApi(self, user_id, password, broker_id, md_address)
        for i in range(self._retry_times):
            self._md_api.connect()
            sleep(self._retry_interval * (i+1))
            if self._md_api.logged_in:
                self.on_log('CTP 行情服务器登录成功')
                break
        else:
            raise RuntimeError('CTP 行情服务器连接或登录超时')
        self._md_api.subscribe(instrument_ids)
        self.on_log('数据同步完成。')

    def get_tick(self):
        while True:
            try:
                return self._tick_que.get(block=True, timeout=1)
            except Empty:
                self.on_debug('Get tick timeout.')

    def exit(self):
        """退出
        """
        self._md_api.close()

    @property
    def snapshot(self):
        return self._snapshot_cache

    def on_tick(self, tick_dict):
        if tick_dict.order_book_id in self.subscribed:
            self._tick_que.put(tick_dict)
        self._snapshot_cache[tick_dict.order_book_id] = tick_dict

    def on_universe_changed(self, event):
        self.subscribed = event.universe

    @staticmethod
    def on_debug(debug):
        logging.debug(debug)

    @staticmethod
    def on_log(log):
        logging.info(log)

    @staticmethod
    def on_err(error, func_name):
        logging.error('CTP 错误，错误代码：%s，错误信息：%s' % (str(error.ErrorID), error.ErrorMsg.decode('utf8')))


if __name__ == '__main__':
    import time
    from wolfquant import config
    user_info = config('../../config.json')['user_info']
    new_getway = MdGateway()
    new_getway.connect(user_info['brokerID'],
                       user_info['userID'],
                       user_info['password'],
                       user_info['register_front'],
                       ['RB1801'])
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
