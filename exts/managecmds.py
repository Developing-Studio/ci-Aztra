import discord
from discord.ext import commands
import datetime
import asyncio
import typing
import aiomysql
from utils.basecog import BaseCog
from utils import pager, emojibuttons, errors

class Managecmds(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        for cmd in self.get_commands():
            cmd.add_check(commands.guild_only())

    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True, read_message_history=True)
    @commands.command(name='clear', aliases=['청소', '클리어'])
    async def _clear(self, ctx: commands.Context, count: int):
        await ctx.message.delete()
        after = datetime.datetime.utcnow() - datetime.timedelta(days=14)
        last_msg = next(iter(await ctx.channel.history(after=after, limit=1, oldest_first=False).flatten()), None)
        if not last_msg:
            await ctx.send(embed=await self.embedmgr.get(ctx, 'Manage_too_old_to_clear', delafter=7), delete_after=7)
            return

        cleartask = asyncio.create_task(ctx.channel.purge(limit=count, after=after))
        msg = await ctx.send(embed=await self.embedmgr.get(ctx, 'Manage_clearing'))
        msgs = await cleartask
        await msg.edit(
            embed=await self.embedmgr.get(ctx, 'Manage_clear_done', msgs),
            delete_after=5
        )
        self.msglog.log(ctx, '[청소]')

    @commands.command(name='userinfo', aliases=['유저정보', '멤버정보', '사용자정보', 'memberinfo'])
    async def _userinfo(self, ctx: commands.Context, member: typing.Optional[discord.Member]=None):
        if not member:
            member = ctx.author
        
        await ctx.send(
            embed=await self.embedmgr.get(ctx, 'User_info', member),
            allowed_mentions=discord.AllowedMentions(roles=False, everyone=False)
        )

    @commands.group(name='serverinfo', aliases=['서버정보', '길드정보', 'guildinfo'], invoke_without_command=False)
    async def _guildinfo(self, ctx: commands.Context):
        if ctx.invoked_subcommand is not None or ctx.subcommand_passed is None:
            await ctx.send(
                embed=await self.embedmgr.get(ctx, 'Guild_info'),
                allowed_mentions=discord.AllowedMentions(roles=False, everyone=False)
            )
        else:
            raise errors.SubcommandNotFound

    @_guildinfo.command(name='settings', aliases=['설정', 'setting'])
    async def _guildinfo_(self, ctx: commands.Context):
        await ctx.send(
            embed=await self.embedmgr.get(ctx, 'Guild_info_settings'),
            allowed_mentions=discord.AllowedMentions(roles=False, everyone=False)
        )
        

def setup(bot):
    cog = Managecmds(bot)
    bot.add_cog(cog)