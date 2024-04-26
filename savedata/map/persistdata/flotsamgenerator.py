# -*- coding: utf-8 -*-

from pydantic import BaseModel


class Flotsamgenerator(BaseModel):

    # 刷新间隔的最大值
    maxspawndelay: int

    # 刷新间隔的最小值
    minspawndelay: int

    # 漂浮物的最大共存数量？有定义，但是没有使用
    maxflotsam: int

    # 以下三个互相对应

    # 漂浮物的 GUID
    # {index: GUID, ...}
    flotsam: dict[int, int]

    # 漂浮物是否有 flotsam 标签，带标签的会阻止附近产生漂浮物
    # 漂浮物主要有两种，一种是 草树枝浮木海洋残骸船碎片，带标签
    # 另一种是 漂流瓶，不带标签
    # 此外，周期性产生的物品比如电羊的刷新、格罗姆便便等，在水上生成时，也会调用这里，不带标签
    # {index: bool, ...}
    flotsamtag: dict[int, bool]

    # 漂浮物距离消失的时间
    # {index: time, ...}
    time: dict[int, float]
