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

class console:
    """debug用的"""

    def __init__(self, text: str = "", func: callable = tooltip, terminal=consolerName, logSwitcher=True, **need):
        self.logSwitcher = logSwitcher
        self.text = text
        self.say = func
        self.prefix = terminal + " > "
        self.need = need
        self.timestamp = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " > "
        self.who = sys._getframe(1).f_code.co_name + " > "
        self.logfile = os.path.join(THIS_FOLDER, logFileName)

    def log(self, chain=True):
        """debug用"""
        obj = self.need["obj"].__class__.__name__ + "." if "obj" in self.need else ""
        text = self.timestamp + self.prefix + obj + self.who + "\n" + self.text + "\n"
        f = open(self.logfile, "a", encoding="utf-8")
        f.write(text)
        f.close()
        if chain:
            return self
        else:
            return

    def _(self, text):
        """当这个类是一个对象的属性时,我们可以通过这个方法来发起通信"""
        self.text = text
        return self

    def talk(self, chain=True):
        """talk 就是 说出来"""
        self.say(self.text)
        if chain:
            return self
        else:
            return

    def showInfo(self, chain=True):
        """和外来的名字一样就是为了链式访问简单一点"""
        self.say = showInfo
        if chain:
            return self
        else:
            return
