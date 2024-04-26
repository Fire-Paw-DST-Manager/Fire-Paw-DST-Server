# -*- coding: utf-8 -*-
from typing import Literal, Union
from pydantic import BaseModel


_moonphase = Literal['new', 'quarter', 'half', 'threequarter', 'full']
_season = Literal['spring', 'summer', 'autumn', 'winter']
_dayphase = Literal['day', 'dusk', 'night']
_nightmarephase = Literal['calm', 'warn', 'wild', 'dawn']
_precipitation = Literal['none', 'rain', 'snow', 'lunarhail']


class Worldstate(BaseModel):
    
    springlength: int
    summerlength: int
    autumnlength: int
    winterlength: int
    isspring: bool
    issummer: bool
    isautumn: bool
    iswinter: bool

    season: _season
    # 当前季节已过天数  不包括今天
    elapseddaysinseason: int
    # 当前季节剩余天数  这两项相加不一定等于当前季节天数，比如已过几天后被 mod 调整为季节第一天，此时已过天数不会清零
    remainingdaysinseason: int
    # 当前季节已过百分比 remainingdaysinseason / totaldaysinseason
    seasonprogress: Union[int, float]

    moonphase: _moonphase
    # 新月
    isnewmoon: bool
    # 满月
    isfullmoon: bool
    # 盈月 新月当天的天亮 -> 满月前一天的天亮  满月前一天会变成亏月，不知道为什么
    iswaxingmoon: bool
    cavemoonphase: _moonphase
    iscavenewmoon: bool
    iscavefullmoon: bool
    iscavewaxingmoon: bool

    nightmarephase: Literal['none', _nightmarephase]
    isnightmarecalm: bool
    isnightmarewarn: bool
    isnightmarewild: bool
    isnightmaredawn: bool
    # 本次暴动周期已过时间  开始 -> 结束 归零 下一次开始 -> 结束
    nightmaretime: Union[int, float]
    # 当前暴动阶段已过时间占总时间的百分比
    nightmaretimeinphase: Union[int, float]

    # 下雨
    israining: bool
    # 下雪
    issnowing: bool
    # 月亮冰雹
    islunarhailing: bool = None
    # 酸雨
    isacidraining: bool = None
    lunarhaillevel: Union[int, float] = None
    snowlevel: Union[int, float]
    issnowcovered: bool
    iswet: bool
    wetness: Union[int, float]
    # 水分值上限
    moistureceil: Union[int, float]
    # 水分值
    moisture: Union[int, float]
    # 降水趋势？ 降水时为 1，降水时为 超出下限的值除以上下限的差值 [0, 1]
    pop: Union[Literal[0, 1], float]
    # 降水速率
    # 相当于 pop 再处理之后的值，考虑更多因素比如降水类型与世界设置
    # 正常情况下计算方式为 min([0.1 + 0.9 * sin(pop * PI)], 峰值降水速率) [0, 1]
    precipitationrate: Union[Literal[0, 1], float]
    # 降水类型
    precipitation: _precipitation

    # 当前温度
    temperature: Union[int, float]

    # 已循环过的天数 当前天数 = cycles + 1
    cycles: int

    # 与天体风暴的开启与关闭绑定 天体是否处于唤醒状态？
    isalterawake: bool

    phase: _dayphase
    isday: bool
    isdusk: bool
    isnight: bool
    cavephase: _dayphase
    iscaveday: bool
    iscavedusk: bool
    iscavenight: bool
    # 当天已过时间占全天的百分比
    time: Union[int, float]
    # 当前阶段已过时间占整个阶段的百分比  白天、黄昏、夜晚 三个阶段
    timeinphase: Union[int, float]
