# -*- coding: utf-8 -*-

from pydantic import BaseModel


class WagpunkManager(BaseModel):
    # 随裂隙的激活被激活

    # 距离废弃垃圾刷新的时间   首次激活与旧的被敲才会有这个，时间是 4 - 7 天
    nextspawntime: float = None

    # 距离下次提示废弃垃圾位置的剩余时间   废弃站刷新时会提示一次（此次不算在hintcount），下次提示间隔随提示次数由 1 -> 15 天。加上刷新时的一次，共提示 11 次
    nexthinttime: float = None

    # 沃格斯塔夫提示过废弃垃圾位置的次数 超过 10 则不会再提示
    hintcount: int = None

    # 拾荒疯猪未刷新时，若附近 40 单位无玩家，则直接刷在大垃圾场中，若有玩家，老瓦则会出来提示玩家离开并在 30s 后再次判定刷新
    # 若拾荒疯猪已刷新，则会选择某个 远离玩家40单位、远离上个刷新点所在node的中心300单位 的主大陆地面node内刷新
    # 最近一次废弃垃圾刷新位置所在的 nodeid
    currentnodeindex: int = None

    # 是否已为初始大垃圾场放置栅栏 一个档会且只会设置一次 true，所以没什么用
    spawnedfences: int = None
