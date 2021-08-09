"""
管理各个子模块的导入导出
"""

from . import common_tools


def import_clipper_tools():
    from .clipper2.lib import tools as clipper_tools
    return clipper_tools


def import_bilink_tools():
    from .bilink import tools as bilink_tools
    return bilink_tools
