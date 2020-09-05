import discord
from utils.embedmgr import aEmbedBase, aMsgBase
import datetime
from dateutil import tz

#
class Manage_clear(aEmbedBase):
    async def ko(self, msgs):
        return discord.Embed(
            description=f'**`{len(msgs)}` 개의 메시지를 삭제했습니다.**',
            color=self.cog.color['success']
        )

class User_info(aEmbedBase):
    async def ko(self, member: discord.Member):
        embed = discord.Embed(
            title=f'📋 | `{member}` 님의 정보',
            color=self.cog.color['info']
        )
        embed.add_field(
            name='디스코드 가입 일자',
            value=member.created_at.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()).strftime('%Y년 %m월 %d일 %X')
        )
        embed.add_field(
            name='서버 참여 일자',
            value=member.joined_at.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal()).strftime('%Y년 %m월 %d일 %X')
        )
        return embed