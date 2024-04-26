# -*- coding: utf-8 -*-
import logging as log
import xml.etree.ElementTree as et
from collections import deque
from io import BytesIO
from random import shuffle
from typing import Union

log.basicConfig(format='%(asctime)s | %(levelname)-8s | %(lineno)4d %(funcName)-10s | - %(message)s',
                datefmt='%y-%m-%d %H:%M:%S',
                level=log.DEBUG)


class Svg:
    # 仅包含所需的svg属性
    _attr_svg = {
        'x': '0',
        'y': '0',
        'width': '100',
        'height': '100',
        # 'version': '1.1',
        # 'baseProfile': 'full',
        'xmlns': 'http://www.w3.org/2000/svg',
        # 'xmlns:xlink': 'http://www.w3.org/1999/xlink',
        # 'pointer-events': 'none',  # 屏蔽鼠标事件，避免卡顿
        # 'buffered-rendering': 'static',  # 缓存渲染的图像，避免卡顿
        'shape-rendering': 'crispEdges',  # 质量优先，防止边缘渲染不对齐出现白线
        'fill-rule': 'evenodd',
    }
    # buffered-rendering: static contain: paint
    # requestAnimationFrame https://blog.csdn.net/a843334549/article/details/123296950

    _declaration = '<?xml version="1.0" encoding="UTF-8" ?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'

    def __init__(self, ele=None, **kwargs) -> None:
        if not ele:
            self._attr_svg.update({i: str(j) for i, j in kwargs.items()})
            self._attr_svg['viewBox'] = f'0 0 {self._attr_svg["width"]} {self._attr_svg["height"]}'
            self.root = self._create_svg()
            self._svg = et.ElementTree(self.root)
        elif isinstance(ele, et.Element):
            self.root = ele
            self._svg = et.ElementTree(self.root)
        elif isinstance(ele, et.ElementTree):
            self.root = ele.getroot()
            self._svg = ele
        else:
            raise TypeError('传入参数[ele]类型需要是 et.ElementTree 或 et.Element')
        self.g = {}
        # self._create_css()

    def _create_svg(self) -> et.Element:
        return et.Element('svg', self._attr_svg)

    def _create_css(self, css_text) -> None:
        # 测试每个元素单独设置 fill 和通过 css 统一设置 fill，在缩放测试下实际耗时差别不大
        # 直接给 g 元素设置，不需要每个单独设置。效率未测试，直觉应该是比单独设置好的
        defs = et.SubElement(self.root, 'defs')
        style = et.SubElement(defs, 'style', {'type': 'text/css'})
        # css = ''.join([f'#g{key} path {{fill:{val}}}' for key, val in color.items()])
        style.append(self._create_cdata(css_text))

    @staticmethod
    def _create_cdata(content):
        content_cdata_comment = f'--><![CDATA[{content}]]><!--'
        return et.Comment(content_cdata_comment)

    def print(self) -> None:
        print(self._declaration, end='')
        et.dump(self.root)

    def save(self, save_path: str = 'export.svg', get_io=False) -> Union[None, BytesIO]:
        # etree 没有对DTD的支持，也不允许定义根元素之外的注释，只能保存时候自行处理
        # MDN 给出的创作指南[https://jwatt.org/svg/authoring/]说最好不要加 DTD，编辑时间段是 2005~2007
        # 但是w3c的在线检测[https://validator.w3.org/]会检测这个，如果没有会被判定为 xml，暂时保持添加
        svgio = BytesIO()
        svgio.write(self._declaration.encode('utf-8'))
        self._svg.write(svgio, encoding='utf-8', xml_declaration=False)
        svgio.seek(0)
        if get_io:
            return svgio

        if not save_path.endswith('.svg'):
            save_path += '.svg'
        with open(save_path, 'wb') as svgf:
            svgf.write(svgio.read())
        svgio.close()

    def creat_group(self, **kwargs) -> et.Element:
        if 'id' not in kwargs:
            for index in range(99999):
                g_id = f'g_{index}'
                if g_id not in self.g:
                    kwargs['id'] = g_id
        self.g[kwargs['id']] = et.SubElement(self.root, 'g', kwargs)
        return self.g[kwargs['id']]


