# -*- coding: utf-8 -*-

"""
将 lua.table 格式简单的转换为 dict 格式
"""

import lupa.lua51 as lupa


class Converter:

    def __init__(self):
        self.lua = lupa.LuaRuntime()

    def table_dict(self, lua_table):

        match typel := lupa.lua_type(lua_table):

            case None:  # ['nil', 'boolean', 'number', 'string'] -> python type
                return lua_table

            case 'table':
                # 因为没法区分 空 table 应该是 dict 还是 list，所以都转为 dict
                # keys = list(lua_table)
                # # 假如lupa.table为空，或keys从数字 1 开始并以 1 为单位递增，则认为是列表，否则为字典。其他情况有点复杂，就这样吧
                # if not len(keys) or keys[0] == 1 and all(map(lambda x: keys[x] + 1 == keys[x + 1], range(len(keys) - 1))):
                #     return [self._table_dict(x) for x in lua_table.values()]
                return {x: self.table_dict(y) for x, y in lua_table.items()}

            case _:
                return f'this is a {typel}'
