# -*- coding: utf-8 -*-
"""
ModManager.currentlyloadingmod
ModManager:GetPostInitFns
"""
import os
from json import loads
import lupa.lua51 as lupa

# 游戏 data 文件夹的位置
data_path = r"C:\Program Files (x86)\Steam\steamapps\common\Don't Starve Together\data"

lua = lupa.LuaRuntime()


def prework():
    lua.globals().package.path = rf"{data_path}\databundles\scripts\?.lua"
    old_cwd = os.getcwd()
    os.chdir(data_path)
    lua.execute("""
    package.assetpath = {{path = ''}}
    MOD_API_VERSION = 10
    APP_VERSION = "DEV_UNKNOWN"
    utf8strtolower, utf8strtoupper, utf8strlen, utf8substr, utf8char = '', '', '', '', ''
    BRANCH = "staging"
    PLATFORM = "WIN32_STEAM"
    POT_GENERATION = true
    function IsConsole() return false end
    function IsPS4() return false end
    function IsXB1() return false end
    function IsRail() return false end
    function IsSteam() return true end
    function IsNotConsole() return true end
    Profile = {}
    function Profile:GetLanguageID() return LANGUAGE.CHINESE_S end
    function Profile:GetWorldCustomizationPresets() return {} end
    TheNet = {}
    function TheNet.IsDedicated() return false end
    function kleifileexists(filepath) local file = io.open(filepath, "rb") if file then file:close() end return file ~= nil end
    function module(a) end
    """)
    lua.require('strict')
    lua.require('class')

    lua.require('constants')

    lua.execute("""
    Asset = Class( function(self, type, file, param)
        self.type = type
        self.file = file
        self.param = param
    end)""")
    lua.require('tilemanager')

    # 这里需要解压 images.zip 到 data/levels/textures 下，用于文件验证
    from os.path import exists
    if not exists(r'levels\textures\images'):
        from zipfile import ZipFile
        with ZipFile('databundles/images.zip') as images:
            images.extractall(r'levels\textures')
    lua.require('tiledefs')

    lua.require("json")

    os.chdir(old_cwd)


"""
现在获取的会缺失一部分，后面再查原因，下面这个是全的  缺少的不是真正的地皮，比如 impassable，世界之外才是这个；各种 noise，地图生成期间才会使用到；各种 wall，这个不知道具体作用；还有一些其他的，这里应该不用考虑这些
GetWorldTileMap()
"""


prework()

world_tiles = loads(lua.eval('encode(WORLD_TILES)'))
# y = loads(lua.eval('encode(INVERTED_WORLD_TILES)'))
ground_names = loads(lua.eval('encode(GROUND_NAMES)'))
print(world_tiles)
print(ground_names)

# INVALID id 是 65535，以前 ground_names 是一个长度为 65536 的列表，现在会被截断，只保留到最大有效地皮的 id
world_tiles.pop('INVALID')

