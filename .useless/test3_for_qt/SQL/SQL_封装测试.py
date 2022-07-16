# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'SQL_封装测试.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/7/31 14:21'
"""
import re


class DB:
    class BOX:
        """仅用作传输,不作别的处理"""

        def __init__(self, string, values):
            self.string: str = string
            self.values: list = values

        def __and__(self, other: "DB.BOX"):
            string = f""" ( {self.string} ) AND ({other.string}) """
            values = self.values + other.values
            return DB.BOX(string, values)

        def __or__(self, other: "DB.BOX"):
            string = f""" ( {self.string} ) OR ({other.string}) """
            values = self.values + other.values
            return DB.BOX(string, values)

        def __neg__(self):
            string = f""" NOT ({self.string})"""
            values = self.values
            return DB.BOX(string, values)

    @staticmethod
    def IN(colname, *value):
        Q = ("?," * len(value))[:-1]
        string = colname + f" IN ({Q}) "
        return DB.BOX(string, list(value))

    @staticmethod
    def LIKE(colname, value):
        return DB.BOX(colname + " LIKE (?) ", [value])

    @staticmethod
    def EQ(LOGIC="AND", **kwargs):
        string = ""
        values = []
        for k, v in kwargs.items():
            string += f" {k}=? {LOGIC} "
            values.append(v)
        string = re.sub(f"{LOGIC}\s+$", "", string)
        return DB.BOX(string, values)

    @staticmethod
    def where(format: "DB.BOX"):
        print(format.string + " " + format.values.__str__())


if __name__ == "__main__":
    DB.where(DB.EQ(A="B", C="D") and (DB.IN("U", "V", "W") or DB.LIKE("X", "%Y%")))

    pass
