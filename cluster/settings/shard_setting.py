# -*- coding: utf-8 -*-
from typing import Union

from pydantic import BaseModel, Field, model_serializer

from ..sections import (
    NetworkForShard,
    SteamForShard,
    AccountForShard,
    ShardForShard
)


class ShardSetting(BaseModel):
    # 单个世界分片的设置 cluster/(Master|Caves)/server.ini

    NETWORK: NetworkForShard = Field(default_factory=NetworkForShard)

    SHARD: ShardForShard = Field(default_factory=ShardForShard)

    ACCOUNT: AccountForShard = Field(default_factory=AccountForShard)

    STEAM: SteamForShard = Field(default_factory=SteamForShard)

    @model_serializer
    def _(self) -> dict[str, Union[NetworkForShard, ShardForShard, AccountForShard, SteamForShard]]:
        result = {}
        allow_key = ['NETWORK', 'SHARD', 'ACCOUNT', 'STEAM']

        for key, value in self:
            if key in allow_key:
                result[key] = value

        return result
