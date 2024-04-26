# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Riftspawner(BaseModel):

    # 存在的裂隙们的 GUIDs
    # {index: GUID, ...}
    rift_guids: dict[int, int]

    # 是否允许暗影裂隙刷新
    _shadow_enabled: bool

    # 生成计时器是否已经结束 结束的话尝试生成裂隙
    timerfinished: bool = None

    # 是否允许月亮裂隙刷新
    _lunar_enabled: bool

