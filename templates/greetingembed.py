import discord
import datetime
from utils import pager, timedelta
from utils.embedmgr import aEmbedBase, aMsgBase


class Greeting_dashboard(aEmbedBase):
    async def ko(self, greeting):
        channel = self.cog.bot.get_channel(greeting["channel"])
        return (
            discord.Embed(title="👋 환영 메시지", color=self.cog.color["info"])
            .add_field(name="전송 채널", value=channel.mention)
            .add_field(
                name="전송 메시지 양식",
                value=f"""\
                    **{greeting['title_format']}**
                    {greeting['desc_format']}
                """,
            )
        )


class Greeting_not_set(aEmbedBase):
    async def ko(self):
        return discord.Embed(
            title="👋 환영 메시지",
            description="이 서버에는 환영 메시지가 설정되어 있지 않습니다!",
            color=self.cog.color["info"],
        )
