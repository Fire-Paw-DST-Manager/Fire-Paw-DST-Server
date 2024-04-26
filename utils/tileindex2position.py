# -*- coding: utf-8 -*-
"""
将地皮索引转为地皮的坐标值
"""


class PointPos:
    map_width: int = None

    @classmethod
    def pos2index(cls, pos: tuple[int, int]) -> int:
        if cls.map_width is None:
            raise ValueError('尚未调用 init 进行初始化')
        return pos[0] + pos[1] * cls.map_width

    @classmethod
    def index2_pos(cls, tile_index: int) -> tuple[int, int]:
        if cls.map_width is None:
            raise ValueError('尚未调用 init 进行初始化')
        return tuple(divmod(tile_index, cls.map_width)[::-1])

    @ classmethod
    def init(cls, map_width: int):
        cls.map_width = map_width
