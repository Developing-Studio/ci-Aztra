import discord
from discord.ext import commands
import datetime
import asyncio
import typing
import aiomysql
from utils.basecog import BaseCog
from utils import pager, emojibuttons

class Greetingcmds(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        for cmd in self.get_commands():
            cmd.add_check(commands.guild_only())

    @commands.group(name='환영메시지')
    async def _greeting(self, ctx: commands.Context):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from greetings where guild=%s', ctx.guild.id):
                    greeting = await cur.fetchone()
                    await ctx.send(embed=await self.embedmgr.get(ctx, 'Greeting_dashboard', greeting))
                else:
                    await ctx.send(embed=await self.embedmgr.get(ctx, 'Greeting_not_set'))

    @_greeting.command(name='설정')
    async def _greeting_set(self, ctx: commands.Context):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from greetings where guild=%s', ctx.guild.id):
                    pass

def setup(bot):
    cog = Greetingcmds(bot)
    bot.add_cog(cog)