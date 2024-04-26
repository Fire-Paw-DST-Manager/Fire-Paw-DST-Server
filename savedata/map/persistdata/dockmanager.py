# -*- coding: utf-8 -*-
from typing import Union

from pydantic import BaseModel, BeforeValidator, model_validator
from typing_extensions import Annotated

from utils.decode_run import decode
from utils.tileindex2position import PointPos


def index2pos(data: dict[int, Union[int, bool]]) -> dict[tuple[int, int], Union[int, bool]]:
    return {PointPos.index2_pos(i): j for i, j in data.items()}


class Dockmanager(BaseModel):

    # TheSim:ZipAndEncodeString 压缩过的信息
    # {'str': data_str}
    # klei_zip.decode(data_str) -> 'return
    # {
    #   dock_tiles={[tile_index]=bool, ...},
    #   dock_health={[tile_index]=int, ...},
    #   marked_for_delete={[tile_index]=bool, ...}
    # }'
    # str: str

    # 索引是 y * width + x
    # (index % width, index//width)   tuple(reversed(divmod(index, width)))

    # 码头是否是根节点
    dock_tiles: Annotated[dict[tuple[int, int], bool], BeforeValidator(index2pos)]

    # 码头血量
    dock_health: Annotated[dict[tuple[int, int], int], BeforeValidator(index2pos)]

    # 码头是否需要被摧毁
    marked_for_delete: Annotated[dict[tuple[int, int], bool], BeforeValidator(index2pos)]

    # noinspection PyNestedDecorators
    @model_validator(mode='before')
    @classmethod
    def _decode(cls, data):
        return decode(data.get('str'))
