from aqt import mw
from aqt.browser import Browser
from aqt.utils import showInfo

from .InputDialog import InputDialog


def func_config():
    """返回配置文件 """


def func_version():
    """返回版本号"""


def func_help():
    """返回帮助页面"""


def func_openInput():
    """打开input对话框"""
    try:
        mw.InputDialog.activateWindow()
    except:
        mw.InputDialog = InputDialog()
        mw.InputDialog.exec()
        mw.activateWindow()
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


def func_linkStarter(mode=999, need: tuple = ("none",)):
    """开始连接的入口,预处理,根据模式选择一种连接算法"""
    if "seleted" in need:
        """如果是选中模式,直接读取dict"""
        pass

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
