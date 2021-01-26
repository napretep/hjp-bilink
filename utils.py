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


def console(text: str, func: callable = tooltip, terminal=consolerName, **need):
    prefix = ""
    prefix += terminal
    text = prefix + text
    func(text)

    if "log" in need:
        text = sys._getframe(1).f_code.co_name + ">" + text
        if "self" in need:
            text = need["self"].__name__ + ">" + text
        text = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S>") + text + "\n"

        f = open(os.path.join(THIS_FOLDER, logFileName), "a", encoding="utf-8")
        f.write(text)
        f.close()
