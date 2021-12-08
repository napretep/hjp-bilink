"""入口

"""
from .lib.common_tools import connectors
connectors.funcs.G.src.ADDON_VERSION="2.4.0beta2"
connectors.funcs.G.ISDEBUG=False

connectors.run()
