# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'date测试.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/10 15:51'
"""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Date:
    year:"int"
    month:"int"
    day:"int"
    hour:"int"
    minute:"int"
    second:"int"
    millisecond:"int"

    def __eq__(self, other:"Date"):
        return other.year==self.year and other.month==self.month and other.day==self.day\
            and other.hour == self.hour and other.minute == self.minute and other.second == self.second \
            and other.millisecond == self.millisecond

    def __le__(self, other:"Date"):
        if other.year>self.year:
            return True
        elif other.year==self.year and other.month>self.month:
            return True
        elif other.year==self.year and other.month==self.month and other.day>self.day:
            return True
        elif other.year==self.year and other.month==self.month and other.day==self.day \
            and other.hour>self.hour :
            return True
        elif other.year==self.year and other.month==self.month and other.day==self.day \
            and other.hour==self.hour and other.minute>self.minute :
            return True
        elif other.year==self.year and other.month==self.month and other.day==self.day \
            and other.hour==self.hour and other.minute==self.minute and other.second>self.second :
            return True
        elif other.year==self.year and other.month==self.month and other.day==self.day \
            and other.hour==self.hour and other.minute==self.minute and other.second==self.second\
            and other.millisecond>self.millisecond:
            return True
        else:
            return False

if __name__ == "__main__":

    pass
    a = datetime.fromtimestamp(1628572786985/1000)
    b = datetime.fromtimestamp(datetime.today().timestamp())
    print(a<b)