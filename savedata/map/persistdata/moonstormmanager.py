# -*- coding: utf-8 -*-
from typing import Union, Literal

from pydantic import BaseModel


class Moonstormmanager(BaseModel):

    # 月亮风暴已循环次数
    _alterguardian_defeated_count: int

    # 遇到过风暴中科学家的玩家列表
    metplayers: dict[str, Literal[True]]

    # 风暴已持续天数  未开启过风暴时该项为 nil
    stormdays: int = None

    # 尝试开始风暴
    startstormtask: Literal[True] = None

    # 尝试在该 node 内开始风暴
    currentbasenodeindex: int = None

    # 当前风暴所在 nodes
    # {index: node_index, ...}
    currentnodes: dict[int, int] = None

    # 是否是天体控制的月相
    moonstyle_altar: Literal[True] = None
