# -*- coding: utf-8 -*-

"""
将通过 TheSim:ZipAndEncodeString 压缩得到的字符串解码为 lua 代码字符串
通过 lupa.lua51 运行 lua 代码得到返回值
将返回值从 lua.table 格式转为 dict 并返回
"""

import lupa.lua51 as lupa

from utils.klei_zip import decode as _decode
from .table2dict import Converter


def decode(data: str):
    lua_script = _decode(data)

    lua = lupa.LuaRuntime()
    return Converter().table_dict(lua.execute(lua_script))
