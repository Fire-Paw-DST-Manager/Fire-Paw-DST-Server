# -*- coding: utf-8 -*-

from pydantic import BaseModel


class _Position(BaseModel):

    x: float

    z: float


class _Timer(BaseModel):

    # 再生剩余时间
    regrowtime: int

    # 物品代码
    product: str

    # 坐标信息
    position: _Position


class Regrowthmanager(BaseModel):

    # 再生计时器
    # carrot_planted, flower, rabbithole, catcoonden, flower_cave, flower_cave_double, flower_cave_triple, lightflier_flower, reeds, cactus, oasis_cactus, cave_banana_tree, red_mushroom, green_mushroom, blue_mushroom
    # {name: {index: _Timer, ...}, ...}
    timers: dict[str, dict[int, _Timer]]
