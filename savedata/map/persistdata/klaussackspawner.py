# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Klaussackspawner(BaseModel):

    # 已刷赃物袋的数量  冬天结束重置为 0
    spawnsthiswinter: int