# 游戏本体的所有地皮 代码内名称与编号之间的关系
all_code_id = {i: world_tiles[i] for i in sorted(world_tiles, key=lambda x: world_tiles[x])}
_ = {
    "IMPASSABLE": 1,
    "ROAD": 2,
    "ROCKY": 3,
    "DIRT": 4,
    "SAVANNA": 5,
    "GRASS": 6,
    "FOREST": 7,
    "MARSH": 8,
    "WOODFLOOR": 10,
    "CARPET": 11,
    "CHECKER": 12,
    "CAVE": 13,
    "FUNGUS": 14,
    "SINKHOLE": 15,
    "UNDERROCK": 16,
    "MUD": 17,
    "BRICK": 18,
    "BRICK_GLOW": 19,
    "TILES": 20,
    "TILES_GLOW": 21,
    "TRIM": 22,
    "TRIM_GLOW": 23,
    "FUNGUSRED": 24,
    "FUNGUSGREEN": 25,
    "DECIDUOUS": 30,
    "DESERT_DIRT": 31,
    "SCALE": 32,
    "LAVAARENA_FLOOR": 33,
    "LAVAARENA_TRIM": 34,
    "QUAGMIRE_PEATFOREST": 35,
    "QUAGMIRE_PARKFIELD": 36,
    "QUAGMIRE_PARKSTONE": 37,
    "QUAGMIRE_GATEWAY": 38,
    "QUAGMIRE_SOIL": 39,
    "QUAGMIRE_CITYSTONE": 41,
    "PEBBLEBEACH": 42,
    "METEOR": 43,
    "SHELLBEACH": 44,
    "ARCHIVE": 45,
    "FUNGUSMOON": 46,
    "FARMING_SOIL": 47,
    "FUNGUSMOON_NOISE": 120,
    "METEORMINE_NOISE": 121,
    "METEORCOAST_NOISE": 122,
    "DIRT_NOISE": 123,
    "ABYSS_NOISE": 124,
    "GROUND_NOISE": 125,
    "CAVE_NOISE": 126,
    "FUNGUS_NOISE": 127,
    "FAKE_GROUND": 200,
    "OCEAN_COASTAL": 201,
    "OCEAN_COASTAL_SHORE": 202,
    "OCEAN_SWELL": 203,
    "OCEAN_ROUGH": 204,
    "OCEAN_BRINEPOOL": 205,
    "OCEAN_BRINEPOOL_SHORE": 206,
    "OCEAN_HAZARDOUS": 207,
    "OCEAN_WATERLOG": 208,
    "MONKEY_GROUND": 256,
    "MONKEY_DOCK": 257,
    "MOSAIC_GREY": 258,
    "MOSAIC_RED": 259,
    "MOSAIC_BLUE": 260,
    "CARPET2": 261,
    "INVALID": 65535,
}
print(all_code_id)

# 游戏本体的所有地皮 代码内名称与注册地皮时附带的名称之间的关系 这里的名称并不正规，比如可以重名，更多的是表达这是属于什么细分类型
all_code_name = {i: ground_names[j - 1] for i, j in all_code_id.items()}
_ = {
    "IMPASSABLE": "Impassable",
    "ROAD": "Road",
    "ROCKY": "Rocky",
    "DIRT": "Dirt",
    "SAVANNA": "Savanna",
    "GRASS": "Grass",
    "FOREST": "Forest",
    "MARSH": "Marsh",
    "WOODFLOOR": "Wood",
    "CARPET": "Carpet",
    "CHECKER": "Checkers",
    "CAVE": "Cave",
    "FUNGUS": "Blue Fungus",
    "SINKHOLE": "Sinkhole",
    "UNDERROCK": "Under Rock",
    "MUD": "Mud",
    "BRICK": "Glowing Bricks",
    "BRICK_GLOW": "Pale Bricks",
    "TILES": "Glowing Tiles",
    "TILES_GLOW": "Pale Tiles",
    "TRIM": "Glowing Trim",
    "TRIM_GLOW": "Pale Trim",
    "FUNGUSRED": "Red Fungus",
    "FUNGUSGREEN": "Green Fungus",
    "DECIDUOUS": "Deciduous",
    "DESERT_DIRT": "Desert Dirt",
    "SCALE": "Scale",
    "LAVAARENA_FLOOR": "Forge Floor",
    "LAVAARENA_TRIM": "Forge Trim",
    "QUAGMIRE_PEATFOREST": "Gorge Peat Forest",
    "QUAGMIRE_PARKFIELD": "Gorge Park Grass",
    "QUAGMIRE_PARKSTONE": "Gorge Park Path",
    "QUAGMIRE_GATEWAY": "Gorge Gateway",
    "QUAGMIRE_SOIL": "Gorge Soil",
    "QUAGMIRE_CITYSTONE": "Gorge Citystone",
    "PEBBLEBEACH": "Pebble Beach",
    "METEOR": "Meteor",
    "SHELLBEACH": "Shell Beach",
    "ARCHIVE": "Archives",
    "FUNGUSMOON": "Moon Fungus",
    "FARMING_SOIL": "Farming Soil",
    "FUNGUSMOON_NOISE": "FUNGUSMOON_NOISE",
    "METEORMINE_NOISE": "METEORMINE_NOISE",
    "METEORCOAST_NOISE": "METEORCOAST_NOISE",
    "DIRT_NOISE": "DIRT_NOISE",
    "ABYSS_NOISE": "ABYSS_NOISE",
    "GROUND_NOISE": "GROUND_NOISE",
    "CAVE_NOISE": "CAVE_NOISE",
    "FUNGUS_NOISE": "FUNGUS_NOISE",
    "FAKE_GROUND": "Fake Ground",
    "OCEAN_COASTAL": "Coastal Ocean",
    "OCEAN_COASTAL_SHORE": "Coastal Shore",
    "OCEAN_SWELL": "Swell Ocean",
    "OCEAN_ROUGH": "Rough Ocean",
    "OCEAN_BRINEPOOL": "Brinepool",
    "OCEAN_BRINEPOOL_SHORE": "Brinepool Shore",
    "OCEAN_HAZARDOUS": "Hazardous Ocean",
    "OCEAN_WATERLOG": "Waterlogged Ocean",
    "MONKEY_GROUND": "Pirate Beach",
    "MONKEY_DOCK": "Docks",
    "MOSAIC_GREY": "Grey Mosaic",
    "MOSAIC_RED": "Red Mosaic",
    "MOSAIC_BLUE": "Blue Mosaic",
    "CARPET2": "Carpet",

    "INVALID": None,
}

