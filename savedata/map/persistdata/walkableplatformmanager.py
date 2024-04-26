# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Walkableplatformmanager(BaseModel):

    # 为 platform 获取 uid 时，在此基础上加 1，因此记录该值，避免获取到重复的 uid
    lastuid: int
