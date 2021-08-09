# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'reduce test.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/5 16:01'
"""
from functools import reduce


class reducer:
    def __init__(self, count, total):
        self.count = count
        self.total = total

    def reduce_link(self, groupA, groupB):
        self.count += 1
        print(self.count)
        return groupB


if __name__ == "__main__":
    x = reducer(0, 100)
    reduce(x.reduce_link, [1, 2, 3, 4, 5, 6])
    print(x.count)
    pass
