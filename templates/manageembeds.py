import discord
from utils.embedmgr import aEmbedBase, aMsgBase
import datetime
from dateutil import tz

class Manage_clearing(aEmbedBase):
    async def ko(self):
        return discord.Embed(
            description='{} 메시지를 청소하는 중...'.format(self.cog.emj.get(self.ctx, 'loading')),
            color=self.cog.color['ask']
        )


class Manage_too_old_to_clear(aEmbedBase):
    async def ko(self):
        return discord.Embed(
            description='{} 디스코드 자체 제한으로 인해 2주가 지난 메시지는 삭제할 수 없습니다!'.format(self.cog.emj.get(self.ctx, 'cross')),
            color=self.cog.color['error']
        )


class Manage_clear_done(aEmbedBase):
    async def ko(self, msgs):
        return discord.Embed(
            description=f"**`{len(msgs)}` 개의 메시지를 삭제했습니다.**",
            color=self.cog.color["success"],
        )


class User_info(aEmbedBase):
    async def ko(self, member: discord.Member):
        embed = discord.Embed(title=f"📋｜{member} 님의 정보", color=self.cog.color["info"])
        embed.add_field(name="서버 닉네임", value=member.display_name)
        embed.add_field(
            name="상태",
            value={
                discord.Status.online: "🟢 온라인",
                discord.Status.idle: "🟡 자리 비움",
                discord.Status.dnd: "🔴 다른 용무 중",
                discord.Status.offline: "⚫ 오프라인",
            }.get(member.status),
        )
        activity = self.ctx.author.activities[0]
        embed.add_field(
            name="상태 메시지",
            value=activity.name
            + " "
            + {
                discord.ActivityType.playing: "하는 중",
                discord.ActivityType.listening: "듣는 중",
                discord.ActivityType.streaming: "방송 중",
                discord.ActivityType.watching: "시청 중",
            }.get(activity.type, ""),
            inline=False,
        )
        embed.add_field(
            name="최상위 역할",
            value=self.ctx.author.top_role.mention
            if self.ctx.author.top_role
            else "없음",
            inline=False,
        )
        embed.add_field(
            name="디스코드 가입 일자",
            value=member.created_at.replace(tzinfo=tz.tzutc())
            .astimezone(tz.tzlocal())
            .strftime("%Y년 %m월 %d일 %X"),
            inline=False,
        )
        embed.add_field(
            name="서버 참여 일자",
            value=member.joined_at.replace(tzinfo=tz.tzutc())
            .astimezone(tz.tzlocal())
            .strftime("%Y년 %m월 %d일 %X"),
        )
        embed.set_thumbnail(url=self.ctx.author.avatar_url)
        return embed