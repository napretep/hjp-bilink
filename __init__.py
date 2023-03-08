"""入口
警告:pyqt不支持中文信号名
"""

# 如果判断本插件 l 结尾,并且判断网络版已经开启, 则不加载本地版内容

from .lib.common_tools import connectors
from .lib.common_tools import compatible_import

#


connectors.funcs.G.src.ADDON_VERSION="2.5.11.2.l"

connectors.funcs.Utils.版本.检查()

if not connectors.funcs.Utils.版本.版本冲突():
    connectors.run()
