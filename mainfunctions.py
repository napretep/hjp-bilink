from aqt.browser import Browser
from aqt.utils import showInfo


def func_config():
    """返回配置文件 """


def func_version():
    """返回版本号"""


def func_help():
    """返回帮助页面"""


def func_openInput():
    """返回input窗口"""


def func_clearInput():
    """清空input文件"""


def func_completeMap():
    """完全图连接"""


def func_GroupByGroup():
    """组到组连接"""


def func_unlinkByNode():
    """按结点取消连接"""


def func_unlinkByPath():
    """按路径取消连接"""


def func_linkStarter(mode=999):
    """开始连接的入口,预处理,根据模式选择一种连接算法"""
    showInfo("hello")


def func_browserInsert(browser: Browser, need: tuple = None):
    """专门用于browser界面的id拷贝
    need: group , clear
    """


def func_singleInsert(card_id: int = 0, desc: str = "", need: tuple = None):
    """
    @param card_id:
    @param desc:
    @param need: clear , last,  tag
    """