# 与 all_code_name 相似，只是把键由 code 换成了 id
all_id_name = {i: ground_names[i - 1] for i in all_code_id.values()}
# print(all_id_name)
_ = {1: 'Impassable',
     2: 'Road',
     3: 'Rocky',
     4: 'Dirt',
     5: 'Savanna',
     6: 'Grass',
     7: 'Forest',
     8: 'Marsh',
     10: 'Wood',
     11: 'Carpet',
     12: 'Checkers',
     13: 'Cave',
     14: 'Blue Fungus',
     15: 'Sinkhole',
     16: 'Under Rock',
     17: 'Mud',
     18: 'Glowing Bricks',
     19: 'Pale Bricks',
     20: 'Glowing Tiles',
     21: 'Pale Tiles',
     22: 'Glowing Trim',
     23: 'Pale Trim',
     24: 'Red Fungus',
     25: 'Green Fungus',
     30: 'Deciduous',
     31: 'Desert Dirt',
     32: 'Scale',
     33: 'Forge Floor',
     34: 'Forge Trim',
     35: 'Gorge Peat Forest',
     36: 'Gorge Park Grass',
     37: 'Gorge Park Path',
     38: 'Gorge Gateway',
     39: 'Gorge Soil',
     41: 'Gorge Citystone',
     42: 'Pebble Beach',
     43: 'Meteor',
     44: 'Shell Beach',
     45: 'Archives',
     46: 'Moon Fungus',
     47: 'Farming Soil',
     120: 'FUNGUSMOON_NOISE',
     121: 'METEORMINE_NOISE',
     122: 'METEORCOAST_NOISE',
     123: 'DIRT_NOISE',
     124: 'ABYSS_NOISE',
     125: 'GROUND_NOISE',
     126: 'CAVE_NOISE',
     127: 'FUNGUS_NOISE',
     200: 'Fake Ground',
     201: 'Coastal Ocean',
     202: 'Coastal Shore',
     203: 'Swell Ocean',
     204: 'Rough Ocean',
     205: 'Brinepool',
     206: 'Brinepool Shore',
     207: 'Hazardous Ocean',
     208: 'Waterlogged Ocean',
     256: 'Pirate Beach',
     257: 'Docks',
     258: 'Grey Mosaic',
     259: 'Red Mosaic',
     260: 'Blue Mosaic',
     261: 'Carpet'}

