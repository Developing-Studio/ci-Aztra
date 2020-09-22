import discord
import datetime
from utils import pager, timedelta
from utils.embedmgr import aEmbedBase, aMsgBase
from utils.customfmt import greeting_message


class Greeting_dashboard(aEmbedBase):
    async def ko(self, greeting: dict):
        channel = self.cog.bot.get_channel(greeting["channel"])
        return (
            discord.Embed(title="👋 환영 메시지", color=self.cog.color["info"])
            .add_field(name="전송 채널", value=channel.mention)
            .add_field(name="제목 양식", value=greeting.get("title_format"))
            .add_field(name="내용 양식", value=greeting.get("desc_format"))
            .set_footer(text="👀: 미리보기")
        )


class Greeting_not_set(aEmbedBase):
    async def ko(self):
        return discord.Embed(
            title="👋 환영 메시지",
            description="이 서버에는 환영 메시지가 설정되어 있지 않습니다!",
            color=self.cog.color["info"],
        ).set_footer(text=f"[ {self.cog.prefix}환영메시지 설정 ] 명령으로 설정할 수 있습니다")


class Greeting_preview(aEmbedBase):
    async def ko(self, greeting: dict):
        return discord.Embed(
            title=discord.utils.escape_markdown(
                greeting_message(greeting.get("title_format"), self.ctx.author),
                as_needed=True,
            ),
            description=discord.utils.escape_markdown(
                greeting_message(greeting.get("desc_format"), self.ctx.author),
                as_needed=True,
            ),
            color=self.cog.color["primary"],
        ).set_author(name="👀 환영 메시지 미리보기")


class Greeting_setup(aEmbedBase):
    async def ko(self, part: str):
        partname = {"title": "제목", "desc": "내용"}.get(part)
        return discord.Embed(
            description=f"**환영 메시지의 {partname}을(를) 입력해주세요.**",
            color=self.cog.color["ask"],
        )