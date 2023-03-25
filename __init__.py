"""入口
警告:pyqt不支持中文信号名

兼容性:
    3.8不支持一些类型标注,需要尽可能注意, 比如 tuple[str], 以后要改成Tuple


"""

# 如果判断本插件 l 结尾,并且判断网络版已经开启, 则不加载本地版内容

from .lib.common_tools import connectors
from .lib.common_tools import compatible_import

#


connectors.funcs.G.src.ADDON_VERSION="dev"

connectors.funcs.Utils.版本.检查()

if not connectors.funcs.Utils.版本.版本冲突():
    connectors.run()
