# -*- coding: utf-8 -*-
from configparser import ConfigParser
from io import StringIO
from sys import stdout

from cluster.settings import ClusterSetting, ShardSetting
from utils.ini_reader import ClusterIniReader, ServerIniReader


def cluster():
    xx = ClusterSetting()

    print('默认存档数据：\n', xx.model_dump())

    c = ConfigParser()
    c.read_dict(xx.model_dump())
    print('默认存档序列化后数据：')
    c.write(stdout)

    parser = ClusterIniReader()
    parser.read('../../test_src/MyDediServer/cluster.ini', encoding='utf-8')
    dd = parser.data
    print(dd)
    print(ClusterSetting(**dd).model_dump())


def shard():
    xx = ShardSetting()
    print('默认分片数据：\n', xx.model_dump())

    c = ConfigParser()
    c.read_dict(xx.model_dump())
    print('默认分片序列化后数据：')
    c.write(stdout)

    parser = ServerIniReader()
    parser.read('../../test_src/MyDediServer/Master/server.ini', encoding='utf-8')
    dd = parser.data
    print(dd)
    print(ShardSetting(**dd))
    print(ShardSetting(**dd).model_dump())


if __name__ == '__main__':
    cluster()
    shard()


