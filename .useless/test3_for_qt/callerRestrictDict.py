import sys
from collections import OrderedDict


class CallerResitrictDict:
    def __init__(self, data, needCaller=None, needClass=None):
        self.__data: "OrderedDict" = OrderedDict(data)
        self.needCaller: "callable" = needCaller
        self.needClass: "type" = needClass

    def restrict_check(self):
        if self.needClass or self.needCaller:
            curr_caller_func_name = sys._getframe(3).f_code.co_name  # 0是restrict_check, 1是所在的调用环境, 2是这个环境的调用者
            need_class = self.needClass.__dict__
            if not (curr_caller_func_name == self.needCaller.__name__ and curr_caller_func_name in need_class):
                raise ValueError(f"请使用{self.needClass.__str__(self.needClass)} 的 {self.needCaller.__name__} 调用我!")

    def __contains__(self, item):
        return item in self.__data

    def __getitem__(self, item):
        return self.__data[item]

    def __delitem__(self, key):
        self.restrict_check()
        self.__data.__delitem__(key)

    def __setitem__(self, key, value):
        self.restrict_check()
        self.__data[key] = value


if __name__ == "__main__":
    a = CallerResitrictDict({}, )
