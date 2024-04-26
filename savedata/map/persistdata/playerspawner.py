# -*- coding: utf-8 -*-
from typing import Literal

from pydantic import BaseModel


class Playerspawner(BaseModel):

    # 记录在世界中生成过的玩家  一些判断比如玩家是否是新玩家时会用到
    _players_spawned: dict[str, Literal[True]]
