def str2bytes(obj, encoding='utf8'):
    if isinstance(obj, str):
        return obj.encode(encoding)
    else:
        return obj


def bytes2str(obj, encoding='utf8'):
    if isinstance(obj, bytes):
        return obj.decode(encoding)
    else:
        return obj


def make_order_book_id(symbol):
    symbol = bytes2str(symbol)
    if len(symbol) < 4:
        return None
    if symbol[-4] not in '0123456789':
        order_book_id = symbol[:2] + '1' + symbol[-3:]
    else:
        order_book_id = symbol
    return order_book_id.upper()
