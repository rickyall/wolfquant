
class Factor_pipeline(object):
    def __init__(self, data):
        self.data = data

    def add(self, func, *args, **kwargs):
        """添加变量
        """
        self.data = func(self.data, *args, **kwargs)
        return self
