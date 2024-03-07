# -*- coding: utf-8 -*-
from utils.ini_reader.common import IniReader, ValueType


class ServerIniReader(IniReader):
    _VALUE_TYPES = {
        'STEAM':
            {
                'master_server_port': ValueType.int,
                'authentication_port': ValueType.int,
            },

        'SHARD':
            {
                'is_master': ValueType.bool,
                'name': ValueType.str,
                'id': ValueType.int,
                'bind_ip': ValueType.str,
                'master_ip': ValueType.str,
                'master_port': ValueType.str,
                'cluster_key': ValueType.str,
            },

        'ACCOUNT':
            {
                'encode_user_path': ValueType.bool,
            },

        'NETWORK':
            {
                'server_port': ValueType.int,
            },
    }
