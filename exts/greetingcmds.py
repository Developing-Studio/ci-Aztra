import discord
from discord.ext import commands
import datetime
import asyncio
import typing
import aiomysql
from utils.basecog import BaseCog
from utils import pager, emojibuttons, event_waiter

class Greetingcmds(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        for cmd in self.get_commands():
            cmd.add_check(commands.guild_only())
            if cmd.name == '환영메시지':
                cmd.add_check(self.check.subcmd_valid)

    @commands.group(name='환영메시지', invoke_without_command=True)
    async def _greeting(self, ctx: commands.Context):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from greetings where guild=%s', ctx.guild.id) == 0:
                    await ctx.send(embed=await self.embedmgr.get(ctx, 'Greeting_not_set'))
                    self.msglog.log(ctx, '[환영메시지: 설정 안됨]')
                    return

                greeting = await cur.fetchone()
                msg = await ctx.send(embed=await self.embedmgr.get(ctx, 'Greeting_dashboard', greeting))
                self.msglog.log(ctx, '[환영메시지: 대시보드]')
                emjs = ['👀']
                async def addreaction(m):
                    for em in emjs:
                        await m.add_reaction(em)
                await addreaction(msg)
                def check(reaction, user):
                    return user == ctx.author and msg.id == reaction.message.id and reaction.emoji in emjs
                while True:
                    try:
                        reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60*5)
                    except asyncio.TimeoutError:
                        try:
                            await msg.clear_reactions()
                        except:
                            pass
                    else:
                        if reaction.emoji in emjs:
                            if ctx.channel.last_message and ctx.channel.last_message_id != msg.id:
                                results = await asyncio.gather(
                                    msg.delete(),
                                    ctx.send(embed=await self.embedmgr.get(ctx, 'Greeting_dashboard', greeting))
                                )
                                msg = results[1]
                                await addreaction(msg)
                                reaction.message = msg

                        if reaction.emoji == '👀':
                            preview_msg = await ctx.send(embed=await self.embedmgr.get(ctx, 'Greeting_preview', greeting))
                            await preview_msg.add_reaction('❌')
                            await event_waiter.wait_for_reaction(self.bot, ctx=ctx, msg=preview_msg, emojis=['❌'], timeout=60*5)
                            await preview_msg.delete()

                        await asyncio.gather(
                            reaction.remove(user),
                            msg.edit(embed=await self.embedmgr.get(ctx, 'Greeting_dashboard', greeting)),
                        )

    @commands.has_permissions(administrator=True)
    @_greeting.command(name='설정')
    async def _greeting_set(self, ctx: commands.Context):
        msg = await ctx.send(embed=await self.embedmgr.get(ctx, 'Greeting_setup', 'title'))
        title_message = await event_waiter.wait_for_message(self.bot, ctx=ctx, timeout=60)
        if len(title_message.content) > 200:
            await ctx.send(embed=await self.embedmgr.get(ctx, 'TextLengthLimitExceeded', len(title_message.content), 200))
            return
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                if await cur.execute('select * from greetings where guild=%s', ctx.guild.id):
                    pass

def setup(bot):
    cog = Greetingcmds(bot)
    bot.add_cog(cog)