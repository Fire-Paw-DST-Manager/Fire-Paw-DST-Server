# -*- coding: utf-8 -*-
import sys
from typing import Union
from pathlib import Path
from cluster.settings import ClusterSetting, ShardSetting


def cluster():
    xx = ClusterSetting()

    print('默认存档数据：\n', xx.model_dump())
    from configparser import ConfigParser

    c = ConfigParser()

    c.read_dict(xx.model_dump())

    from io import StringIO
    s = StringIO()
    c.write(s)
    s.seek(0)

    print('默认存档序列化后数据：\n', s.read())

    from utils.ini_reader import ClusterIniReader
    parser = ClusterIniReader()
    parser.read('../../test_src/MyDediServer/cluster.ini', encoding='utf-8')
    dd = parser.data
    print(dd)
    print(ClusterSetting(**dd).model_dump())


def shard():
    xx = ShardSetting()
    print('默认分片数据：\n', xx.model_dump())

    from utils.ini_reader import ClusterIniReader
    parser = ClusterIniReader()
    parser.read('../../test_src/MyDediServer/Master/server.ini', encoding='utf-8')
    dd = parser.data
    print(dd)
    print(ShardSetting(**dd).model_dump())


if __name__ == '__main__':
    cluster()
    shard()


