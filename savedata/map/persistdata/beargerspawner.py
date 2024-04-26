# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Beargerspawner(BaseModel):

    # 上次熊死亡时的天数
    lastKillDay: int = None

    # 是否处于熊即将到来的预警阶段
    warning: bool

    # 已经刷新的熊的数量
    numSpawned: int

    # 存活的刷新的熊的 GUID，代码刷的不算，一般只有一个
    # {index: GUID, ...}
    activehasslers: dict[int, int]

    # 等待刷新的熊的数量  0 或 1
    numToSpawn: int
