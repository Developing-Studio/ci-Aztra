import discord
from discord.ext import commands
import datetime
import asyncio
import typing
import aiomysql
from utils.basecog import BaseCog
from utils import pager, emojibuttons
import uuid

class Warncmds(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        for cmd in self.get_commands():
            cmd.add_check(commands.guild_only())

    @commands.command(name='경고')
    async def _warn(self, ctx: commands.Context, member: typing.Optional[discord.Member]=None, reason=None, count: int=1):
        if reason is None:
            await self._warn_list(ctx, member)
        else:
            await self._warn_give(ctx, member, reason, count)

    @commands.command(name='경고확인')
    async def _warn_list(self, ctx: commands.Context, member: typing.Optional[discord.Member]=None):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if not member:
                    member = ctx.author
                
                await cur.execute('select * from warndata where guild=%s and member=%s', (
                    ctx.guild.id, member.id
                ))
                warns = await cur.fetchall()
                pgr = pager.Pager(warns, 8)
                
                await ctx.send(embed=await self.embedmgr.get(ctx, 'Warn_list', pgr, member))

    @commands.has_permissions(manage_messages=True, add_reactions=True)
    @commands.command(name="경고부여")
    async def _warn_give(self, ctx: commands.Context, member: typing.Optional[discord.Member], reason=None, count: int=1):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                msg = await ctx.send(ctx.author.mention, embed=await self.embedmgr.get(ctx, 'Warn_give_ask', member, reason, count))
                emjs = [self.emj.get(ctx, 'check'), self.emj.get(ctx, 'cross')]
                for em in emjs:
                    await msg.add_reaction(em)
                self.msglog.log(ctx, '[등록: 등록하기]')
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=lambda r, u: u == ctx.author and msg.id == r.message.id and r.emoji in emjs)
                except asyncio.TimeoutError:
                    try:
                        await msg.delete()
                    except:
                        pass
                else:
                    if reaction.emoji == emjs[0]:
                        await cur.execute('insert into warndata (uuid, guild, member, count, warnby, reason, dt) values (%s, %s, %s, %s, %s, %s, %s)', (
                            uuid.uuid4().hex, ctx.guild.id, member.id, count, ctx.author.id, reason, datetime.datetime.now()
                        ))

def setup(bot):
    cog = Warncmds(bot)
    bot.add_cog(cog)