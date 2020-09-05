import discord
from discord.ext import commands
import datetime
import asyncio
import typing
import aiomysql
from utils.basecog import BaseCog
from utils import pager, emojibuttons

class Managecmds(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        for cmd in self.get_commands():
            cmd.add_check(commands.guild_only())

    @commands.has_permissions(manage_messages=True)
    @commands.command(name='청소', aliases=['clear'])
    async def _clear(self, ctx: commands.Context, count: int):
        msgs = await ctx.channel.purge(limit=count)
        await ctx.send(
            embed=await self.embedmgr.get(ctx, 'Manage_clear', msgs),
            delete_after=5
        )

    @commands.command(name='유저', aliases=['user', 'userinfo', '유저정보', '멤버정보', '사용자정보', 'memberinfo', 'member'])
    async def _userinfo(self, ctx: commands.Context, member: typing.Optional[discord.Member]=None):
        if not member:
            member = ctx.author
        
        await ctx.send(embed=await self.embedmgr.get(ctx, 'User_info', member))

def setup(bot):
    cog = Managecmds(bot)
    bot.add_cog(cog)