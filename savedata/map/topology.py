# -*- coding: utf-8 -*-
from typing import Union, Literal

from pydantic import BaseModel

"""
scripts/maputil.lua
"""
"""
最大的是整张地图 map
地图中有许多地形 task
地形中有许多区块 room
区块包含主区块、背景区块，下面的 node 就是指这些区块
"""


class _Node(BaseModel):

    # 与该 node 接壤的 其它 node
    # {index: nodeid, ...}
    neighbours: dict[int, int] = None

    # Default = 0,		    -- Land can touch any other Default node in the task that is within range
    # Blank = 1,		    -- empty room with impassable ground
    # Background = 2,
    # Random = 3,
    # Blocker = 4,		    -- Adds 2 Blank nodes beside it
    # Room = 5,			    -- Land can only touch the room(s) it is connected to by the graph (adds impassable around its parameter with a single land bidge)
    # BackgroundRoom = 6,
    # SeparatedRoom = 7,	-- adds impassable around its entire parameter
    type: int

    # colour index
    c: int

    # klei 代码里说是 center，但是和 x, y 为什么不一样呢，有什么区别
    # debug 中传送玩家到某个 node 时，是使用的这个
    # {index: x, index: y}
    cent: dict[int, float]

    x: int
    y: int

    # 该 node 的端点，连接起来之后是该 node 的范围
    # {index: {index: x, index: y}}, ...}
    poly: dict[int, dict[int, int]]

    # 有效边
    # {index: flattenedEdges_id, ...}
    validedges: dict[int, int] = None

    # 覆盖的面积 单位是 墙距²
    area: int


class _Edge(BaseModel):

    # node1 id
    n1: int

    # node2 id
    n2: int

    # 颜色
    c: int


class _Colours(BaseModel):
    a: Union[int, float]
    r: Union[int, float]
    g: Union[int, float]
    b: Union[int, float]


class Topology(BaseModel):
    """
    注意：lua 中索引从 1 开始
    """

    # 索引为 边在 flattenedEdges 中的索引，可据此获取该边。值为 该边隶属的 node 的 id
    # 为 false 时，情况与 flattenedEdges 相同
    # {index: {index: x, index: y} or false, ...}
    edgeToNodes: dict[int, Union[dict[int, int], Literal[False]]] = None

    # 按顺序排列的 nodeid，可根据索引将 nodidtilemap 中的编号转为对应的 nodeid
    # {node_index: node_id, ...}
    ids: dict[int, str]

    # 只在 debug 代码中看到，正常可能没有用处
    # {index: _Colours, ...}
    colours: dict[int, _Colours]

    # 世界设置项的 预设名 如 "SURVIVAL"
    level_type: str

    # 和 ids 是对应的，对应 node 的 story_depth   还不知道用处  有的会多，不知道原因
    # {node_index: depth, ...}
    story_depths: dict[int, int]

    # 世界设置项
    overrides: dict[str, Union[str, bool]]

    # 遍历 nodes 中每个 node 的 poly 中的点组成的列表   重复点跳过
    # {index: {index: x, index: y}, ...}
    flattenedPoints: dict[int, dict[int, int]] = None

    # 索引为 nodeid
    # {node_index: _Node}
    nodes: dict[int, _Node]

    # 各 node 中心的连线
    # {index: _Edge}
    edges: dict[int, _Edge]

    # 遍历 nodes 中每个 node，将 poly 中相邻两点连线，最后一个点再连到第一个点，由这些连线组成的列表 重复边跳过
    # 将存的整数作为索引，在 flattenedPoints 中取点
    # 为 false 的为无效边，在 node.validedges 存有对应 node 的有效边
    # 无效边：不接壤两个 node、或忽略墙体与蜘蛛网的情况下，人物不能经寻路在两点行动
    # {edge_index: {index: flattenedPoints_start_index, index: flattenedPoints_end_index} or false, ...}
    flattenedEdges: dict[int, Union[dict[int, int], Literal[False]]] = None
