import discord
from utils.embedmgr import aEmbedBase, aMsgBase
import datetime
from dateutil import tz


class Manage_clearing(aEmbedBase):
    async def ko(self):
        return discord.Embed(
            description="{} 메시지를 청소하는 중...".format(
                self.cog.emj.get(self.ctx, "loading")
            ),
            color=self.cog.color["ask"],
        )


class Manage_too_old_to_clear(aEmbedBase):
    async def ko(self):
        return discord.Embed(
            description="{} 디스코드 자체 제한으로 인해 2주가 지난 메시지는 삭제할 수 없습니다!".format(
                self.cog.emj.get(self.ctx, "cross")
            ),
            color=self.cog.color["error"],
        )


class Manage_clear_done(aEmbedBase):
    async def ko(self, msgs):
        return discord.Embed(
            description=f"**`{len(msgs)}` 개의 메시지를 삭제했습니다.**",
            color=self.cog.color["success"],
        )


class User_info(aEmbedBase):
    async def ko(self, member: discord.Member):
        activity = member.activities[0] if member.activities else None
        sangme = (
            discord.utils.escape_markdown(activity.name, as_needed=True)
            + " "
            + {
                discord.ActivityType.playing: "하는 중",
                discord.ActivityType.listening: "듣는 중",
                discord.ActivityType.streaming: "방송 중",
                discord.ActivityType.watching: "시청 중",
            }.get(activity.type, "")
            if activity
            else "(없음)"
        )
        return (
            discord.Embed(title=f"📋 | {member} 님의 정보", color=self.cog.color["info"])
            .add_field(name="**디스코드 ID**", value=member.id)
            .add_field(name="**서버 닉네임**", value=member.display_name)
            .add_field(
                name="**상태**",
                value={
                    discord.Status.online: "🟢 온라인",
                    discord.Status.idle: "🟡 자리 비움",
                    discord.Status.dnd: "🔴 다른 용무 중",
                    discord.Status.offline: "⚫ 오프라인",
                }.get(member.status),
                inline=False,
            )
            .add_field(
                name="**상태 메시지**",
                value=(sangme[:200] + "..." if len(sangme) > 200 else sangme),
                inline=False,
            )
            .add_field(
                name="**최상위 역할**",
                value=member.top_role.mention if member.top_role else "없음",
                inline=False,
            )
            .add_field(
                name="**디스코드 가입 일자**",
                value=member.created_at.replace(tzinfo=tz.tzutc())
                .astimezone(tz.tzlocal())
                .strftime("%Y년 %m월 %d일 %X"),
                inline=False,
            )
            .add_field(
                name="**서버 참여 일자**",
                value=member.joined_at.replace(tzinfo=tz.tzutc())
                .astimezone(tz.tzlocal())
                .strftime("%Y년 %m월 %d일 %X"),
            )
            .set_thumbnail(url=member.avatar_url)
        )


class Guild_info(aEmbedBase):
    async def ko(self):
        region = (
            str(self.ctx.guild.region).replace("-", " ").title().replace("Us", "US", 1)
        )
        regioncode = {
            "South Korea": "kr",
            "Brazil": "br",
            "Europe": "eu",
            "Hong Kong": "hk",
            "India": "in",
            "Japan": "jp",
            "Russia": "ru",
            "Singapore": "sg",
            "Southafrica": "za",
            "Sydney": "au",
            "US Central": "us",
            "US East": "us",
            "US West": "us",
            "US South": "us",
        }.get(region)
        return (
            discord.Embed(title="🧾 | 서버 정보", color=self.cog.color["info"])
            .add_field(name="**서버 이름**", value=self.ctx.guild.name)
            .add_field(
                name="**서버 위치**",
                value=f":flag_{regioncode}: " + region if regioncode else region,
            )
            .add_field(name="멤버 수", value=len(self.ctx.guild.members))
            .add_field(
                name="**이모지**",
                value="""\
                    일반 `{}`개, 움직이는 이모지 `{}`개
                    (최대 `{}`개씩)
                """.format(
                    len(list(filter(lambda x: not x.animated, self.ctx.guild.emojis))),
                    len(list(filter(lambda x: x.animated, self.ctx.guild.emojis))),
                    self.ctx.guild.emoji_limit,
                ),
                inline=False,
            )
            .add_field(
                name="**서버 부스트 레벨**",
                value="부스트 없음"
                if self.ctx.guild.premium_subscription_count == 0
                else f"""\
                    레벨 {self.ctx.guild.premium_tier}
                    (부스트 {self.ctx.guild.premium_subscription_count}개)
                """,
            )
            .add_field(
                name="**잠수 채널**",
                value=self.ctx.guild.afk_channel.mention
                if self.ctx.guild.afk_channel
                else "(없음)",
            )
            .add_field(
                name="**서버 생성 일자**",
                value=self.ctx.guild.created_at.replace(tzinfo=tz.tzutc())
                .astimezone(tz.tzlocal())
                .strftime("%Y년 %m월 %d일 %X"),
            )
            .set_thumbnail(url=self.ctx.guild.icon_url)
        )


class Guild_info_settings(aEmbedBase):
    async def ko(self):
        return (
            discord.Embed(title="🧾 | 서버 정보 - 서버 설정 정보", color=self.cog.color["info"])
            .add_field(
                name="**2단계 인증 필요 여부**",
                value="예" if self.ctx.guild.mfa_level else "아니오",
            )
            .add_field(
                name="**보안 수준**",
                value={
                    discord.VerificationLevel.none: "없음",
                    discord.VerificationLevel.low: "낮음",
                    discord.VerificationLevel.medium: "보통",
                    discord.VerificationLevel.high: "높음",
                    discord.VerificationLevel.very_high: "매우 높음",
                }.get(self.ctx.guild.verification_level),
            )
            .add_field(
                name="**콘텐츠 필터**",
                value={
                    discord.ContentFilter.disabled: "스캔하지 않음",
                    discord.ContentFilter.no_role: "역할 없는 멤버만 스캔",
                    discord.ContentFilter.all_members: "모든 멤버 스캔",
                }.get(self.ctx.guild.explicit_content_filter),
            )
            .add_field(
                name="**기본 알림 설정**",
                value={
                    discord.NotificationLevel.only_mentions: "@mentions만",
                    discord.NotificationLevel.all_messages: "모든 메시지",
                }.get(self.ctx.guild.default_notifications),
            )
        )