class Path:
    """绘制图像的边缘
    e.g. self.load_map
        input ([
                [1, 0, 0],
                [0, 0, 0],
                [0, 0, 1]
                ])
        output
            3,
            3,
            {
                0: [
                    [(1, 0), (3, 0), (3, 2), (2, 2), (2, 3), (0, 3), (0, 1), (1, 1)]
                ],
                1: [
                    [(0, 0), (1, 0), (1, 1), (0, 1)],
                    [(2, 2), (3, 2), (3, 3), (2, 3)]
                ],
            }
        *     *     *     *     |     *     *     *     *
                                |        1     0  -  0
        *     *           *     |     *     *  |     |  *
                                |        0  -  0  -  0
        *           *     *     |     *  |     |  *     *
                                |        0  -  0     1
        *     *     *     *     |     *     *     *     *
    """

    def __init__(self):
        self.width: int = 0
        self.height: int = 0

        # 对于一个二维数组，如果子元素中保存的是一行的数据，认为是正常图，一列的数据则认为是翻转 x, y 轴的图，默认处理正常方向的图
        self.flipped: bool = False

        self.map_data: list[list[int]] = []

        self.edges: dict[int, list[list[tuple[int, int]]]] = {}

        self.paths: dict[int, list[str]] = {}

    def load_map(self, map_data: list[list[int]], is_flipped: bool = False) -> tuple[int, int, dict[int, list[list[tuple[int, int]]]]]:

        if not map_data or not map_data[0]:
            return 0, 0, {}

        if isinstance(map_data[0], int):
            self.map_data = map_data.copy()
        else:
            self.map_data = [[j for j in i] for i in map_data]

        if self.flipped != is_flipped:
            self._flip_map()

        if self.map_data:
            self.width = len(self.map_data[0])
            self.height = len(self.map_data)
        else:
            self.width = 0
            self.height = 0

        for ele_id, single_info in self._link_point().items():
            self.edges[ele_id] = [self._attach(self._classify(rount)) for rount in single_info]

        return self.width, self.height, self.edges

    def _flip_map(self):
        # 翻转 x, y 轴
        self.map_data = [list(i) for i in zip(*self.map_data)]

    def _link_point(self) -> dict[int, list[dict[tuple[int, int], set[tuple[int, int]]]]]:
        """分析传入地图信息，返回每种id的每块独立区域的边缘上的点与它们的出边
        默认处理正常图，若要处理反转图，可以通过翻转输入
        或调换函数内关于 self.map_data, map_data_padding, visited 的 x, y 值与 self.width, self.height
        e.g.
            self.map_data = [[0, 1],
                             [1, 0]]

                           |列表中每个字典代表一块独立区域|
                    {编号: [{顶点坐标: {出边向量, }, }, ], }  # 终点坐标 = 顶点坐标 + 出边向量   存图方式类似邻接表
            output: dict[int, list[dict[tuple[int, int], set[tuple[int, int]]]]] = {
            0: [
                {(0, 0): {(1, 0)}, (1, 0): {(0, 1)}, (1, 1): {(-1, 0)}, (0, 1): {(0, -1)}},  # 左上角的 0，没有与其它 0 相连，所以单独输出
                {(1, 1): {(1, 0)}, (2, 1): {(0, 1)}, (2, 2): {(-1, 0)}, (1, 2): {(0, -1)}}   # 右下角的 0，没有与其它 0 相连，所以单独输出
                ],
            1: [
                {(0, 1): {(1, 0)}, (1, 1): {(0, 1)}, (1, 2): {(-1, 0)}, (0, 2): {(0, -1)}},  # 左下角的 1，没有与其它 1 相连，所以单独输出
                {(1, 0): {(1, 0)}, (2, 0): {(0, 1)}, (2, 1): {(-1, 0)}, (1, 1): {(0, -1)}}   # 右上角的 1，没有与其它 1 相连，所以单独输出
                ]
            }


        创建 map_data_padding，在 self.map_data 的基础上，每行每列都在末尾添加 None，这样不需要判断下标是否越界(-1, max + 1)
        根据 map_data_padding 的大小创建 visited，并将额外添加的元素的位置设置为 True，用于记录哪些元素已经被访问过，避免重复访问
        遍历二维数组，出现未访问过的元素时，说明有一个未记录的区域，
            以该元素位置为起点，使用扫描线种子填充算法，寻找与当前元素连通的所有同类型元素，
            并根据相对位置，将其边缘添加到同一个字典中，
            遍历完毕时，所有区域应该都已记录
        """

        # 以左上角为原点为元素顶点建立坐标系
        # 每个地皮元素 顶点 自其自身左上角顺时针排序为 (0, 0), (1, 0), (1, 1), (0, 1)
        # 每条地皮元素 边缘 自其自身左上角顺时针排序为（不分方向） [(0, 0), (1, 0)], [(1, 0), (1, 1)], [(1, 1), (0, 1)], [(0, 1), (0, 0)]
        vector_right = (1, 0)
        vector_up = (0, -1)
        vector_left = (-1, 0)
        vector_down = (0, 1)

        #           |列表中每个字典代表一块独立区域|
        # {地皮编号: [{顶点坐标: {出边向量, }, }, ], }
        all_tile_info: dict[int, list[dict[tuple[int, int], set[tuple[int, int]]]]] = {}

        queue = deque()

        # 令下标(-1)与(w+1)/(h+1)可被正常访问，并返回一个不会与地皮相同的值。
        # 与visited一起使用，免去判断是否下标越界，提高效率 可以省去接近 w * h * 4 * 4 次比较运算
        map_data_padding = [*[i + [None] for i in self.map_data], [None] * (self.width + 1)]

        # 初始值设为 False。额外添加的值设为 True，避免检查
        visited = [*[[False] * self.width + [True] for _ in range(self.height)], [True] * (self.width + 1)]

        # ehx, ehy -> element_header_x, element_header_y
        for ehy, col in enumerate(self.map_data):
            for ehx, tile_code in enumerate(col):

                if visited[ehy][ehx]:
                    continue

                queue.append((ehx, ehy))
                visited[ehy][ehx] = True

                if tile_code not in all_tile_info:
                    all_tile_info[tile_code] = []

                all_tile_info[tile_code].append(single_tile_info := {})

                # ex, ey -> element_x, element_y
                while queue:
                    # 两种需要添加边缘的情况
                    # 1 当前行的最左端与最右端，对应的左右边缘
                    # 2 遍历上下行时，地皮不同，对应的上下边缘

                    ex, ey = queue.pop()

                    right, left, now = 0, 0, ex

                    while True:
                        # 向右寻找
                        now += 1

                        if map_data_padding[ey][now] != tile_code:
                            # 撞墙，结束
                            right = now - 1

                            # 添加右边缘，从元素的右上角向下到右下
                            # current_point = right, ey
                            start_vertex = right + 1, ey
                            if start_vertex not in single_tile_info:
                                single_tile_info[start_vertex] = set()
                            single_tile_info[start_vertex].add(vector_down)
                            break

                        # 是相同类型元素，继续走
                        visited[ey][now] = True

                    # 重置 now 的位置
                    now = ex

                    while True:
                        # 向左寻找
                        now -= 1

                        if map_data_padding[ey][now] != tile_code:
                            # 撞墙， 结束
                            left = now + 1

                            # 添加左边缘，从元素的左下向上到左上
                            # current = left, ey
                            start_vertex = left, ey + 1
                            if start_vertex not in single_tile_info:
                                single_tile_info[start_vertex] = set()
                            single_tile_info[start_vertex].add(vector_up)
                            break

                        # 是相同类型元素，继续走
                        visited[ey][now] = True

                    # 同行遍历完毕，开始遍历上下行
                    pre_col = (ey - 1, map_data_padding[ey - 1], (0, 0), vector_right)
                    after_col = (ey + 1, map_data_padding[ey + 1], (1, 1), vector_left)
                    for next_col_index, next_col_data, offset_element, direction_row_ in (pre_col, after_col):

                        # 标记该元素是否是最右侧相同类型元素，初始为 True，添加元素入队列后设置为 False，遇到其他类型元素时，设置为 True
                        flag = True

                        for next_element_x in range(right, left - 1, -1):
                            # 从右至左遍历
                            if next_col_data[next_element_x] == tile_code:
                                # 该点是相同类型地皮

                                if visited[next_col_index][next_element_x]:
                                    # 该点已经处理过，跳过
                                    continue

                                if flag:
                                    # 该元素是主行的最左、最右或该点左侧是其它类型地皮，添加到队列中
                                    queue.append((next_element_x, next_col_index))
                                    visited[next_col_index][next_element_x] = True

                                    # 标记一下，在遇到不同类型地皮之前，不再将点加入队列
                                    flag = False
                                continue

                            # 该点不是相同类型地皮，标记一下，下次遇到相同类型时，应加入队列
                            if not flag:
                                flag = True

                            # 地皮类型不同，说明此处应有边缘
                            # current = next_element_x, ey
                            start_vertex = next_element_x + offset_element[0], ey + offset_element[1]
                            # add_edge(start_vertex, direction_row_, single_tile_info)
                            if start_vertex not in single_tile_info:
                                single_tile_info[start_vertex] = set()
                            single_tile_info[start_vertex].add(direction_row_)

        return all_tile_info

    def _link_point_old(self) -> dict[int, list[dict[tuple[int, int], set[tuple[int, int]]]]]:
        """分析传入地图信息，返回每种id的每块独立区域的边缘上的点与它们的出边
        默认处理正常图，若要处理反转图，可以通过翻转输入
        或调换函数内关于 self.map_data, map_data_padding, visited 的 x, y 值与 self.width, self.height
        e.g.
            self.map_data = [[0, 1],
                             [1, 0]]

                           |列表中每个字典代表一块独立区域|
                    {编号: [{顶点坐标: {出边向量, }, }, ], }  # 终点坐标 = 顶点坐标 + 出边向量   存图方式类似邻接表
            output: dict[int, list[dict[tuple[int, int], set[tuple[int, int]]]]] = {
            0: [
                {(0, 0): {(1, 0)}, (1, 0): {(0, 1)}, (1, 1): {(-1, 0)}, (0, 1): {(0, -1)}},  # 左上角的 0，没有与其它 0 相连，所以单独输出
                {(1, 1): {(1, 0)}, (2, 1): {(0, 1)}, (2, 2): {(-1, 0)}, (1, 2): {(0, -1)}}   # 右下角的 0，没有与其它 0 相连，所以单独输出
                ],
            1: [
                {(0, 1): {(1, 0)}, (1, 1): {(0, 1)}, (1, 2): {(-1, 0)}, (0, 2): {(0, -1)}},  # 左下角的 1，没有与其它 1 相连，所以单独输出
                {(1, 0): {(1, 0)}, (2, 0): {(0, 1)}, (2, 1): {(-1, 0)}, (1, 1): {(0, -1)}}   # 右上角的 1，没有与其它 1 相连，所以单独输出
                ]
            }
        """

        # 以左上角为原点为元素顶点建立坐标系
        # 每个地皮元素 顶点 自其自身左上角顺时针排序为 (0, 0), (1, 0), (1, 1), (0, 1)
        # 每条地皮元素 边缘 自其自身左上角顺时针排序为（不分方向） [(0, 0), (1, 0)], [(1, 0), (1, 1)], [(1, 1), (0, 1)], [(0, 1), (0, 0)]
        # 根据邻接元素的位置，先列出对应关系  出现环形图案时，内外连线方向一致会有问题，可以处理，但不必要，svg 的 fill-rule evenodd 可以解决
        # 邻接元素的偏移量
        right = (1, 0)
        left = (-1, 0)
        up = (0, -1)
        down = (0, 1)
        sides = (up, right, down, left)
        sides_edge = {
            # 切换坐标系时的偏移量 以该点为起点的连线
            up: ((0, 0), (1, 0)),
            right: ((1, 0), (0, 1)),
            down: ((1, 1), (-1, 0)),
            left: ((0, 1), (0, -1)),
        }
        # 上面只检查四向的元素，所以仅斜向相接的两块地皮不会被划分到同一个独立区域中，检查八向可以将它们划分在一个区域
        # 但是循环次数要多一倍，不是很值得
        # other_sides = (
        #     (1, -1),  # right up
        #     (1, 1),  # right down
        #     (-1, -1),  # left up
        #     (-1, 1),  # left down
        # )

        #           |列表中每个字典代表一块独立区域|
        # {地皮编号: [{顶点坐标: {出边向量, }, }, ], }
        all_tile_info: dict[int, list[dict[tuple[int, int], set[tuple[int, int]]]]] = {}

        queue = deque()

        # 令下标(-1)与(w+1)/(h+1)可被正常访问，并返回一个不会与地皮相同的值。
        # 与visited一起使用，免去判断是否下标越界，提高效率 可以省去接近 w * h * 4 * 4 次比较运算
        map_data_padding = [*[i + [None] for i in self.map_data], [None] * (self.width + 1)]

        # 初始值设为 False。额外添加的值设为 True，避免检查
        visited = [*[[False] * self.width + [True] for _ in range(self.height)], [True] * (self.width + 1)]

        # ehx, ehy -> element_header_x, element_header_y
        # for ehx, col in enumerate(self.map_data):
        for ehy, col in enumerate(self.map_data):
            # for ehy, tile_code in enumerate(col):
            for ehx, tile_code in enumerate(col):

                # if visited[ehx][ehy]:
                if visited[ehy][ehx]:
                    continue

                # print(f'out add {(ex, ey)} {tile_code=}')

                queue.append((ehx, ehy))
                # visited[ehx][ehy] = True
                visited[ehy][ehx] = True

                if tile_code not in all_tile_info:
                    all_tile_info[tile_code] = []

                all_tile_info[tile_code].append(single_tile_info := {})

                # ex, ey -> element_x, element_y
                while queue:
                    ex, ey = queue.pop()
                    # print(f'check {(px, py)}')

                    # 判断四个方向上是否需要添加边缘与检查
                    # eox, eoy -> element_offset_x, element_offset_y  邻接元素的偏移量
                    # nx, ny   -> neighbor_x, neighbor_y              邻接元素坐标
                    for eox, eoy in sides:
                        nx, ny = ex + eox, ey + eoy

                        # 邻接元素有 3 种情况，超出地图、与目标相同、与目标不同，1、3 需要添加边缘，2 需要检查邻接元素
                        # 添加了额外的数据使 1、3 具有相同的判断条件
                        # if map_data_padding[nx][ny] == tile_code:
                        if map_data_padding[ny][nx] == tile_code:
                            # if visited[nx][ny]:
                            if visited[ny][nx]:
                                continue

                            # print(f'in add {(nx, ny)} {tile_code=}')
                            queue.append((nx, ny))
                            # visited[nx][ny] = True
                            visited[ny][nx] = True
                            continue

                        # 情况 2
                        # vox, voy -> vertex_offset_x, vertex_offset_y    元素坐标转换顶点坐标的偏移量
                        (vox, voy), direction_vector = sides_edge[(eox, eoy)]

                        # 根据 offset 在对应位置添加边缘
                        start = ex + vox, ey + voy

                        if start not in single_tile_info:
                            single_tile_info[start] = set()

                        single_tile_info[start].add(direction_vector)

        return all_tile_info

    @staticmethod
    def _attach(rounts: list[list[tuple[int, int]]]) -> list[tuple[int, int]]:
        """独立区域可能包含多条边缘，比如环形区域有内边缘与外边缘
        将这些边缘合并为一条
        做法是 随机选一条作为主路径，将其封闭，再将其它路径添加在后面，然后回到主路径起点，继续连接下一条路径"""
        main_rount = max(rounts, key=lambda _: len(_))
        for rount in rounts:
            if rount is main_rount:
                continue
            mx, my = main_access = main_rount[0]
            access_index = 0
            for i, (px, py) in enumerate(rount):
                # 保证连线不是水平或竖直，一般情况无意义，是为了处理成 svg 路径时方便判断使用 M 命令，避免出现连线
                if mx != px and my != py:
                    access_index = i
                    break
            # [main_start, main_..., main_end] + /
            # [main_start, *rount[access_index:], *rount[:access_index], rount[access_index], main_start]
            if main_access != main_rount[-1]:
                main_rount.append(main_access)
            main_rount.extend(rount[access_index:])
            main_rount.extend(rount[:access_index + 1])
            # main_rount.append(main_access)

        return main_rount

    @staticmethod
    def _classify(links: dict[tuple[int, int], set[tuple[int, int]]]) -> list[list[tuple[int, int]]]:
        """通过传入的图的数据，将其中的通路连接起来并返回"""
        rounts = []

        def choose_start():
            # 选择某条连线的某个端点作为startpoint
            # 入度：以该顶点为终点的连线的数量；出度：以该顶点为起点的连线的数量
            # 点共有三种情况
            #   1 在连线中间，入度为 1，出度为 1，两条连线同向；
            #   2 在连线一端，入度为 1，出度为 1，两条连线反向；
            #   3 在连线一端，入度为 2，出度为 2，入的两条连线反向，出的两条连线反向。
            #                    ↑           ↑
            # eg: 1. → * →    2. * ←    3. → * ←
            #                                ↓
            # 所以 出度为 2 时，是 3；出度为 1 时，根据出入的连线方向确定是 1 或 2
            # 2 满足要求的点，返回
            # 1, 3 在出的连线中选择一条继续走，直到到达 2 的状态
            start_x, start_y = next(iter(links))
            current_direction = None

            # 寻找当前点的入边方向
            for direction_x, direction_y in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                pre_point = start_x + direction_x, start_y + direction_y

                if pre_point not in links:
                    continue

                pre_direction = -direction_x, -direction_y
                if pre_direction in links[pre_point]:
                    current_direction = pre_direction
                    break

            while True:
                next_directions = links[(start_x, start_y)]

                next_direction = next_directions.copy().pop()
                match len(next_directions):
                    case 1:
                        if next_direction == current_direction:
                            # 情况1
                            start_x, start_y = start_x + next_direction[0], start_y + next_direction[1]
                            continue
                        # 情况 2
                        return start_x, start_y
                    case 2:
                        # 情况 3
                        start_x, start_y = start_x + next_direction[0], start_y + next_direction[1]
                        current_direction = next_direction
                    case _:
                        raise

        while links:
            start = choose_start()

            rounts.append(rount := [start])

            next_point = start

            while True:
                # print(f'{next_point=} {start=}')
                current = next_point

                direction = links[current].pop()
                if not links[current]:
                    links.pop(current)

                next_point = current[0] + direction[0], current[1] + direction[1]

                if next_point == start:
                    break

                if next_point not in links:
                    raise ValueError(f'连线不能形成回路，{next_point=}, {links=}')

                if direction not in links[next_point]:
                    rount.append(next_point)
        return rounts

    def convert_path(self) -> dict[int, list[str]]:
        """将路径转为 svg 的 path 元素的 d 属性值，出现嵌套时需搭配 fill-rule evenodd 正确显示"""
        for ele_id, single_edges in self.edges.items():
            self.paths[ele_id] = (single_paths := [])
            for edge in single_edges:
                path = []
                edge_iter = iter(edge)
                # s -> start
                sx, sy = edge_iter.__next__()
                path.append(f'M{sx} {sy}')
                for x, y in edge_iter:
                    if sx == x:
                        command, offset, sy = 'v', y - sy, y
                    elif sy == y:
                        command, offset, sx = 'h', x - sx, x
                    else:
                        command, offset = 'M', f'{x} {y}'
                        sx, sy = x, y
                        # print('注意：两点不在同行或同列')
                    path.append(f'{command}{offset}')
                path.append(f'Z')
                single_paths.append(''.join(path))

        return self.paths


