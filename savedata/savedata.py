"""
游戏内调用klei的算法对字符串编码
TheSim:SetPersistentString('123456789.lua', 'ABC', is_encode_save_bool [, callback]) => \
~/Documents/Klei/DoNotStarveTogether/446835953/client_save/123456789.lua
TheSim:GetPersistentString("123456789.lua", function(load_success, str) print(str) end, false)
TheSim:DecodeAndUnzipString('str') -> str
TheSim:ZipAndEncodeString('str') -> strwd


"""

from json import dumps
from pathlib import Path
from typing import Union

import lupa.lua51 as lupa

from .map import Map, OldMap
from utils.table2dict import Converter
from utils.tileindex2position import PointPos


class SaveData:
    def __init__(self, file_path: str):
        file = Path(file_path)
        if not file.is_file():
            if file.exists():
                raise ValueError(f'路径指向的不是文件类型 {file.absolute()}')
            raise ValueError(f'路径不存在 {file.absolute()}')

        self._file = file

        # map meta world_network mods ents  snapshot super    playerinfo
        # 正常存档中会有 (map 地图数据, meta 存档基础数据, world_network 世界数据, mods 模组数据, ents 实例数据)
        # 存档时如果游戏还在运行且有玩家，会有 snapshot，记录当前玩家信息
        # super 在本地档，如果调用了某些指令，或使用了控制台，会为 true，重启后会重置
        # 在专服 还没测
        # TheNet:SerializeWorldSession(data, session_identifier, ENCODE_SAVES, callback, metadataStr or "")
        #                              table str                 bool          function  str
        # data 会按特定的格式转为 lua 代码，值为 nil 的将被忽略，所以 super 虽然每次保存世界都会被设置，但不是 true 就是 nil，nil时被忽略了
        # 关于特定的格式，2021.08.12 之前版本是返回一个 table 的格式，之后修改为调用函数返回每一项最后合成 table
        # TheNet:SerializeWorldSession({["123"]="123"}, "12345", true, function() end, "")

        # 没有找到 playerinfo 相关的信息，但是有个存档中确实有，不知道会不会是 mod 导致的，应该不需要考虑

        # 所有数据
        self.all_data = self._load()

        # 正常存档一定会有的数据
        self.map: Union[Map, OldMap]
        self.meta: dict = {}
        self.world_network: dict = {}
        self.mods: dict = {}
        self.ents: dict = {}

        # 不一定会有的数据
        self.snapshot: dict = {}
        self.super: bool = False

        # 除了以上之外的数据
        self.extra_data: dict = {}

        self._format_data()

    def _verification(self):
        """
        验证并处理数据
        """
        # 在实例化 map 对象之前，为其中某些数据建立坐标与索引的转换关系
        PointPos.init(self.map.get('width'))
        self._map_process()

    def _map_process(self):
        """
        if not savedata.map.tiledata then
            map:SetFromStringLegacy(savedata.map.tiles)
        else
            map:SetFromString(savedata.map.tiles)
            map:SetMapDataFromString(savedata.map.tiledata)
        end
        """
        self.map: dict
        if 'tiledata' in self.map:
            self.map = Map(**self.map)
        else:
            self.map = OldMap(**self.map)

    def _format_data(self):
        data_list = list(self.all_data)
        contrast_necessary = {
            "map": True,
            "meta": True,
            "world_network": True,
            "mods": True,
            "ents": True,
            "snapshot": False,
            "super": False,
        }
        for key, necessary in contrast_necessary.items():
            if key in data_list:
                self.__setattr__(key, self.all_data[key])
                data_list.remove(key)
                continue
            if necessary:
                raise ValueError(f'缺少 {key} 数据')

        for k in data_list:
            self.extra_data[k] = self.all_data[k]

        self._verification()

    def _load(self):
        with self._file.open('r', encoding='utf-8') as file:
            savedata = file.read().removesuffix('\x00')

        if not savedata:
            return {}

        lua = lupa.LuaRuntime()
        xx = lua.eval('loadstring(python.eval("savedata"))()')
        return Converter().table_dict(xx)

    def save(self, save_path: str = None):
        if save_path is None:
            save_path = f'{str(self._file.absolute()).removesuffix(self._file.suffix)}.json'

        file = Path(save_path)
        if file.exists():
            ValueError(f'文件已存在 {file.absolute()}')

        file.write_text(self._json(), encoding='utf-8')

    def __repr__(self):
        return f'<SaveData: {self._file.absolute()}>'

    def _json(self):
        return dumps(self.all_data)
