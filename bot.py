import discord
import datetime
import json
import asyncio
import platform
import importlib
import aiomysql
import os
import logging
import logging.handlers
import paramiko
from utils import errors, checks, msglogger, emojictrl, datamgr, embedmgr
from utils.aztra import Aztra
from db import permissions
from templates import aztraembeds, eventembeds, basecembeds, publicembeds

# Local Data Load
with open('./data/config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)
with open('./data/version.json', 'r', encoding='utf-8') as version_file:
    version = json.load(version_file)
with open('./data/color.json', 'r', encoding='utf-8') as color_file:
    color = json.load(color_file)
with open('./data/emojis.json', 'r', encoding='utf-8') as emojis_file:
    emojis = json.load(emojis_file)
with open('./data/prefixes.json', 'r', encoding='utf-8') as prefixes_file:
    prefixes = json.load(prefixes_file)['prefixes']
    prefix = prefixes[0]

# Make Dir
reqdirs = ['./logs', './logs/aztra', './logs/error', './logs/ping', './logs/discord']
for dit in reqdirs:
    if not os.path.isdir(dit):
        os.makedirs(dit)

# Setup Logging
logger = logging.getLogger('aztra')
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_streamh = logging.StreamHandler()
log_streamh.setFormatter(log_formatter)
logger.addHandler(log_streamh)
log_fileh = logging.handlers.RotatingFileHandler('./logs/aztra/aztra.log', maxBytes=config['maxlogbytes'], backupCount=10, encoding='utf-8')
log_fileh.setFormatter(log_formatter)
logger.addHandler(log_fileh)

dlogger = logging.getLogger('discord')
dlogger.setLevel(logging.INFO)
dhandler = logging.handlers.RotatingFileHandler(filename='./logs/discord/discord.log', maxBytes=config['maxlogbytes'], backupCount=10, encoding='utf-8')
dformatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s: %(message)s')
dlog_streamh = logging.StreamHandler()
dhandler.setFormatter(dformatter)
dlog_streamh.setFormatter(dformatter)
dlogger.addHandler(dhandler)
dlogger.addHandler(dlog_streamh)

pinglogger = logging.getLogger('ping')
pinglogger.setLevel(logging.INFO)
ping_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ping_fileh = logging.handlers.RotatingFileHandler('./logs/ping/ping.log', maxBytes=config['maxlogbytes'], backupCount=10, encoding='utf-8')
ping_fileh.setFormatter(ping_formatter)
pinglogger.addHandler(ping_fileh)

errlogger = logging.getLogger('error')
errlogger.setLevel(logging.DEBUG)
err_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
err_streamh = logging.StreamHandler()
err_streamh.setFormatter(err_formatter)
errlogger.addHandler(err_streamh)
err_fileh = logging.handlers.RotatingFileHandler('./logs/error/error.log', maxBytes=config['maxlogbytes'], backupCount=10, encoding='utf-8')
err_fileh.setFormatter(err_formatter)
errlogger.addHandler(err_fileh)

logger.info('========== START ==========')

# IMPORTant data
if platform.system() == 'Windows':
    if config['betamode'] == False:
        with open(os.path.abspath(config['securedir']['Windows']) + '\\' + config['tokenFileName'], encoding='utf-8') as token_file:
            token = token_file.read()
    else:
        with open(os.path.abspath(config['securedir']['Windows']) + '\\' + config['betatokenFileName'], encoding='utf-8') as token_file:
            token = token_file.read()
    with open(os.path.abspath(config['securedir']['Windows']) + '\\' + config['dbacName'], encoding='utf-8') as dbac_file:
        dbac = json.load(dbac_file)
    with open(os.path.abspath(config['securedir']['Windows']) + '\\' + config['sshFileName'], encoding='utf-8') as ssh_file:
        ssh = json.load(ssh_file)
elif platform.system() == 'Linux':
    if config['is_android']:
        if config['betamode'] == False:
            with open(os.path.abspath(config['securedir']['Android']) + '/' + config['tokenFileName'], encoding='utf-8') as token_file:
                token = token_file.read()
        else:
            with open(os.path.abspath(config['securedir']['Android']) + '/' + config['betatokenFileName'], encoding='utf-8') as token_file:
                token = token_file.read()
        with open(os.path.abspath(config['securedir']['Android']) + '/' + config['dbacName'], encoding='utf-8') as dbac_file:
            dbac = json.load(dbac_file)
        with open(os.path.abspath(config['securedir']['Android']) + '/' + config['sshFileName'], encoding='utf-8') as ssh_file:
            ssh = json.load(ssh_file)
    else:
        if config['betamode'] == False:
            with open(os.path.abspath(config['securedir']['Linux']) + '/' + config['tokenFileName'], encoding='utf-8') as token_file:
                token = token_file.read()
        else:
            with open(os.path.abspath(config['securedir']['Linux']) + '/' + config['betatokenFileName'], encoding='utf-8') as token_file:
                token = token_file.read()
        with open(os.path.abspath(config['securedir']['Linux']) + '/' + config['dbacName'], encoding='utf-8') as dbac_file:
            dbac = json.load(dbac_file)
        with open(os.path.abspath(config['securedir']['Linux']) + '/' + config['sshFileName'], encoding='utf-8') as ssh_file:
            ssh = json.load(ssh_file)

loop = asyncio.get_event_loop()

# SSH Connect
sshclient = paramiko.SSHClient()
sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy)
sshclient.connect(ssh['host'], username=ssh['user'], password=ssh['password'], port=ssh['port'])

