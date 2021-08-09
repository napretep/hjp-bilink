"""入口"""
from .lib.common_tools import funcs, connectors
from .lib.bilink import dialogs, G

# 检查版本更新
if funcs.config_check_update():
    funcs.Dialogs.open_version()

connectors.run()