class Map:
    svg_colors = [
        "aliceblue",
        "antiquewhite",
        "aqua",
        "aquamarine",
        "azure",
        "beige",
        "bisque",
        # "black",  # 背景专用
        "blanchedalmond",
        "blue",
        "blueviolet",
        "brown",
        "burlywood",
        "cadetblue",
        "chartreuse",
        "chocolate",
        "coral",
        "cornflowerblue",
        "cornsilk",
        "crimson",
        "cyan",
        "darkblue",
        "darkcyan",
        "darkgoldenrod",
        "darkgray",
        "darkgreen",
        "darkgrey",
        "darkkhaki",
        "darkmagenta",
        "darkolivegreen",
        "darkorange",
        "darkorchid",
        "darkred",
        "darksalmon",
        "darkseagreen",
        "darkslateblue",
        "darkslategray",
        "darkslategrey",
        "darkturquoise",
        "darkviolet",
        "deeppink",
        "deepskyblue",
        "dimgray",
        "dimgrey",
        "dodgerblue",
        "firebrick",
        "floralwhite",
        "forestgreen",
        "fuchsia",
        "gainsboro",
        "ghostwhite",
        "gold",
        "goldenrod",
        "gray",
        "grey",
        "green",
        "greenyellow",
        "honeydew",
        "hotpink",
        "indianred",
        "indigo",
        "ivory",
        "khaki",
        "lavender",
        "lavenderblush",
        "lawngreen",
        "lemonchiffon",
        "lightblue",
        "lightcoral",
        "lightcyan",
        "lightgoldenrodyellow",
        "lightgray",
        "lightgreen",
        "lightgrey",
        "lightpink",
        "lightsalmon",
        "lightseagreen",
        "lightskyblue",
        "lightslategray",
        "lightslategrey",
        "lightsteelblue",
        "lightyellow",
        "lime",
        "limegreen",
        "linen",
        "magenta",
        "maroon",
        "mediumaquamarine",
        "mediumblue",
        "mediumorchid",
        "mediumpurple",
        "mediumseagreen",
        "mediumslateblue",
        "mediumspringgreen",
        "mediumturquoise",
        "mediumvioletred",
        "midnightblue",
        "mintcream",
        "mistyrose",
        "moccasin",
        "navajowhite",
        "navy",
        "oldlace",
        "olive",
        "olivedrab",
        "orange",
        "orangered",
        "orchid",
        "palegoldenrod",
        "palegreen",
        "paleturquoise",
        "palevioletred",
        "papayawhip",
        "peachpuff",
        "peru",
        "pink",
        "plum",
        "powderblue",
        "purple",
        "red",
        "rosybrown",
        "royalblue",
        "saddlebrown",
        "salmon",
        "sandybrown",
        "seagreen",
        "seashell",
        "sienna",
        "silver",
        "skyblue",
        "slateblue",
        "slategray",
        "slategrey",
        "snow",
        "springgreen",
        "steelblue",
        "tan",
        "teal",
        "thistle",
        "tomato",
        "turquoise",
        "violet",
        "wheat",
        "white",
        "whitesmoke",
        "yellow",
        "yellowgreen",
    ]

    svg_attr_common = {
        'stroke-width': '0',
        'stroke-linejoin': "round",
        'stroke-linecap': "round",  # butt round square  无 圆角 方角
    }

    def __init__(self, map_data: list[Union[int, Union[list[int], tuple[int]]]], width: int = None, height: int = None,
                 is_flipped: bool = False):
        self.width: int = 0
        self.height: int = 0

        self.map_data: list[[list[int]]] = map_data

        self._format_data(width, height)

        if is_flipped:
            self.width, self.height = self.height, self.width

        path = Path()
        self.edges = path.load_map(self.map_data, is_flipped)
        self.paths = path.convert_path()

        self.svg: Svg = Svg(width=self.width, height=self.height, **self.svg_attr_common)
        self._g: dict[str, et.Element] = self.svg.g

        self.tile_names = self._get_tile_names()
        self.priority = self._get_priority()
        self.tile_colors = self._get_tile_colors()

    def _format_data(self, width: int = None, height: int = None) -> None:
        if not self.map_data:
            raise ValueError('传入地图数据为空')
        if isinstance(self.map_data[0], int):
            map_data_len = len(self.map_data)
            if width is None:
                if height is None:
                    width = height = int(map_data_len ** 0.5)
                    if width * height != map_data_len:
                        raise ValueError(
                            f'未传入宽高，且 map_data 表示的地图不是正方形 {width=} {height=} {map_data_len=}')
                else:
                    width = map_data_len // height
            if height is None:
                height = map_data_len // width
            if width * height != map_data_len:
                raise ValueError(f'宽高数据与 map_data 表示的地图不符 {width} x {height} != {len(self.map_data)}')
            self.width = width
            self.height = height
            self.map_data = [self.map_data[i * self.height: (i + 1) * self.height] for i in range(self.width)]
        elif isinstance(self.map_data[0], (list, tuple)):
            self.width = len(self.map_data[0])
            self.height = len(self.map_data)

            if (width or height) and (self.width != width or self.height != height):
                log.warning(f'传入宽高 {width=}, {height=} 与图数据不符，已更正为 width={self.width}, height={self.height}')
        else:
            raise TypeError('传入地图数据格式错误')

    def _get_tile_names(self) -> dict[int, str]:
        return {i: str(i) for i in list(self.paths)}

    def _get_priority(self) -> list[int]:
        # 根据地皮优先级列表，首先生成低优先级的，再生成高优先级的覆盖，用来实现不同优先级地皮间的覆盖效果
        return sorted(list(self.paths))

    def _get_tile_colors(self) -> dict[str, str]:
        tile_colors = {}
        colors = []
        for tile_code in self.paths:
            if not colors:
                colors = self.svg_colors.copy()
                shuffle(colors)
            tile_colors[str(tile_code)] = colors.pop()

        return tile_colors

    def save(self, save_path: str = 'map', get_io=False) -> Union[None, BytesIO]:
        for tile_code in self.priority:
            tile_name = self.tile_names[tile_code]
            g_id = f'g_{tile_name}'
            if tile_name not in self._g:
                color = self.tile_colors.get(tile_name)
                # 通过边框实现地皮优先级覆盖会导致图形合并时连接的线也有边框，连接时避免同行同列，通过 M 命令连接可以避免
                self.svg.creat_group(**{
                    'id': g_id,
                    'stroke': color,
                    # 'stroke-width': '0.25',  # 迁移到 svg 属性
                    # 'stroke-linecap': "round",  # 迁移到 svg 属性
                    # "stroke-linejoin": "round",  # 迁移到 svg 属性
                    'fill': color,
                })
            for path in self.paths[tile_code]:
                et.SubElement(self._g[g_id], 'path', {'d': path})

        # 中心点
        # cx, cy = (self.width - 1) / 2 + 1, (self.height - 1) / 2 + 1
        # et.SubElement(self.root, 'path', {'stroke': 'red', 'stroke-width': '2', 'd': f'M{cx} {cy}Z'})

        return self.svg.save(save_path, get_io)


