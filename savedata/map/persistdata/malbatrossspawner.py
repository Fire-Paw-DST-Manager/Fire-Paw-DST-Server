# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Malbatrossspawner(BaseModel):

    # 是否是世界上第一次刷新
    _firstspawn: bool

    # 存在的邪天翁的 GUID
    activeguid: int = None

    # 生成计时器是否已经结束  结束的话说明可以尝试刷新了
    _timerfinished: bool = None
