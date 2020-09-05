import discord
from discord.ext import tasks
import asyncio
import aiomysql
from utils.basecog import BaseCog
from utils import datamgr
import traceback
import datetime
import math
from configs import advlogging

# pylint: disable=no-member

class Tasks(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.gamenum = 0
        self.last_reset = datetime.datetime.now()
        self.logger.info('백그라운드 루프를 시작합니다.')
        self.sync_guilds.start()
        self.presence_loop.start()
        self.pingloop.start()

    def cog_unload(self):
        self.sync_guilds.cancel()
        self.presence_loop.cancel()
        self.pingloop.cancel()

    @tasks.loop(seconds=5)
    async def pingloop(self):
        try:
            ping = int(self.bot.latency*100000)/100
            if ping <= 100:
                pinglevel = 0
            elif ping <= 300:
                pinglevel = 1
            elif ping <= 500:
                pinglevel = 2
            elif ping <= 700:
                pinglevel = 3
            else:
                pinglevel = 4
            self.bot.set_data('ping', (ping, pinglevel))
            self.pinglogger.info(f'{ping}ms')
            self.pinglogger.info(f'CLIENT_CONNECTED: {not self.bot.is_closed()}')
            guildshards = {}
            if self.bot.shard_id:
                for one in self.bot.latencies:
                    guildshards[one[0]] = tuple(filter(lambda guild: guild.shard_id == one[0], self.bot.guilds))
            self.bot.set_data('guildshards', guildshards)
        except:
            self.errlogger.error(traceback.format_exc())

    @tasks.loop(seconds=5)
    async def sync_guilds(self):
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute('select id from serverdata')
                    db_guilds = await cur.fetchall()
                    db_guild_ids = list(map(lambda one: one['id'], db_guilds))
                    client_guild_ids = list(map(lambda one: one.id, self.bot.guilds))
                    
                    # 등록 섹션
                    added_ids = list(set(client_guild_ids) - set(db_guild_ids))
                    added = list(map(lambda one: self.bot.get_guild(one), added_ids))
                    async def add_guild(guild: discord.Guild):
                        self.logger.info(f'새 서버를 발견했습니다: {guild.name}({guild.id})')
                        sendables = list(filter(lambda ch: ch.permissions_for(guild.me).send_messages, guild.text_channels))
                        if sendables:
                            selected = []
                            for sch in sendables:
                                sname = sch.name.lower()
                                if '공지' in sname and '봇' in sname:
                                    pass
                                elif 'noti' in sname and 'bot' in sname:
                                    pass

                                elif '공지' in sname:
                                    pass
                                elif 'noti' in sname:
                                    pass
                                elif 'announce' in sname:
                                    pass

                                elif '봇' in sname:
                                    pass
                                elif 'bot' in sname:
                                    pass

                                else:
                                    continue
                                selected.append(sch)
                            
                            if not selected:
                                selected.append(sendables[0])
                            await cur.execute('insert into serverdata(id, noticechannel, master) values (%s, %s, %s)', (guild.id, sendables[0].id, 0))
                            self.logger.info(f'서버 추가 성공: ' + guild.name + f'({guild.id})')
                            embed = discord.Embed(title='🎉 안녕하세요!', description=f'안녕하세요! Aztra를 초대해 주셔서 감사합니다. `{self.prefix}도움` 명령으로 전체 명령어를 확인할 수 있어요!', color=self.color['primary'])
                            embed.set_footer(text=f"혹시 이 채널이 공지 채널이 아닌가요? '{self.prefix}공지채널' 명령으로 선택하세요!\n")
                            await sendables[0].send(embed=embed)
                            async def send_log(channel_id: int):
                                channel = self.bot.get_channel(channel_id)
                                await channel.send(embed=discord.Embed(title='{} 새 서버를 추가했습니다'.format(self.emj.get(None, 'check')), description='{g}({g.id})'.format(g=guild), color=self.color['info']))
                            aws = []
                            for cid in advlogging.IO_LOG_CHANNEL_IDS:
                                aws.append(send_log(cid))
                            asyncio.gather(*aws)
                        else:
                            await cur.execute('insert into serverdata(id, noticechannel, master) values (%s, %s, %s)', (guild.id, None, 0))
                            self.logger.info(f'접근 가능한 채널이 없는 서버 추가 성공: ' + guild.name + f'({guild.id})')
                            async def send_log(channel_id: int):
                                channel = self.bot.get_channel(channel_id)
                                await channel.send(embed=discord.Embed(title='{} 새 서버를 추가했습니다'.format(self.emj.get(None, 'check')), description='{g}({g.id})\n(접근 가능한 채널 없음)'.format(g=guild), color=self.color['info']))
                            aws = []
                            for cid in advlogging.IO_LOG_CHANNEL_IDS:
                                aws.append(send_log(cid))
                            asyncio.gather(*aws)

                    for guild in added:
                        await add_guild(guild)

                    # 제거 섹션
                    deleted_ids = list(set(db_guild_ids) - set(client_guild_ids))
                    async def del_guild(gid: int):
                        self.logger.info(f'존재하지 않는 서버를 발견했습니다: {gid}')
                        await cur.execute('delete from serverdata where id=%s', gid)
                        async def send_log(channel_id: int):
                            channel = self.bot.get_channel(channel_id)
                            await channel.send(embed=discord.Embed(title='{} 존재하지 않거나 나간 서버를 발견했습니다'.format(self.emj.get(None, 'cross')), description=f'DB에서 제거했습니다\nID: `{gid}`', color=self.color['info']))
                        aws = []
                        for cid in advlogging.IO_LOG_CHANNEL_IDS:
                            aws.append(send_log(cid))
                        asyncio.gather(*aws)

                    dellist = []
                    for gid in deleted_ids:
                        dellist.append(del_guild(gid))

                    await asyncio.gather(*dellist)

        except:
            self.bot.get_data('errlogger').error(traceback.format_exc())

    @tasks.loop(seconds=5)
    async def presence_loop(self):
        try:
            if self.bot.get_data('shutdown_left') is not None:
                await self.bot.change_presence(
                    activity=discord.Game(
                        str(math.trunc(self.bot.get_data('shutdown_left'))) + '초 후 종료'
                    )
                )
            elif self.bot.get_data('on_inspection') == True:
                await self.bot.change_presence(
                    status=discord.Status.idle,
                    activity=discord.Game(
                        'Aztra 점검 중'
                    )
                )
            else:
                games = [
                    f'{self.prefix}도움 입력!',
                    f'{self.prefix}도움 | {len(self.bot.guilds)} 서버',
                    f'{self.prefix}도움 | {len(self.bot.users)} 사용자'
                ]
                await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(games[self.gamenum]))
                if self.gamenum == len(games)-1:
                    self.gamenum = 0
                else:
                    self.gamenum += 1
        except:
            self.errlogger.error(traceback.format_exc())

    @pingloop.before_loop
    @sync_guilds.before_loop
    @presence_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

def setup(bot):
    cog = Tasks(bot)
    bot.add_cog(cog)