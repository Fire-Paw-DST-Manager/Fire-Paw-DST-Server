# -*- coding: utf-8 -*-

from pydantic import BaseModel


"""新年活动、冬季盛宴、鸦年华、万圣节"""


class Specialeventsetup(BaseModel):

    # 当前活动
    current_event: str

    # 挖掘坟墓时出蝙蝠的累积概率  每挖掘一次概率增加 0.1-0.2，出蝙蝠后清零
    halloween_bats: float

    # 额外开启的活动
    # {index: event_name, ...}
    current_extra_events: dict[int, str]
