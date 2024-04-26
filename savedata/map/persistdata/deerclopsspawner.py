# -*- coding: utf-8 -*-
from typing import Literal, Union
from pydantic import BaseModel


class _Health(BaseModel):
    health: Union[int, float]


class _Location(BaseModel):

    # 横轴
    x: float

    # 高度
    y: float

    # 纵轴
    z: float

    # 位置名
    name: str


class _Knownlocations(BaseModel):
    locations: dict[int, _Location]


class _Data(BaseModel):

    # 巨鹿已摧毁的建筑数量
    structuresDestroyed: int

    # 血量
    health: _Health

    # 记录的位置
    knownlocations: _Knownlocations


class _Deerclops(BaseModel):
    x: float
    z: float
    prefab: Literal['deerclops']
    skinname: str = None
    skin_id: int = None
    alt_skin_ids: int = None


class Deerclopsspawner(BaseModel):
    # 是否处于巨鹿即将到来的预警阶段
    warning: bool

    # 存档的巨鹿数据
    storedhassler: _Deerclops = None

    # 巨鹿的 GUID
    activehassler: int = None
