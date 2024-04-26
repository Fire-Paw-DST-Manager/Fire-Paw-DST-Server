# -*- coding: utf-8 -*-

from pydantic import BeforeValidator, BaseModel, model_validator
from typing_extensions import Annotated

from .persistdata import Persistdata
from .tiles_like_parser import (
    convert_tiles,
    convert_oldtiles,
    convert_nodeidtilemap,
    convert_tiledata,
    convert_oldtiledata,
    convert_nav
)
from .topology import Topology


class Map(BaseModel):

    # necessery

    # 由 tileid 组成的二维图
    tiles: Annotated[list[int], BeforeValidator(convert_tiles)]

    # 世界类型名，如 forest, cave
    prefab: str

    # 地图宽度
    width: int

    # 地图高度
    height: int

    # not necessery

    # 由 nodeid 组成的二维图
    nodeidtilemap: Annotated[list[int], BeforeValidator(convert_nodeidtilemap)] = None

    # 由 不知道什么东西 组成的二维图
    tiledata: Annotated[list[int], BeforeValidator(convert_tiledata)] = None

    # 寻路相关的二维图
    nav: Annotated[list[int], BeforeValidator(convert_nav)] = None

    # 是否隐藏已探索区域。为真时，玩家地图将仅显示当前视野范围，探索过的区域在离开视野后就会变黑。但是数据没有清除，在设否后探索过的区域会重新点亮
    hideminimap: bool = None

    # 各个 node 中各类资源的密度
    generated: dict[str, dict[str, dict[str, float]]] = None

    # 一些记录，比如天体打过多少次、漂流瓶都有谁开过一次等等，很多
    persistdata: Persistdata = None

    # 地皮与其编号的对应关系
    world_tile_map: dict = None

    # 自然生成的小路的数据
    roads: dict = None

    # 陆地之外是海洋还是虚空
    has_ocean: bool = None

    # 拓扑信息，各个 node 的位置、连接信息
    topology: Topology = None


class OldMap(Map):
    tiles: Annotated[list[int], BeforeValidator(convert_oldtiles)]

    tiledata: Annotated[list[int], BeforeValidator(convert_oldtiledata)] = None

    # noinspection PyNestedDecorators
    @model_validator(mode='before')
    @classmethod
    def fix_tiledata(cls, data):
        data['tiledata'] = data.get('tiles')
        return data
