"""这个是用来放一些工具的
debug函数
一些常量
"""
import datetime

from aqt.utils import *

consolerName = "hjp-bilink|"


def console(text: str, func: callable = tooltip, need: tuple = ("console",)):
    prefix = ""
    if "time" in need:
        prefix += datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    if "console" in need:
        prefix += consolerName
    text = prefix + text
    func(text)