"""
local GroundTiles = require("worldtiledefs")
io.open("ground_properties.json", "w"):write(json.encode(GroundTiles.ground))
-- 顺序就是地皮优先级顺序，未被模组修改的话，就是 tiledefs.lua 内添加地皮的顺序（添加时有些tileid是空值，会按类型自动分配id）
里面有一项 _render_layer，该项是与索引值一致的（world.lua - 143）

-- 代码中地皮名与地皮编号的对应关系 {TILE_REAL_NAME: TILE_CODE}
io.open("world_tiles.json", "w"):write(json.encode(WORLD_TILES))
-- 代码中地皮名组成的列表，索引即为编号 [TILE_REAL_NAME1, TILE_REAL_NAME2] 很长，因为给所有地皮留了位置，共 65535
io.open("inverted_world_tiles.json", "w"):write(json.encode(INVERTED_WORLD_TILES))
-- 地皮的名称，索引即为编号 [TILE_NAME1, TILE_NAME2]
io.open("ground_names.json", "w"):write(json.encode(GROUND_NAMES))
"""
# 按优先级排列的包含地皮信息的列表，这部分才是真正的地皮，上面的所有的实际包含一些效果和其他的
ground_properties = loads(lua.eval('encode(require("worldtiledefs").ground)'))

# 按优先级排列的地皮编号的列表
tiles = [i[0] for i in ground_properties]
print(tiles)

# 地皮编号为键，优先级为值的字典
priority_id = {j: i + 1 for i, j in enumerate(tiles)}
_ = {
    202: 1,
    206: 2,
    201: 3,
    208: 4,
    205: 5,
    203: 6,
    204: 7,
    207: 8,
    38: 9,
    41: 10,
    36: 11,
    37: 12,
    35: 13,
    2: 14,
    42: 15,
    256: 16,
    44: 17,
    8: 18,
    3: 19,
    5: 20,
    7: 21,
    6: 22,
    4: 23,
    30: 24,
    31: 25,
    13: 26,
    14: 27,
    24: 28,
    25: 29,
    46: 30,
    15: 31,
    16: 32,
    17: 33,
    45: 34,
    19: 35,
    18: 36,
    21: 37,
    20: 38,
    23: 39,
    22: 40,
    43: 41,
    257: 42,
    32: 43,
    10: 44,
    12: 45,
    258: 46,
    259: 47,
    260: 48,
    261: 49,
    11: 50,
    39: 51,
    47: 52,
    34: 53,
    33: 54
}

# 和上个相同，只是键由 id 换成了 code
all_id_code = {j: i for i, j in all_code_id.items()}
priority_code = {all_id_code[j]: i + 1 for i, j in enumerate(tiles)}
_ = {
    'OCEAN_COASTAL_SHORE': 1,
    'OCEAN_BRINEPOOL_SHORE': 2,
    'OCEAN_COASTAL': 3,
    'OCEAN_WATERLOG': 4,
    'OCEAN_BRINEPOOL': 5,
    'OCEAN_SWELL': 6,
    'OCEAN_ROUGH': 7,
    'OCEAN_HAZARDOUS': 8,
    'QUAGMIRE_GATEWAY': 9,
    'QUAGMIRE_CITYSTONE': 10,
    'QUAGMIRE_PARKFIELD': 11,
    'QUAGMIRE_PARKSTONE': 12,
    'QUAGMIRE_PEATFOREST': 13,
    'ROAD': 14,
    'PEBBLEBEACH': 15,
    'MONKEY_GROUND': 16,
    'SHELLBEACH': 17,
    'MARSH': 18,
    'ROCKY': 19,
    'SAVANNA': 20,
    'FOREST': 21,
    'GRASS': 22,
    'DIRT': 23,
    'DECIDUOUS': 24,
    'DESERT_DIRT': 25,
    'CAVE': 26,
    'FUNGUS': 27,
    'FUNGUSRED': 28,
    'FUNGUSGREEN': 29,
    'FUNGUSMOON': 30,
    'SINKHOLE': 31,
    'UNDERROCK': 32,
    'MUD': 33,
    'ARCHIVE': 34,
    'BRICK_GLOW': 35,
    'BRICK': 36,
    'TILES_GLOW': 37,
    'TILES': 38,
    'TRIM_GLOW': 39,
    'TRIM': 40,
    'METEOR': 41,
    'MONKEY_DOCK': 42,
    'SCALE': 43,
    'WOODFLOOR': 44,
    'CHECKER': 45,
    'MOSAIC_GREY': 46,
    'MOSAIC_RED': 47,
    'MOSAIC_BLUE': 48,
    'CARPET2': 49,
    'CARPET': 50,
    'QUAGMIRE_SOIL': 51,
    'FARMING_SOIL': 52,
    'LAVAARENA_TRIM': 53,
    'LAVAARENA_FLOOR': 54
}

