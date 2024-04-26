# -*- coding: utf-8 -*-

from pydantic import BaseModel


class _Shipdatas(BaseModel):

    # 船的 GUID
    boat: int

    # 船长的 GUID
    caption: int

    # 船员们的 GUID
    # {index: GUID, ...}
    crew: dict[int, int]


class Piratespawner(BaseModel):

    # 只定义了，没用到  值为 -1
    _scheduledtask: int

    # 距下次海盗袭击剩余时间  减短速度与 女王与离女王最近的玩家的距离 成反比增加倍数
    nextpiratechance: float

    # 只定义了，没用到，每次来海盗的数量？  值为 1
    maxpirates: int

    # 只定义了，没用到，袭击开始时海盗延迟多久刷新？  值为 20
    minspawndelay: int

    # 只定义了，没用到，袭击开始时海盗延迟多久刷新？  值为 30
    maxspawndelay: int

    # 赃物藏匿点的 GUID
    currentstash: int = None

    # 海盗船的信息
    shipdatas: dict[int, _Shipdatas]
