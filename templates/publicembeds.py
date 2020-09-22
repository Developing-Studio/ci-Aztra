import discord
from discord.ext import commands
from utils.basecog import BaseCog
from utils.embedmgr import aEmbedBase


class Canceled(aEmbedBase):
    async def ko(self):
        embed = discord.Embed(title="❌ 취소되었습니다.", color=self.cog.color["error"])
        return embed

    async def en(self):
        embed = discord.Embed(title="❌ Canceled.", color=self.cog.color["error"])
        return embed


class MissingArgs(aEmbedBase):
    async def ko(self, paramdesc):
        return discord.Embed(
            title="❗ 명령어에 빠진 부분이 있습니다!",
            description=f"**`{paramdesc}`이(가) 필요합니다!**\n자세한 명령어 사용법은 `{self.cog.prefix}도움` 을 통해 확인하세요!",
            color=self.cog.color["error"],
        )


class CharNotFound(aEmbedBase):
    async def ko(self, charname):
        return discord.Embed(
            title=f"❓ 존재하지 않는 캐릭터입니다!: `{charname}`", color=self.cog.color["error"]
        )


class NotEnoughMoney(aEmbedBase):
    async def ko(self, more_required: int):
        return discord.Embed(
            title="❓ 돈이 부족합니다!",
            description=f"`{more_required}`골드가 부족합니다!",
            color=self.cog.color["error"],
        )


class TextLengthLimitExceeded(aEmbedBase):
    async def ko(self, length: int, limit: int):
        return discord.Embed(
            title="⛔ 글자 수 제한 초과!",
            description=f"입력한 글자 수({length})가 너무 깁니다! (최대 {limit}자)"
        )