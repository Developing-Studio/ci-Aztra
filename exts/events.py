import discord
from discord.ext import commands
import traceback
import datetime
import asyncio
import sys
import aiomysql
from utils.basecog import BaseCog
from utils import errors, datamgr
import uuid
from configs import advlogging

class Events(BaseCog):
    def __init__(self, bot):
        super().__init__(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info(f'로그인: {self.bot.user.id}')
        await self.bot.change_presence(status=discord.Status.online)
        if self.config['betamode']:
            self.logger.warning('BETA MODE ENABLED')

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        excinfo = sys.exc_info()
        errstr = f'{"".join(traceback.format_tb(excinfo[2]))}{excinfo[0].__name__}: {excinfo[1]}'
        self.errlogger.error('\n========== sERROR ==========\n' + errstr + '\n========== sERREND ==========')

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                uid = uuid.uuid4()
                allerrs = (type(error), type(error.__cause__))
                tb = traceback.format_exception(type(error), error, error.__traceback__)
                origintb = traceback.format_exception(type(error), error, error.__traceback__)
                err = [line.rstrip() for line in tb]
                errstr = '\n'.join(err)
                originerr = err = [line.rstrip() for line in origintb]
                originerrstr = '\n'.join(originerr)
                if isinstance(error, errors.MissingRequiredArgument):
                    await ctx.send(embed=await self.embedmgr.get(ctx, 'Cmderror_MissingArg', error.paramdesc))
                    self.msglog.log(ctx, f'[필요한 명령 인자 없음: "{error.param.name}"({error.paramdesc})]')
                    return

                elif isinstance(error, discord.NotFound):
                    self.msglog.log(ctx, f'[찾을 수 없음]')
                    return

                elif isinstance(error, commands.CommandOnCooldown):
                    return
                    
                elif commands.errors.MissingRequiredArgument in allerrs:
                    self.msglog.log(ctx, '[필요한 명령 인자 없음]')
                    return
                    
                elif isinstance(error, errors.NotRegistered):
                    await ctx.send(embed=await self.embedmgr.get(ctx, 'Cmderror_not_registered'))
                    self.msglog.log(ctx, '[미등록 사용자]')
                    return
                    
                elif isinstance(error, errors.NotMaster):
                    return
                    
                elif isinstance(error, errors.onInspection):
                    await ctx.send(embed=await self.embedmgr.get(ctx, 'Cmderror_on_inspection'))
                    self.msglog.log(ctx, '[점검중]')
                    return
                    
                elif errors.ParamsNotExist in allerrs:
                    await ctx.send(embed=await self.embedmgr.get(ctx, 'Cmderror_params_not_exist', error.__cause__.param))
                    self.msglog.log(ctx, '[존재하지 않는 명령 옵션]')
                    return
                    
                elif isinstance(error, commands.CommandNotFound):
                    return
                    
                elif isinstance(error, errors.SentByBotUser):
                    return

                elif isinstance(error, commands.BadArgument):
                    await ctx.send(embed=await self.embedmgr.get(ctx, 'Cmderror_bad_argument'))
                    self.msglog.log(ctx, '[올바르지 않은 명령 인자]')
                    return
                    
                elif isinstance(error, commands.NoPrivateMessage):
                    await ctx.send(embed=await self.embedmgr.get(ctx, 'Cmderror_no_private_message'))
                    self.msglog.log(ctx, '[길드 전용 명령]')
                    return
                    
                elif isinstance(error, commands.PrivateMessageOnly):
                    await ctx.send(embed=await self.embedmgr.get(ctx, 'Cmderror_private_only'))
                    self.msglog.log(ctx, '[DM 전용 명령]')
                    return
                    
                elif isinstance(error, commands.MissingPermissions):
                    await ctx.send(embed=await self.embedmgr.get(ctx, 'Cmderror_missing_perms', error.missing_perms))
                    self.msglog.log(ctx, '[멤버 권한 부족]')
                    return
                    
                elif isinstance(error, errors.MissingAztraPermissions):
                    await ctx.send(embed=await self.embedmgr.get(ctx, 'Cmderror_missing_aztra_perms', error.missing_perms))
                    self.msglog.log(ctx, '[Azalea 권한 부족]')
                    return

                elif isinstance(error, commands.BotMissingPermissions):
                    await ctx.send(embed=await self.embedmgr.get(ctx, 'Cmderror_missing_bot_perms', error.missing_perms))
                    self.msglog.log(ctx, '[봇 권한 부족]')
                    return
                    
                elif isinstance(error.__cause__, discord.HTTPException):
                    if error.__cause__.code in [50013, 50001]:
                        try:
                            await ctx.send(embed=await self.embedmgr.get(ctx, 'Cmderror_missing_bot_perms'))
                        except discord.Forbidden:
                            await ctx.author.send(embed=await self.embedmgr.get(ctx, 'Cmderror_missing_sendmsg_perm'))
                            self.msglog.log(ctx, '[봇 메시지 전송 권한 없음]')
                        else:
                            self.msglog.log(ctx, '[봇 권한 부족]')
                        return
                        
                    elif error.__cause__.code == 50035:
                        await ctx.send(embed=await self.embedmgr.get(ctx, 'Cmderror_sendfail_too_long'))
                        self.msglog.log(ctx, '[너무 긴 메시지 전송 시도]')
                        return
                        
                    elif error.__cause__.code == 50007:
                        await ctx.send(ctx.author.mention, embed=await self.embedmgr.get(ctx, 'Cmderror_sendfail_dm'))
                        self.msglog.log(ctx, '[DM 전송 실패]')
                        return
                        
                    elif error.__cause__.code == 10008:
                        self.msglog.log(ctx, '[찾을 수 없음]')
                        return

                    else:
                        await ctx.send(await self.embedmgr.get(ctx, 'Cmderror_errcode', error))
                        
                self.msglog.log(ctx, '[커맨드 오류: {}]'.format(uid))
                await cur.execute('insert into error (uuid, content, datetime) values (%s, %s, %s)', (uid.hex, errstr, datetime.datetime.now()))
                causestr = await self.embedmgr.get(ctx, 'Cmderror_error_cause_msg')
                if not await self.check.is_master(ctx.author):
                    # 일반 유저의 경우
                    self.errlogger.error(f'\n========== CMDERROR ========== {uid.hex}\n' + errstr + '\n========== CMDERREND ==========')
                    embed = await self.embedmgr.get(ctx, 'Cmderror_errorembed_foruser', uid)
                    await ctx.send(embed=embed)

                    async def send_log(channel_id: int):
                        channel = self.bot.get_channel(channel_id)
                        if not channel:
                            return
                        try:
                            await channel.send(causestr, embed=embed)
                        except discord.HTTPException as exc:
                            if exc.code == 50035:
                                await channel.send(embed=await self.embedmgr.get(ctx, 'Cmderror_as_file', uid, errstr))

                    sendlist = []
                    for one in advlogging.ERROR_LOG_CHANNEL_IDS:
                        sendlist.append(send_log(one))
                    await asyncio.gather(*sendlist)
                    
                else:
                    # 마스터 유저의 경우
                    print(f'\n========== CMDERROR ========== {uid.hex}\n' + errstr + '\n========== CMDERREND ==========')
                    
                    try:
                        msg = await ctx.author.send(causestr, embed=await self.embedmgr.get(ctx, 'Cmderror_errorembed_formaster', uid, errstr))
                    except discord.HTTPException as exc:
                        if exc.code == 50035:
                            msg = await ctx.author.send(embed=await self.embedmgr.get(ctx, 'Cmderror_as_file', errstr))

                    if ctx.channel.type != discord.ChannelType.private:
                        await ctx.send(ctx.author.mention, embed=await self.embedmgr.get(ctx, 'Cmderror_errdm_sent', msg))

def setup(bot):
    cog = Events(bot)
    bot.add_cog(cog)