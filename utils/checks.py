import discord
from discord.ext import commands
import aiomysql
from . import errors, datamgr

class Checks:
    def __init__(self, pool: aiomysql.Pool, datadb: datamgr.DataDB):
        self.pool = pool
        self.datadb = datadb

    async def registered(self, ctx: commands.Context):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from userdata where id=%s', ctx.author.id) != 0:
                    return True
                raise errors.NotRegistered('가입되지 않은 사용자입니다: {}'.format(ctx.author.id))
    
    def is_registered(self):
        return commands.check(self.registered)

    async def _has_internal_perms(self, user: discord.User, **perms):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if not await cur.execute('select * from userdata where id=%s', user.id):
                    return []
                fetch = await cur.fetchone()
                value = fetch['perms']
                pdgr = datamgr.PermDBMgr(self.datadb)
                master = pdgr.get_permission('master').value
                if (value & master) == master:
                    return True
                missings = []
                for one in perms:
                    perm = pdgr.get_permission(one)
                    if perms[one]:
                        if (value & perm.value) == perm.value:
                            continue
                    else:
                        if (value & perm.value) != perm.value:
                            continue
                    missings.append(perm.name)
                    return missings

    async def is_master(self, user: discord.User):
        return bool(await self._has_internal_perms(user, master=True))

    def has_aztra_permissions(self, **perms: bool):
        async def predicate(ctx: commands.Context):
            missings = await self._has_internal_perms(ctx.author, **perms)
            if type(missings) is list:
                raise errors.MissingAztraPermissions(missings)
            return True
            
        return predicate

    async def notbot(self, ctx: commands.Context):
        if not ctx.author.bot:
            return True
        raise errors.SentByBotUser('봇 유저로부터 메시지를 받았습니다: {}'.format(ctx.author.id))

    def is_notbot(self):
        return commands.check(self.notbot)

    async def subcmd_valid(self, ctx: commands.Context, include_group_itself=False):
        if include_group_itself:
            pass
        elif ctx.invoked_subcommand is not None or ctx.subcommand_passed is None:
            return True
        raise errors.SubcommandNotFound

    async def on_inspection(self, ctx: commands.Context):
        if await self.is_master(ctx.author):
            return True
        else:
            raise errors.onInspection('점검 중에는 마스터 유저만 사용이 가능합니다')
