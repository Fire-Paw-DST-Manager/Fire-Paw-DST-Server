# -*- coding: utf-8 -*-
from typing import Literal

from pydantic import BaseModel


class _Spawninfo(BaseModel):

    # 下一条猎犬刷新时间
    timetonext: float

    # 等待刷新的猎犬数量
    count: int

    # 玩家存活时间 或 同批次玩家平均存活时间
    averageplayerage: float


class _Missingplayerspawninfo(BaseModel):
    # 预警期间猎犬咆哮间隔
    _announcewarningsoundinterval: int

    # 袭击等待时间  还有多久刷狗
    _timetoattack: float

    # 是否处于预警状态
    _warning: bool

    # 距离下次猎犬咆哮时间
    _timetonextwarningsound: float

    # 预警持续时间
    _warnduration: int

    # 袭击信息
    _spawninfo: _Spawninfo = None

    # 玩家在陆地还是海上，海上的话不来狗
    _targetstatus: Literal['land', 'water'] = None


class Hounded(BaseModel):

    # 错过猎犬袭击的玩家信息  在袭击前下线的玩家
    missingplayerspawninfo: dict[str, _Missingplayerspawninfo]

    # 是否处于预警状态
    warning: bool

    # 袭击等待时间  还有多久猎犬刷新
    timetoattack: float

    # 预警持续时间  从预警开始到猎犬刷新
    warnduration: int

    # 是否要准备袭击计划  关袭击或没人的时候为否
    attackplanned: bool
