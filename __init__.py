"""入口
警告:pyqt不支持中文信号名
"""

from .lib.common_tools import connectors
from .lib.common_tools import compatible_import

connectors.funcs.G.src.ADDON_VERSION="2.5.6.l"

connectors.run()
