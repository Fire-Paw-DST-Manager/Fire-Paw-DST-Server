# -*- coding: utf-8 -*-
from pydantic import BaseModel

from .beargerspawner import Beargerspawner
from .deerclopsspawner import Deerclopsspawner
from .deerherding import Deerherding
from .deerherdspawner import Deerherdspawner
from .desolationspawner import Desolationspawner
from .dockmanager import Dockmanager
from .farming_manager import FarmingManager
from .forestpetrification import Forestpetrification
from .frograin import Frograin
from .hounded import Hounded
from .klaussackloot import Klaussackloot
from .klaussackspawner import Klaussackspawner
from .lunarriftmutationsmanager import Lunarriftmutationsmanager
from .malbatrossspawner import Malbatrossspawner
from .mermkingmanager import Mermkingmanager
from .messagebottlemanager import Messagebottlemanager
from .moonstormmanager import Moonstormmanager
from .piratespawner import Piratespawner
from .specialeventsetup import Specialeventsetup
from .undertile import Undertile
from .uniqueprefabids import Uniqueprefabids
from .wagpunk_manager import WagpunkManager
from .walkableplatformmanager import Walkableplatformmanager
from .worldmeteorshower import Worldmeteorshower
from .worldsettingstimer import Worldsettingstimer
from .riftspawner import Riftspawner
from .playerspawner import Playerspawner
from .worldstate import Worldstate
from .regrowthmanager import Regrowthmanager
from .chessunlocks import Chessunlocks
from .lunarthrall_plantspawner import LunarthrallPlantspawner
from .flotsamgenerator import Flotsamgenerator

"""
有必要全部处理吗，随着时间推移应该会添加很多，只处理目前需要的吧

有些值在初始状态是空的，或某些状态下为 nil，nil 值的项在保存时会被游戏忽略
所以一些值需要设置缺省值
一些状态在 lua 中的值可能为 true/nil，nil 的时候这一项就会在存档中消失。Literal[True]

有些数据可能在不断地更新中有了新的保存版本，要处理旧的数据吗？
不！那其它所有的旧的都需要处理，不如处理前通过检查保存版本判断是否需要更新，需要的话开启一次把数据都更新到最新版本

"""


class Persistdata(BaseModel):

    # 天体风暴
    moonstormmanager: Moonstormmanager = None

    # 无眼鹿群
    deerherding: Deerherding = None

    # 胡萝卜鼠年
    yotc_raceprizemanager: dict = None

    # 兔人年
    yotb_stagemanager: dict = None

    # 漂流瓶
    messagebottlemanager: Messagebottlemanager = None

    # 邪天翁
    malbatrossspawner: Malbatrossspawner = None

    # 荒芜再生
    desolationspawner: Desolationspawner = None

    # 猎犬袭击
    hounded: Hounded = None

    # 赃物袋刷新
    klaussackspawner: Klaussackspawner = None

    # 海盗袭击
    piratespawner: Piratespawner = None

    # 陨石
    worldmeteorshower: Worldmeteorshower = None

    # 无眼鹿群刷新
    deerherdspawner: Deerherdspawner = None

    # 森林石化冷却
    forestpetrification: Forestpetrification = None

    # 鱼人王
    mermkingmanager: Mermkingmanager = None

    # underneath_tiles 码头下的原始地皮？
    undertile: Undertile = None

    # 一些刷新计时 比如 熊、巨鹿、邪天翁、果蝇王
    worldsettingstimer: Worldsettingstimer = None

    # 再生管理器
    regrowthmanager: Regrowthmanager = None

    # 码头管理器
    dockmanager: Dockmanager = None

    # 赃物袋礼物内容
    klaussackloot: Klaussackloot = None

    # 耕地管理器
    farming_manager: FarmingManager = None

    # 限时活动 冬季盛宴、鸦年华之类
    specialeventsetup: Specialeventsetup = None

    # 熊獾刷新数据
    beargerspawner: Beargerspawner = None

    # 已经刷新在世界中的玩家？
    playerspawner: Playerspawner = None

    # 巨鹿刷新拿数据
    deerclopsspawner: Deerclopsspawner = None

    # 青蛙雨
    frograin: Frograin = None

    # 世界状态信息，季节、时间、雨露值等等
    worldstate: Worldstate = None

    # 已经解锁的棋子
    chessunlocks: Chessunlocks = None

    # 漂浮物 玩家在附近时，海上会刷的一些东西，草、树枝、浮木、残骸等
    flotsamgenerator: Flotsamgenerator = None

    # 唯一物品的 id
    uniqueprefabids: Uniqueprefabids = None

    # 裂隙
    riftspawner: Riftspawner = None

    # 月亮突变生物 座狼、巨鹿、熊
    lunarriftmutationsmanager: Lunarriftmutationsmanager = None

    # 废弃的垃圾
    wagpunk_manager: WagpunkManager = None

    # 船
    walkableplatformmanager: Walkableplatformmanager = None

    lunarthrall_plantspawner: LunarthrallPlantspawner = None
