"""入口"""
# from .lib.common_tools import funcs
# 检查版本更新
# if funcs.config_check_update():
#     funcs.Dialogs.open_version()

# funcs.config_check_update()

from .lib.common_tools import connectors
connectors.run()
