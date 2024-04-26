# -*- coding: utf-8 -*-
"""
if datatype == 'nodeidtilemap':
    # map.topology     这里存的应该都是 node 相关的数据
    #             ids  存放nodeid，与nodeidtilemap共同指明各node的分布与范围
    #             flattenedPoints  存放的是，各个node的边界，连接后可得到voronoi图
    #             nodes  貌似是各个node的细节
    name_id_map = data['map'].get('topology', {}).get('ids', [])
    name_id_map = {j: i + 1 for i, j in enumerate(name_id_map)}
elif datatype == 'tiles':
    name_id_map = data['map'].get('world_tile_map')  # 地皮数量修改（22.06）之前的存档是没有该项的，且tiles与tiledata还没有分开
else:
    name_id_map = {}

"""
from .map import Map
from .tiles import Tiles
from .nodeidtilemap import NodeIdTileMap
