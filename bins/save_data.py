"""定时保存高频数据
"""
import time
import json
from wolfquant import config
from wolfquant.interface import MdGateway
user_info = config('../config.json')['user_info']


def save_future(symbol_list, data_path):
    """保存期货数据
    """
    new_getway = MdGateway()
    new_getway.connect(user_info['brokerID'],
                       user_info['userID'],
                       user_info['password'],
                       user_info['register_front'],
                       symbol_list)
    try:
        while 1:
            time.sleep(1)
            with open(data_path, 'a') as f:
                json.dumps(new_getway._snapshot_cache, f)
    except KeyboardInterrupt:
        pass


def main():
    save_future(['rb1801', 'i1801'], 'data.json')


if __name__ == '__main__':
    main()