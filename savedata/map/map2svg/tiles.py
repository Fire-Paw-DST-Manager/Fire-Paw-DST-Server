# -*- coding: utf-8 -*-
import logging as log
from random import shuffle
from typing import Union

from .map import Map

log.basicConfig(format='%(asctime)s | %(levelname)-8s | %(lineno)4d %(funcName)-10s | - %(message)s',
                datefmt='%y-%m-%d %H:%M:%S',
                level=log.DEBUG)


class Tiles(Map):
    svg_attr_common = {
        'stroke-width': '0.3',
        'stroke-linejoin': "round",
        'stroke-linecap': "round",  # butt round square  无 圆角 方角
    }
    colors = {
        'TEST': 'orange',  # 测试用途

        'IMPASSABLE': '#000000',
        'FAKE_GROUND': '#000000',
        'ROAD': '#D1AE6E',
        'ROCKY': '#C2A163',
        'DIRT': '#F4CC80',
        'SAVANNA': '#DBA545',
        'GRASS': '#C7BD51',
        'FOREST': '#7D8146',
        'MARSH': '#836549',
        'WEB': '#000000',
        'WOODFLOOR': '#AE894A',
        'CARPET': '#B57647',
        'CHECKER': '#CE9E60',
        'CAVE': '#A48F63',
        'FUNGUS': '#57625F',
        'SINKHOLE': '#8C863C',
        'UNDERROCK': '#715E42',
        'MUD': '#8B5F2F',
        'BRICK': '#77734F',
        'BRICK_GLOW': '#787450',
        'TILES': '#6C4643',
        'TILES_GLOW': '#6E4744',
        'TRIM': '#473A2F',
        'TRIM_GLOW': '#6E4744',
        'FUNGUSRED': '#9A6647',
        'FUNGUSGREEN': '#69623A',
        'DECIDUOUS': '#A8784C',
        'DESERT_DIRT': '#E1B863',
        'SCALE': '#5C4929',
        'LAVAARENA_FLOOR': '#78270F',
        'LAVAARENA_TRIM': '#78270F',
        'QUAGMIRE_PEATFOREST': '#A0845A',
        'QUAGMIRE_PARKFIELD': '#A4754A',
        'QUAGMIRE_PARKSTONE': '#E7B879',
        'QUAGMIRE_GATEWAY': '#8B853B',
        'QUAGMIRE_SOIL': '#5A4429',
        'QUAGMIRE_CITYSTONE': '#DBB773',
        'PEBBLEBEACH': '#C0AD6B',
        'METEOR': '#8AA36D',
        'SHELLBEACH': '#C0AD6B',
        'ARCHIVE': '#906137',
        'FUNGUSMOON': '#59523A',
        'FARMING_SOIL': '#554127',

        'OCEAN_COASTAL': '#2E464E',
        'OCEAN_COASTAL_SHORE': '#2F464D',
        'OCEAN_SWELL': '#27354B',
        'OCEAN_ROUGH': '#2B2838',
        'OCEAN_BRINEPOOL': '#3E6467',
        'OCEAN_BRINEPOOL_SHORE': '#2F464D',
        'OCEAN_HAZARDOUS': '#1B181C',
        'OCEAN_WATERLOG': '#3A6165',

        'MONKEY_GROUND': '#BBA969',
        'MONKEY_DOCK': '#85664B',
        'MOSAIC_GREY': '#47362A',
        'MOSAIC_RED': '#702D2E',
        'MOSAIC_BLUE': '#46312D',
        'CARPET2': '#34171E',
    }
    priority = {
        'INVALID': -1,
        'IMPASSABLE': 0,
        'FAKE_GROUND': 0,
        'OCEAN_COASTAL_SHORE': 1,
        'OCEAN_BRINEPOOL_SHORE': 2,
        'OCEAN_COASTAL': 3,
        'OCEAN_WATERLOG': 4,
        'OCEAN_BRINEPOOL': 5,
        'OCEAN_SWELL': 6,
        'OCEAN_ROUGH': 7,
        'OCEAN_HAZARDOUS': 8,
        'QUAGMIRE_GATEWAY': 9,
        'QUAGMIRE_CITYSTONE': 10,
        'QUAGMIRE_PARKFIELD': 11,
        'QUAGMIRE_PARKSTONE': 12,
        'QUAGMIRE_PEATFOREST': 13,
        'ROAD': 14,
        'PEBBLEBEACH': 15,
        'MONKEY_GROUND': 16,
        'SHELLBEACH': 17,
        'MARSH': 18,
        'ROCKY': 19,
        'SAVANNA': 20,
        'FOREST': 21,
        'GRASS': 22,
        'DIRT': 23,
        'DECIDUOUS': 24,
        'DESERT_DIRT': 25,
        'CAVE': 26,
        'FUNGUS': 27,
        'FUNGUSRED': 28,
        'FUNGUSGREEN': 29,
        'FUNGUSMOON': 30,
        'SINKHOLE': 31,
        'UNDERROCK': 32,
        'MUD': 33,
        'ARCHIVE': 34,
        'BRICK_GLOW': 35,
        'BRICK': 36,
        'TILES_GLOW': 37,
        'TILES': 38,
        'TRIM_GLOW': 39,
        'TRIM': 40,
        'METEOR': 41,
        'MONKEY_DOCK': 42,
        'SCALE': 43,
        'WOODFLOOR': 44,
        'CHECKER': 45,
        'MOSAIC_GREY': 46,
        'MOSAIC_RED': 47,
        'MOSAIC_BLUE': 48,
        'CARPET2': 49,
        'CARPET': 50,
        'QUAGMIRE_SOIL': 51,
        'FARMING_SOIL': 52,
        'LAVAARENA_TRIM': 53,
        'LAVAARENA_FLOOR': 54,
    }
    tiles_cache = {
        0: 'TEST',  # 测试用途

        1: 'IMPASSABLE',
        2: 'ROAD',
        3: 'ROCKY',
        4: 'DIRT',
        5: 'SAVANNA',
        6: 'GRASS',
        7: 'FOREST',
        8: 'MARSH',
        9: 'WEB',
        10: 'WOODFLOOR',
        11: 'CARPET',
        12: 'CHECKER',
        13: 'CAVE',
        14: 'FUNGUS',
        15: 'SINKHOLE',
        16: 'UNDERROCK',
        17: 'MUD',
        18: 'BRICK',
        19: 'BRICK_GLOW',
        20: 'TILES',
        21: 'TILES_GLOW',
        22: 'TRIM',
        23: 'TRIM_GLOW',
        24: 'FUNGUSRED',
        25: 'FUNGUSGREEN',
        30: 'DECIDUOUS',
        31: 'DESERT_DIRT',
        32: 'SCALE',
        33: 'LAVAARENA_FLOOR',
        34: 'LAVAARENA_TRIM',
        35: 'QUAGMIRE_PEATFOREST',
        36: 'QUAGMIRE_PARKFIELD',
        37: 'QUAGMIRE_PARKSTONE',
        38: 'QUAGMIRE_GATEWAY',
        39: 'QUAGMIRE_SOIL',
        41: 'QUAGMIRE_CITYSTONE',
        42: 'PEBBLEBEACH',
        43: 'METEOR',
        44: 'SHELLBEACH',
        45: 'ARCHIVE',
        46: 'FUNGUSMOON',
        47: 'FARMING_SOIL',
        200: 'FAKE_GROUND',
        201: 'OCEAN_COASTAL',
        202: 'OCEAN_COASTAL_SHORE',
        203: 'OCEAN_SWELL',
        204: 'OCEAN_ROUGH',
        205: 'OCEAN_BRINEPOOL',
        206: 'OCEAN_BRINEPOOL_SHORE',
        207: 'OCEAN_HAZARDOUS',
        208: 'OCEAN_WATERLOG',
        256: 'MONKEY_GROUND',
        257: 'MONKEY_DOCK',
        258: 'MOSAIC_GREY',
        259: 'MOSAIC_RED',
        260: 'MOSAIC_BLUE',
        261: 'CARPET2',
        65535: 'INVALID',
    }

    def __init__(self, map_data: list[Union[int, Union[list[int], tuple[int]]]], tile_id_name: dict = None, is_flipped: bool = True):
        if tile_id_name is not None:
            self.tile_names = {j: i for i, j in tile_id_name.items()}
        else:
            log.warning('未传入地皮名与地皮编号对应的关系，将使用预存的对应关系，对应关系并不一定准确')
            self.tile_names = self.tiles_cache

        super().__init__(map_data, is_flipped=is_flipped)

    def _get_tile_names(self) -> dict[int, str]:
        for i in self.paths:
            if i not in self.tile_names:
                self.tile_names[i] = str(i)
        return self.tile_names

    def _get_priority(self) -> list[int]:
        return sorted(list(self.paths), key=lambda x: self.priority.get(self.tile_names.get(x), 0))

    def _get_tile_colors(self) -> dict[str, str]:
        colors = []
        tile_names = self._get_tile_names()
        for i in self.paths:
            i = tile_names[i]
            if i not in self.colors:
                if not colors:
                    colors = self.svg_colors.copy()
                    shuffle(colors)
                color = colors.pop()
                log.warning(f'{i} 没有对应的颜色，已选取随机颜色：{color}')
                self.colors[str(i)] = color
        return self.colors
