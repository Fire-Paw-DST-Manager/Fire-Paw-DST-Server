# -*- coding: utf-8 -*-
from typing import Union

from pydantic import BaseModel, BeforeValidator, model_validator
from typing_extensions import Annotated

from utils.decode_run import decode
from utils.tileindex2position import PointPos


class _WeedSpawn(BaseModel):

    # 目标耕地索引
    loc: int

    # 将会在当前季节过去多久后萌芽
    season_time: float


def _decode_nutrient(n: int):
    return (n >> 16) & 0xff, (n >> 8) & 0xff, n & 0xff


def _recover_nutrient(d: dict[int, int]) -> dict[int, tuple[int, int, int]]:
    return {PointPos.index2_pos(i): _decode_nutrient(j) for i, j in d.items()}


def index2pos(data: dict[int, Union[int, bool]]) -> dict[tuple[int, int], Union[int, bool]]:
    return {PointPos.index2_pos(i): j for i, j in data.items()}


class FarmingManager(BaseModel):

    # TheSim:ZipAndEncodeString 压缩过的信息
    # {'str': data_str}
    # klei_zip.decode(data_str) -> '
    # return {
    #   remaining_weed_spawns={{loc=int, season_time=float}, ...},  # 值为空时不存在
    #   lordfruitfly_queued_spawn=bool,
    #   nutrientgrid={[tile_index]=int, ...},
    #   moisturegrid={[tile_index]=int, ...},
    #   version=int
    # }'
    # str: str

    # 索引是 y * width + x
    # (index % width, index//width)   tuple(reversed(divmod(index, width)))

    # 等待萌芽的杂草信息
    remaining_weed_spawns: dict[int, _WeedSpawn] = None

    # 果蝇王计时器是否已关闭
    lordfruitfly_queued_spawn: bool

    # 耕地的养分数据
    # {tile_index: nutrient} -> {tile_index: (催长剂（蓝色方块）, 堆肥（黄色线条）, 便便（红色三角）)}
    nutrientgrid: Annotated[dict[tuple[int, int], tuple[int, int, int]], BeforeValidator(_recover_nutrient)]

    # 耕地的水分数据
    # {tile_index: moisture}
    moisturegrid: Annotated[dict[tuple[int, int], Union[float, int]], BeforeValidator(index2pos)]

    # 保存数据的版本，有两个版本 1、2
    version: int

    # noinspection PyNestedDecorators
    @model_validator(mode='before')
    @classmethod
    def _decode(cls, data):
        return decode(data.get('str'))