# 将上个键值置换的字典
priority_id_code = {j: i for i, j in priority_code.items()}
_ = {
    1: 'OCEAN_COASTAL_SHORE',
    2: 'OCEAN_BRINEPOOL_SHORE',
    3: 'OCEAN_COASTAL',
    4: 'OCEAN_WATERLOG',
    5: 'OCEAN_BRINEPOOL',
    6: 'OCEAN_SWELL',
    7: 'OCEAN_ROUGH',
    8: 'OCEAN_HAZARDOUS',
    9: 'QUAGMIRE_GATEWAY',
    10: 'QUAGMIRE_CITYSTONE',
    11: 'QUAGMIRE_PARKFIELD',
    12: 'QUAGMIRE_PARKSTONE',
    13: 'QUAGMIRE_PEATFOREST',
    14: 'ROAD',
    15: 'PEBBLEBEACH',
    16: 'MONKEY_GROUND',
    17: 'SHELLBEACH',
    18: 'MARSH',
    19: 'ROCKY',
    20: 'SAVANNA',
    21: 'FOREST',
    22: 'GRASS',
    23: 'DIRT',
    24: 'DECIDUOUS',
    25: 'DESERT_DIRT',
    26: 'CAVE',
    27: 'FUNGUS',
    28: 'FUNGUSRED',
    29: 'FUNGUSGREEN',
    30: 'FUNGUSMOON',
    31: 'SINKHOLE',
    32: 'UNDERROCK',
    33: 'MUD',
    34: 'ARCHIVE',
    35: 'BRICK_GLOW',
    36: 'BRICK',
    37: 'TILES_GLOW',
    38: 'TILES',
    39: 'TRIM_GLOW',
    40: 'TRIM',
    41: 'METEOR',
    42: 'MONKEY_DOCK',
    43: 'SCALE',
    44: 'WOODFLOOR',
    45: 'CHECKER',
    46: 'MOSAIC_GREY',
    47: 'MOSAIC_RED',
    48: 'MOSAIC_BLUE',
    49: 'CARPET2',
    50: 'CARPET',
    51: 'QUAGMIRE_SOIL',
    52: 'FARMING_SOIL',
    53: 'LAVAARENA_TRIM',
    54: 'LAVAARENA_FLOOR'
}

