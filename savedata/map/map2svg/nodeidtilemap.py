# -*- coding: utf-8 -*-
import logging as log
from random import shuffle
from typing import Union

from .map import Map

log.basicConfig(format='%(asctime)s | %(levelname)-8s | %(lineno)4d %(funcName)-10s | - %(message)s',
                datefmt='%y-%m-%d %H:%M:%S',
                level=log.DEBUG)


class NodeIdTileMap(Map):
    svg_attr_common = {
        'stroke-width': '0',
        'stroke-linejoin': "round",
        'stroke-linecap': "round",  # butt round square  无 圆角 方角
    }

    colors = {}

    def __init__(self, map_data: list[Union[int, Union[list[int], tuple[int]]]], node_ids: list = None, is_flipped: bool = True):
        if node_ids is not None:
            self.tile_names = {i + 1: j for i, j in enumerate(node_ids)}
            self._random_color = False
        else:
            log.warning('未传入 id 与 name 对应的关系，将使用 id 作为 name')
            self.tile_names = {}
            self._random_color = True

        self.tile_names[0] = 'background'

        super().__init__(map_data, is_flipped=is_flipped)

    def _get_tile_names(self) -> dict[int, str]:
        for i in self.paths:
            if i not in self.tile_names:
                self.tile_names[i] = str(i)
        return self.tile_names

    def _get_tile_colors(self) -> dict[str, str]:
        colors = []
        for i in self.paths:
            i = self.tile_names[i]
            if i not in self.colors:
                if not colors:
                    colors = self.svg_colors.copy()
                    shuffle(colors)
                color = colors.pop()
                log.warning(f'{i} 没有对应的颜色，已选取随机颜色：{color}')
                self.colors[str(i)] = color
        return self.colors
