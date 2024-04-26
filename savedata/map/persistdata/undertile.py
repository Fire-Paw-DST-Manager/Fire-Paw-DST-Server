# -*- coding: utf-8 -*-
from typing import Union

from pydantic import BaseModel, BeforeValidator, model_validator
from typing_extensions import Annotated

from utils.decode_run import decode
from utils.tileindex2position import PointPos


def index2pos(data: dict[int, Union[int, bool]]) -> dict[tuple[int, int], Union[int, bool]]:
    return {PointPos.index2_pos(i): j for i, j in data.items()}


class Undertile(BaseModel):

    # TheSim:ZipAndEncodeString 压缩过的信息
    # {'str': data_str}
    # klei_zip.decode(data_str) -> 'return {underneath_tiles={[tile_index]=tile_code, ...}}'
    # str: str

    # 索引是 y * width + x
    # (index % width, index//width)   tuple(reversed(divmod(index, width)))

    # 进行一些会临时覆盖原本地皮的操作时，用于记录原本地皮种类。比如耕地、码头、裂隙
    underneath_tiles: Annotated[dict[tuple[int, int], int], BeforeValidator(index2pos)]

    # noinspection PyNestedDecorators
    @model_validator(mode='before')
    @classmethod
    def _decode(cls, data):
        return decode(data.get('str'))