"""
TURF_ROAD             = "Cobblestones",                   卵石路
TURF_ROCKY            = "Rocky Turf",                     岩石地皮
TURF_DIRT             = "Dirt Turf",                      泥土地皮
TURF_SAVANNA          = "Savanna Turf",                   热带草原地皮
TURF_GRASS            = "Grass Turf",                     长草地皮
TURF_FOREST           = "Forest Turf",                    森林地皮
TURF_MARSH            = "Marsh Turf",                     沼泽地皮
TURF_WOODFLOOR        = "Wooden Flooring",                木地板
TURF_CARPETFLOOR      = "Carpeted Flooring",              地毯地板
TURF_CHECKERFLOOR     = "Checkered Flooring",             棋盘地板
TURF_METEOR           = "Moon Crater Turf",               月球环形山地皮
TURF_SHELLBEACH       = "Shell Beach Turf",               贝壳海滩地皮
TURF_PEBBLEBEACH      = "Rocky Beach Turf",               岩石海滩地皮
TURF_DRAGONFLY        = "Scaled Flooring",                龙鳞地板

TURF_CAVE             = "Guano Turf",                     鸟粪地皮
TURF_FUNGUS           = "Fungal Turf",                    菌类地皮
TURF_FUNGUS_RED       = "Fungal Turf",                    菌类地皮
TURF_FUNGUS_GREEN     = "Fungal Turf",                    菌类地皮
TURF_FUNGUS_MOON      = "Mutated Fungal Turf",            变异菌类地皮

TURF_ARCHIVE          = "Ancient Stonework",              远古石刻

TURF_RUINSBRICK       = "Ancient Flooring",               远古地面
TURF_RUINSBRICK_GLOW  = "Imitation Ancient Flooring",     仿远古地面
TURF_RUINSTILES       = "Ancient Tilework",               远古瓷砖
TURF_RUINSTILES_GLOW  = "Imitation Ancient Tilework",     仿远古瓷砖
TURF_RUINSTRIM        = "Ancient Brickwork",              远古砖雕
TURF_RUINSTRIM_GLOW   = "Imitation Ancient Brickwork",    仿远古砖雕

TURF_SINKHOLE         = "Slimy Turf",                     黏滑地皮
TURF_UNDERROCK        = "Cave Rock Turf",                 洞穴岩石地皮
TURF_MUD              = "Mud Turf",                       泥泞地皮
TURF_DESERTDIRT       = "Sandy Turf",                     沙漠地皮
TURF_DECIDUOUS        = "Deciduous Turf",                 落叶林地皮
TURF_MONKEY_GROUND    = "Moon Quay Beach Turf",           月亮码头海滩地皮

TURF_CARPETFLOOR2     = "Lush Carpet",                    茂盛地毯
TURF_MOSAIC_GREY      = "Grey Mosaic Flooring",           灰色马赛克地面
TURF_MOSAIC_BLUE      = "Blue Mosaic Flooring",           蓝色马赛克地面
TURF_MOSAIC_RED       = "Red Mosaic Flooring",            红色马赛克地面

"""
# 有优先级的地皮的翻译与 code id 之间的对应关系，一部分是上面游戏本体的翻译，一部分是手动翻译，熔炉暴食的不知道咋翻译呀
code_trans = {
    "ROAD": '卵石路',
    "ROCKY": '岩石地皮',
    "DIRT": '泥土地皮',
    "SAVANNA": '热带草原地皮',
    "GRASS": '长草地皮',
    "FOREST": '森林地皮',
    "MARSH": '沼泽地皮',
    "WOODFLOOR": '木地板',
    "CARPET": '地毯地板',
    "CHECKER": '棋盘地板',
    "CAVE": '鸟粪地皮',
    "FUNGUS": '蓝色菌类地皮',
    "SINKHOLE": '黏滑地皮',
    "UNDERROCK": '洞穴岩石地皮',
    "MUD": '泥泞地皮',
    "BRICK": '远古地面',
    "BRICK_GLOW": '仿远古地面',
    "TILES": '远古瓷砖',
    "TILES_GLOW": '仿远古瓷砖',
    "TRIM": '远古砖雕',
    "TRIM_GLOW": '仿远古砖雕',
    "FUNGUSRED": '红色菌类地皮',
    "FUNGUSGREEN": '绿色菌类地皮',
    "DECIDUOUS": '落叶林地皮',
    "DESERT_DIRT": '沙漠地皮',
    "SCALE": '龙鳞地板',

    "LAVAARENA_FLOOR": "Forge Floor",
    "LAVAARENA_TRIM": "Forge Trim",
    "QUAGMIRE_PEATFOREST": "Gorge Peat Forest",
    "QUAGMIRE_PARKFIELD": "Gorge Park Grass",
    "QUAGMIRE_PARKSTONE": "Gorge Park Path",
    "QUAGMIRE_GATEWAY": "Gorge Gateway",
    "QUAGMIRE_SOIL": "Gorge Soil",
    "QUAGMIRE_CITYSTONE": "Gorge Citystone",

    "PEBBLEBEACH": '岩石海滩地皮',
    "METEOR": '月球环形山地皮',
    "SHELLBEACH": '贝壳海滩地皮',
    "ARCHIVE": '远古石刻',
    "FUNGUSMOON": '变异菌类地皮',
    "FARMING_SOIL": '耕地',
    "OCEAN_COASTAL": '浅海',
    "OCEAN_COASTAL_SHORE": '海滨',
    "OCEAN_SWELL": '中海',
    "OCEAN_ROUGH": '深海',
    "OCEAN_BRINEPOOL": '盐堆海域',
    "OCEAN_BRINEPOOL_SHORE": '盐堆海滨',
    "OCEAN_HAZARDOUS": '危险海域',
    "OCEAN_WATERLOG": '水中木海域',
    "MONKEY_GROUND": '月亮码头海滩地皮',
    "MONKEY_DOCK": '码头',
    "MOSAIC_GREY": '灰色马赛克地面',
    "MOSAIC_RED": '蓝色马赛克地面',
    "MOSAIC_BLUE": '红色马赛克地面',
    "CARPET2": '茂盛地毯',
}
id_trans = {
    2: '卵石路',
    3: '岩石地皮',
    4: '泥土地皮',
    5: '热带草原地皮',
    6: '长草地皮',
    7: '森林地皮',
    8: '沼泽地皮',
    10: '木地板',
    11: '地毯地板',
    12: '棋盘地板',
    13: '鸟粪地皮',
    14: '菌类地皮',
    15: '黏滑地皮',
    16: '洞穴岩石地皮',
    17: '泥泞地皮',
    18: '远古地面',
    19: '仿远古地面',
    20: '远古瓷砖',
    21: '仿远古瓷砖',
    22: '远古砖雕',
    23: '仿远古砖雕',
    24: '菌类地皮',
    25: '菌类地皮',
    30: '落叶林地皮',
    31: '沙漠地皮',
    32: '龙鳞地板',

    33: "Forge Floor",
    34: "Forge Trim",
    35: "Gorge Peat Forest",
    36: "Gorge Park Grass",
    37: "Gorge Park Path",
    38: "Gorge Gateway",
    39: "Gorge Soil",
    41: "Gorge Citystone",

    42: '岩石海滩地皮',
    43: '月球环形山地皮',
    44: '贝壳海滩地皮',
    45: '远古石刻',
    46: '变异菌类地皮',
    47: '耕地',
    201: '浅海',
    202: '浅海海岸',
    203: '中海',
    204: '深海',
    205: '盐堆海域',
    206: '盐堆海岸',
    207: '危险海域',
    208: '水中木海域',
    256: '月亮码头海滩地皮',
    257: '码头',
    258: '灰色马赛克地面',
    259: '蓝色马赛克地面',
    260: '红色马赛克地面',
    261: '茂盛地毯',
}

