# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Deerherdspawner(BaseModel):

    # 鹿的 GUID
    # {index: GUID, ...}
    _activedeer: dict[int, int]

    # 上次召唤鹿群的天数
    # 召唤后需要等待秋季长度且是秋天才会再次召唤，召唤延迟是  秋季长度 * 0.2(首秋0.5) * (1 +- 0.33)
    _prevherdsummonday: int
