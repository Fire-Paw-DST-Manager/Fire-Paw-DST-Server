# -*- coding: utf-8 -*-

from pydantic import BaseModel


class _Timer(BaseModel):

    # 还有多久计时器结束
    timeleft: float

    # 该计时器首次开始的时间
    initial_time: float

    # 计时器是否暂停
    paused: bool = None

    # 在 longupdate 时是否忽略该项
    blocklongupdate: bool = None


class Worldsettingstimer(BaseModel):

    # 许多东西的计时器，太多了，没法统计，所以不统计
    timers: dict[str, _Timer]
