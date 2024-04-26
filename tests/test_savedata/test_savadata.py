# -*- coding: utf-8 -*-

from savedata import SaveData


from time import time
s = time()
a = SaveData('../../test_src/MyDediServer/Master/save/session/5524C083947B6187/0000000003')
print(time() - s)
print(a)

print(list(a.all_data))

print(list(a.map.model_dump()))
print(list(a.meta))
print(list(a.world_network))
print(len(a.ents))
print(list(a.mods))

print(a.super)
print(list(a.snapshot))

print(list(a.extra_data))

print(a.map.topology.model_dump().keys())
print(a.mods)
print()
print(a.map.topology)
