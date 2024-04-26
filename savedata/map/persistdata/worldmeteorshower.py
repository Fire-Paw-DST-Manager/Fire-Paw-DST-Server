# -*- coding: utf-8 -*-
from typing import Union
from pydantic import BaseModel


class Worldmeteorshower(BaseModel):

    # 降落带有天体宝球的可疑的巨石的概率 0.34 0.68 1
    moonrockshell_chance: Union[float, int]
