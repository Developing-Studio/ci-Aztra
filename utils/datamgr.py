import aiomysql
from enum import Enum
from typing import List, Dict, Any, Callable
import json
from .basemgr import AzaleaData, AzaleaManager, AzaleaDBManager
from . import mgrerrors

class SettingType(Enum):
    select = 0

class Setting(AzaleaData):
    def __init__(self, name: str, title: str, description: str, type: Any, default: Any):
        self.name = name
        self.title = title
        self.description = description
        self.type = type
        self.default = default

class SettingData(AzaleaData):
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value

class Permission(AzaleaData):
    def __init__(self, value: int, name: str):
        self.value = value
        self.name = name

class PermissionsData(AzaleaData):
    def __init__(self, value: int):
        self.value = value

class DataDB:
    def __init__(self):
        self.permissions = []
        self.reloader = None

    def load_permissions(self, perms: List[Permission]):
        self.permissions = perms

    def set_reloader(self, callback: Callable):
        self.reloader = callback

    def set_loader(self, callback: Callable):
        self.loader = callback

    def reload(self):
        self.reloader(self)

class PermDBMgr(AzaleaDBManager):
    def __init__(self, datadb: DataDB):
        self.permissions = datadb.permissions

    def get_permission(self, name: str):
        perm = list(filter(lambda x: x.name == name, self.permissions))
        if perm:
            return perm[0]

    def get_permission_by_value(self, value: int):
        perm = list(filter(lambda x: x.value == value, self.permissions))
        if perm:
            return perm[0]

class SettingDBMgr(AzaleaDBManager):
    def __init__(self, datadb: DataDB, mode='char'):
        self.settings = datadb.char_settings

    def fetch_setting(self, name: str):
        sets = list(filter(lambda x: x.name == name, self.settings))
        if sets:
            return sets[0]

    def get_base_settings(self):
        base = {}
        for one in self.settings:
            base[one.name] = one.default
        return base

class SettingMgr(AzaleaManager):
    def __init__(self, pool: aiomysql.Pool, sdgr: SettingDBMgr, charuuid: str):
        self.pool = pool
        self.sdgr = sdgr
        self.charuuid = charuuid

    @classmethod
    def get_dict_from_settings(self, settings: List[SettingData]):
        setdict = {}
        for one in settings:
            setdict[one.name] = one.value
        return setdict

    @classmethod
    def get_settings_from_dict(self, settingdict: Dict):
        sets = []
        for key, value in settingdict.items():
            sets.append(SettingData(key, value))
        return sets

    async def _save_settings(self, settings: Dict):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                rst = await cur.execute('update chardata set settings=%s where uuid=%s', (json.dumps(settings, ensure_ascii=False), self.charuuid))
                return rst

    async def get_raw_settings(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute('select settings from chardata where uuid=%s', self.charuuid)
                fetch = await cur.fetchone()
                raw = json.loads(fetch['settings'])
                return raw

    async def get_setting(self, name: str) -> Any:
        raw = await self.get_raw_settings()
        sets = self.get_settings_from_dict(raw)
        rawset = self.get_dict_from_settings(sets)
        setting = list(filter(lambda x: x.name == name, sets))
        if setting:
            return setting[0].value
        setting = list(filter(lambda x: x.name == name, self.sdgr.settings))
        if setting:
            setadd = self.sdgr.fetch_setting(name)
            rawset[setadd.name] = setadd.default
            await self._save_settings(rawset)
            return setadd.default
        else:
            raise mgrerrors.SettingNotFound(name)

    async def edit_setting(self, name: str, value):
        rawset = await self.get_raw_settings()
        setting = list(filter(lambda x: x.name == name, self.sdgr.settings))
        if setting:
            setedit = self.sdgr.fetch_setting(name)
            rawset[setedit.name] = value
            await self._save_settings(rawset)
        else:
            raise mgrerrors.SettingNotFound(name)