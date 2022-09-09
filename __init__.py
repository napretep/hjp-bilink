"""入口

"""
from .lib.common_tools import connectors
from .lib.common_tools import  compatible_import

connectors.funcs.G.src.ADDON_VERSION="2.4.7.l"
connectors.funcs.G.ISDEBUG=False

connectors.run()
