import discord
from utils.embedmgr import aEmbedBase, aMsgBase
import datetime
from utils.pager import Pager
from utils import timedelta


class Warn_list(aEmbedBase):
    async def ko(self, pgr: Pager, member):
        now = datetime.datetime.now()
        warns = pgr.get_thispage()
        if not warns:
            return discord.Embed(
                title=f"🚨 {member} 님의 경고가 하나도 없습니다!", color=self.cog.color["warn"]
            )

        embed = discord.Embed(
            title=f"🚨 {member} 님의 경고 목록", description="", color=self.cog.color["warn"]
        )

        for one in warns:
            embed.description += """\
                **{}** ({}회)
                > {}, By {}
            """.format(
                one["reason"],
                one["count"],
                " ".join(list(timedelta.format_timedelta(now - one["dt"]).values())[0])
                + " 전"
                if one["dt"] <= now - datetime.timedelta(minutes=1)
                else "방금",
                self.ctx.guild.get_member(one["warnby"])
                if self.ctx.guild.get_member(one["warnby"])
                else "(알 수 없음)",
            )

        return embed


class Warn_give_ask(aEmbedBase):
    async def ko(self, target, reason, count):
        return (
            discord.Embed(
                title="🚨 경고 부여",
                description="다음과 같이 경고를 부여하시겠습니까?",
                color=self.cog.color["warn"],
            )
            .add_field(name="대상", value=target.mention)
            .add_field(name="사유", value=reason if reason else "(없음)")
            .add_field(name="경고 횟수", value=str(count))
        )