# -*- coding: utf-8 -*-

from pydantic import BaseModel


class LunarthrallPlantspawner(BaseModel):

    # 释放虚影的剩余波数
    waves_to_release: int = None

    # 下次设定释放虚影任务的时间   两天一次，每次会设置 2.5-7.5 的延迟(nextspawn)去释放虚影
    spawntask: float = None

    # 存在的裂隙的 GUID
    currentrift: int = None

    # 距离开始释放虚影的时间
    nextspawn: float = None