async def dbcmd(cmd):
    _, stdout, _ = await bot.loop.run_in_executor(None, sshclient.exec_command, cmd)
    lines = stdout.readlines()
    return ''.join(lines)

# DB Connect
dbkey = 'default'
if config['betamode']:
    dbkey = 'beta'

async def connect_db():
    pool = await aiomysql.create_pool(
        host=dbac[dbkey]['host'],
        user=dbac[dbkey]['dbUser'],
        password=dbac[dbkey]['dbPassword'],
        db=dbac[dbkey]['dbName'],
        charset='utf8',
        autocommit=True
    )
    return pool
    
pool = loop.run_until_complete(connect_db())

bot = Aztra(command_prefix=prefixes, error=errors, status=discord.Status.dnd, activity=discord.Game('아즈트라 시작'))
bot.remove_command('help')

# 메시지로거
msglog = msglogger.Msglog(logger)

for i in color.keys(): # convert HEX to DEC
    color[i] = int(color[i], 16)

emj = emojictrl.Emoji(bot, emojis['emoji-server'], emojis['emojis'])

# DB 로드

def loader(datadb: datamgr.DataDB):
    datadb.load_permissions(permissions.PERMISSIONS)

def reloader(datadb: datamgr.DataDB):
    db_modules = [
        permissions
    ]
    for md in db_modules:
        importlib.reload(md)
    loader(datadb)

datadb = datamgr.DataDB()
datadb.set_reloader(reloader)
loader(datadb)

# 임베드 매니저
embedmgr = embedmgr.EmbedMgr(
    pool,
    aztraembeds,
    eventembeds,
    basecembeds,
    publicembeds
)

# 체크 매니저
check = checks.Checks(pool, datadb)

def awaiter(coro):
    return asyncio.ensure_future(coro)

bot.add_check(check.notbot)

# 데이터 적재

bot.add_data('config', config)
bot.add_data('color', color)
bot.add_data('check', check)
bot.add_data('emojictrl', emj)
bot.add_data('msglog', msglog)
bot.add_data('errlogger', errlogger)
bot.add_data('pinglogger', pinglogger)
bot.add_data('logger', logger)
bot.add_data('pool', pool)
bot.add_data('embedmgr', embedmgr)
bot.add_data('dbcmd', dbcmd)
bot.add_data('ping', None)
bot.add_data('shutdown_left', None)
bot.add_data('guildshards', None)
bot.add_data('version_str', version['versionPrefix'] + version['versionNum'])
bot.add_data('lockedexts', ['exts.basecmds'])
bot.add_data('datadb', datadb)
bot.add_data('awaiter', awaiter)
bot.add_data('eventcogname', 'Events')
bot.add_data('start', datetime.datetime.now())
if config['inspection']:
    bot.add_data('on_inspection', True)
    bot.add_check(check.on_inspection)
else:
    bot.add_data('on_inspection', False)

bot.datas['allexts'] = []
for ext in list(filter(lambda x: x.endswith('.py') and not x.startswith('_'), os.listdir('./exts'))):
    bot.datas['allexts'].append('exts.' + os.path.splitext(ext)[0])
    bot.load_extension('exts.' + os.path.splitext(ext)[0])
logger.info('{} 개의 확장을 로드했습니다'.format(len(bot.datas.get('allexts'))))

bot.run(token)