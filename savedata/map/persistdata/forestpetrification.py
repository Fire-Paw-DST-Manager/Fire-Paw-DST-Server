# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Forestpetrification(BaseModel):

    # 距离下次森林石化的时间
    cooldown: int
