from discord.ext import commands
from setting import masters
from . import errors

async def master_only(ctx: commands.Context):
    if ctx.author.id in masters.MASTER_IDS:
        return True
    raise errors.NotMaster