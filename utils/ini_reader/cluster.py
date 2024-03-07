# -*- coding: utf-8 -*-

from utils.ini_reader.common import IniReader, ValueType


class ClusterIniReader(IniReader):
    _VALUE_TYPES = {

        'GAMEPLAY':
            {
                'game_mode': ValueType.str,
                'max_players': ValueType.int,
                'pvp': ValueType.bool,
                'pause_when_empty': ValueType.bool,
                'vote_enabled': ValueType.bool,
            },

        'NETWORK':
            {
                'cluster_name': ValueType.str,
                'cluster_description': ValueType.str,
                'cluster_password': ValueType.str,
                'cluster_language': ValueType.str,
                'autosaver_enabled': ValueType.bool,
                'idle_timeout': ValueType.int,
                'lan_only_cluster': ValueType.bool,
                'offline_cluster': ValueType.bool,
                'tick_rate': ValueType.int,
                'whitelist_slots': ValueType.int,
                'override_dns': ValueType.str,
                'MethodType.internet_broadcasting_enabled': ValueType.bool,
                'cluster_cloud_id': ValueType.int,
                'cached_ping_size': ValueType.int,
            },

        'MISC':
            {
                'console_enabled': ValueType.bool,
                'max_snapshots': ValueType.int,
                'use_alternate_gc': ValueType.bool,
                # 'debug_random_data': ,
                # 'encoded_user_cache': ,
            },

        'STEAM':
            {
                'steam_group_admins': ValueType.bool,
                'steam_group_id': ValueType.int,
                'steam_group_only': ValueType.bool,
            },

        'SHARD':
            {
                'shard_enabled': ValueType.bool,
                'bind_ip': ValueType.str,
                'master_ip': ValueType.str,
                'master_port': ValueType.int,
                'cluster_key': ValueType.str,
            },
    }