code_id_named = {
    "ROAD": 2,
    "ROCKY": 3,
    "DIRT": 4,
    "SAVANNA": 5,
    "GRASS": 6,
    "FOREST": 7,
    "MARSH": 8,
    "WOODFLOOR": 10,
    "CARPET": 11,
    "CHECKER": 12,
    "CAVE": 13,
    "FUNGUS": 14,
    "SINKHOLE": 15,
    "UNDERROCK": 16,
    "MUD": 17,
    "BRICK": 18,
    "BRICK_GLOW": 19,
    "TILES": 20,
    "TILES_GLOW": 21,
    "TRIM": 22,
    "TRIM_GLOW": 23,
    "FUNGUSRED": 24,
    "FUNGUSGREEN": 25,
    "DECIDUOUS": 30,
    "DESERT_DIRT": 31,
    "SCALE": 32,

    "LAVAARENA_FLOOR": 33,
    "LAVAARENA_TRIM": 34,
    "QUAGMIRE_PEATFOREST": 35,
    "QUAGMIRE_PARKFIELD": 36,
    "QUAGMIRE_PARKSTONE": 37,
    "QUAGMIRE_GATEWAY": 38,
    "QUAGMIRE_SOIL": 39,
    "QUAGMIRE_CITYSTONE": 41,

    "PEBBLEBEACH": 42,
    "METEOR": 43,
    "SHELLBEACH": 44,
    "ARCHIVE": 45,
    "FUNGUSMOON": 46,
    "FARMING_SOIL": 47,
    "OCEAN_COASTAL": 201,
    "OCEAN_COASTAL_SHORE": 202,
    "OCEAN_SWELL": 203,
    "OCEAN_ROUGH": 204,
    "OCEAN_BRINEPOOL": 205,
    "OCEAN_BRINEPOOL_SHORE": 206,
    "OCEAN_HAZARDOUS": 207,
    "OCEAN_WATERLOG": 208,
    "MONKEY_GROUND": 256,
    "MONKEY_DOCK": 257,
    "MOSAIC_GREY": 258,
    "MOSAIC_RED": 259,
    "MOSAIC_BLUE": 260,
    "CARPET2": 261,
}
