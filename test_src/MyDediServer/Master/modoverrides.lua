return {
  --共11个mod，不开启的mod用“--”或“--[[]]”注释掉
--[[
  ["workshop-1984703361"]={--自动清理
    configuration_options={
      Auto_Clean_Boat=false,
      Auto_Clean_Item_time=5,
      Auto_Clean_Percent=10,
      UnBurnable_ON_OFF=false 
    },
    enabled=true 
  },
]]
  --["workshop-1582864428"]={ configuration_options={  }, enabled=true },--死亡不重置
  --["workshop-1887331613"]={ configuration_options={ lang="zh", notice_method=2 }, enabled=true },--熊孩警告。系统消息宣告
  ["workshop-2172032964"]={ configuration_options={ RequestAge=5 }, enabled=true },--下线掉落，5天白名单

--[[
  ["workshop-2371017612"]={--保险箱。不可破坏、造价困难
    configuration_options={
      display_on_open=true,
      set_idioma_donchest="lang_CHI",
      set_indestructible_chest="y",
      set_recipe_chest="3" 
    },
    enabled=true 
  },
]]

  ["workshop-1595631294"]={--智能小木牌
    configuration_options={
      BundleItems=false,
      ChangeSkin=true,
      Digornot=true,
      DragonflyChest=false,
      Icebox=false,
      SaltBox=false 
    },
    enabled=true 
  },

--[[
  ["workshop-2097358269"]={--成熟的箱子
    configuration_options={
      collect_items_dist0=2,
      collect_items_dist1=0,
      dragonflychest=0,
      icebox=1,
      is_collect_drop=1,
      is_collect_lootdropper=1,
      is_collect_open=1,
      is_collect_periodicspawner=1,
      is_collect_take=0,
      iscollectone=1,
      minisign_dist=0.1,
      saltbox=0,
      treasurechest=1,
      ["收集时机"]=false,
      ["收集种类限制"]=false,
      ["箱子种类"]=false,
      ["距离设置 (4 == 一块地皮)"]=false 
    },
    enabled=true 
  },
]]

  ["workshop-666155465"]={--showme
    configuration_options={
      chestB=-1,
      chestG=-1,
      chestR=-1,
      display_hp=-1,
      food_estimation=-1,
      food_order=0,
      food_style=2,
      lang="chs",
      show_food_units=-1,
      show_uses=-1 
    },
    enabled=true 
  },

--[[
  ["workshop-1916988643"]={--纯净辅助。花台还原和种子消失
    configuration_options={
      [""]=0,
      ATKSPEED=false,
      BAT=false,
      BEEQUEENGIFTWRAP=false,
      BEEQUEENHAT=false,
      BETTERFOSSIL=false,
      BIRD=false,
      BLOCKABLEPOOPING=false,
      BUNDLE=false,
      CHECKSKINOWNERSHIP=false,
      COOKPOT=false,
      CROWNFRAGMENT=false,
      CUSTOMFAILSTR=false,
      ENDTABLE=true,
      EQUIPMENT=false,
      FIREFLIES=false,
      FLOWER=false,
      GATHERMOONGLASS=false,
      GLOMMER=false,
      HALLOWEEN=false,
      HONORMOUND=false,
      LUNARCROWN=false,
      LUREPLANT=false,
      MHATS=false,
      NAMEABLE_WATCHES=false,
      NODARTWASTE=false,
      NOFORESTRESOURCEREGEN=false,
      NOGHOSTHOUNDED=false,
      NOOCEANTREESTRIKEDROP=false,
      PIGKINGMOONGLASS=false,
      POCKETRESKIN=false,
      PROPSIGN=false,
      RANDOMLIGHTS=false,
      SANDSTONE=false,
      SEED=true,
      SISTURN=false,
      SITEMOTE=false,
      SMARTUNWRAP=false,
      SUMMONMAGIC=false,
      TENTACLE=false,
      TURFARCHIVE=false 
    },
    enabled=true 
  },
]]
  
  --["workshop-2559637840"]={ configuration_options={  }, enabled=true } --隐藏管理员标志
}