"""这个是用来放一些工具的
debug函数
一些常量
"""
import datetime

from aqt.utils import *

VERSION = "0.5"
helpSite = "https://gitee.com/huangjipan/hjp-bilink"
inputFileName = "input.json"
configFileName = "config.json"
helpFileName = "README.md"
relyLinkDir = "1423933177"
relyLinkConfigFileName = "config.json"
logFileName = "log.txt"
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
PREV_FOLDER = os.path.dirname(THIS_FOLDER)
RELY_FOLDER = os.path.join(PREV_FOLDER, relyLinkDir)
inputSchema = {"IdDescPairs": [], "addTag": ""}
consolerName = "hjp-bilink|"
algPathDict = {
    "desc": ["默认连接", "完全图连接", "组到组连接", "按结点取消连接", "按路径取消连接"],
    "mode": [999, 0, 1, 2, 3]
}


def console(text: str, func: callable = tooltip, need: tuple = ("console",)):
    prefix = ""
    if "time" in need:
        prefix += datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    if "console" in need:
        prefix += consolerName
    text = prefix + text
    func(text)
