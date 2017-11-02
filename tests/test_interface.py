from wolfquant.interface import MdGateway


def test_get_data():
    import time
    from wolfquant import config
    user_info = config('../config.json')['user_info']
    new_getway = MdGateway()
    new_getway.connect(user_info['brokerID'],
                       user_info['userID'],
                       user_info['password'],
                       user_info['register_front'],
                       ['rb1801'])
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    test_get_data()