"""
游戏内，地皮坐标轴正向是和地图坐标系一致的，在屏幕逆时针旋转 45° 后（即按一下q），向下是x(0, )的正向，向右是y(, 0)的正向
但保存的游戏数据是按列保存的，先第一列，再第二列以此类推，因此该处构造的坐标系轴方向是与游戏内对调的，x, y -> y, x
但该处构造的坐标系与 svg 坐标系轴方向是一致的，因此虽然 svg 中显示方向与游戏内一致，但其 x,y 值是互换的，不可以直接用

游戏内默认方向 两个坐标体系
1 以地皮排列为基础构建的坐标系，默认上方指向 地皮的零点(0, 0)。向上走 x,y 逐渐减小，最小为(0, 0)  425*425 x,y ∈[0,424]
425*425 游戏内显示实际长度是 426  除去(0~424)，(0, 0)后面还有一个(0, 0)，这一行一列的地皮也是impassable，426*426范围外则是invalid，invalid上创建新实体时游戏会崩溃  两个(0, 0)都越过之后，开始负值计数
2 以地图中心为原点构建的坐标系，默认上方指向 x, y 轴的负方向
按 q 将屏幕逆时针旋转 45° 后，左上为地皮原点(0, 0)，  地图中心右下方半个地皮为坐标原点，下方为 x 轴正向，右为 y 轴正向

下方地皮坐标默认以地皮左上角的坐标为原点，方便换算
坐标原点与地皮原点  425*425 坐标原点在 (212, 212)(213, 213) 两块地皮交接处，即 地皮(213, 213)    地皮(0, 0), (424, 424) 对应原点坐标(-852, -852) (844, 844)
400*400 坐标原点在 (200, 200) 地皮中心   地皮(0, 0), (399, 399) 对应坐标(-802, -802)(794, 794)
对于 size * size 的地图，地皮(0, 0) 的坐标是(-((size-1)/2+1)*4, -((size-1)/2+1)*4)
地皮(size-1, size-1) 的坐标是 (((size-1)/2 - 1)*4, ((size-1)/2 - 1)*4)
因为 size x size 大的地皮矩阵中，相邻边角的两块地皮间距是 size - 1，所以 (size - 1) - ((size-1)/2+1) = ((size-1)/2 - 1)

所以对于实体坐标，游戏内 x, y 坐标分别除以 4 并对调，加上 (size-1)/2+1，就是 svg 内实体坐标了
游戏 -> svg
(x, y) -> ( y / 4 + ((height-1)/2+1), x / 4 + ((width-1)/2+1) )
svg -> 游戏
(x, y) -> ( (y - (height-1)/2+1) * 4, (x - (width-1)/2+1) * 4 )
svg 中，地图中心坐标 ( (width-1)/2+1, (height-1)/2+1 )
游戏内地皮坐标中，地图中心坐标 ( (height-1)/2+1, (width-1)/2+1 )
"""
