# -*- coding: utf-8 -*-
from typing import Literal
from pydantic import BaseModel


class Messagebottlemanager(BaseModel):

    # 使用过一次漂流瓶的玩家列表
    player_has_used_a_bottle: dict[str, Literal[True]] = None

    # 遇到过寄居蟹奶奶的玩家列表
    hermit_has_been_found_by: dict[str, Literal[True]] = None
