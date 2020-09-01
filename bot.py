import discord
from discord.ext import commands
import asyncio
import aiomysql
import os
import paramiko
import platform
import json
import logging
import logging.handlers
from setting import general
from utils import msglogger

bot = commands.Bot(command_prefix='//')
bot.remove_command('help')

# Make Dir
reqdirs = ['./logs', './logs/azalea', './logs/error', './logs/ping', './logs/discord']
for dit in reqdirs:
    if not os.path.isdir(dit):
        os.makedirs(dit)

logger = logging.getLogger('azalea')
logger.setLevel(logging.DEBUG)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_streamh = logging.StreamHandler()
log_streamh.setFormatter(log_formatter)
logger.addHandler(log_streamh)
log_fileh = logging.handlers.RotatingFileHandler('./logs/azalea/azalea.log', maxBytes=general.MAX_LOG_FILE_BYTES, backupCount=10, encoding='utf-8')
log_fileh.setFormatter(log_formatter)
logger.addHandler(log_fileh)

dlogger = logging.getLogger('discord')
dlogger.setLevel(logging.INFO)
dhandler = logging.handlers.RotatingFileHandler(filename='./logs/discord/discord.log', maxBytes=general.MAX_LOG_FILE_BYTES, backupCount=10, encoding='utf-8')
dformatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s: %(message)s')
dlog_streamh = logging.StreamHandler()
dhandler.setFormatter(dformatter)
dlog_streamh.setFormatter(dformatter)
dlogger.addHandler(dhandler)
dlogger.addHandler(dlog_streamh)

pinglogger = logging.getLogger('ping')
pinglogger.setLevel(logging.INFO)
ping_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ping_fileh = logging.handlers.RotatingFileHandler('./logs/ping/ping.log', maxBytes=general.MAX_LOG_FILE_BYTES, backupCount=10, encoding='utf-8')
ping_fileh.setFormatter(ping_formatter)
pinglogger.addHandler(ping_fileh)

errlogger = logging.getLogger('error')
errlogger.setLevel(logging.DEBUG)
err_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
err_streamh = logging.StreamHandler()
err_streamh.setFormatter(err_formatter)
errlogger.addHandler(err_streamh)
err_fileh = logging.handlers.RotatingFileHandler('./logs/error/error.log', maxBytes=general.MAX_LOG_FILE_BYTES, backupCount=10, encoding='utf-8')
err_fileh.setFormatter(err_formatter)
errlogger.addHandler(err_fileh)

logger.info('========== START ==========')

# IMPORTant data
if platform.system() == 'Windows':
    if general.BETA_MODE == False:
        with open(os.path.abspath(general.SECURE_DIR.get('Windows')) + '\\' + general.TOKEN_FILE_NAME, encoding='utf-8') as token_file:
            token = token_file.read()
    else:
        with open(os.path.abspath(general.SECURE_DIR.get('Windows')) + '\\' + general.BETA_TOKEN_FILE_NAME, encoding='utf-8') as token_file:
            token = token_file.read()
    with open(os.path.abspath(general.SECURE_DIR.get('Windows')) + '\\' + general.DBAC_FILE_NAME, encoding='utf-8') as dbac_file:
        dbac = json.load(dbac_file)
    with open(os.path.abspath(general.SECURE_DIR.get('Windows')) + '\\' + general.SSH_FILE_NAME, encoding='utf-8') as ssh_file:
        ssh = json.load(ssh_file)
elif platform.system() == 'Linux':
    if general.IS_ANDROID:
        if general.BETA_MODE == False:
            with open(os.path.abspath(general.SECURE_DIR.get('Android')) + '/' + general.TOKEN_FILE_NAME, encoding='utf-8') as token_file:
                token = token_file.read()
        else:
            with open(os.path.abspath(general.SECURE_DIR.get('Android')) + '/' + general.BETA_TOKEN_FILE_NAME, encoding='utf-8') as token_file:
                token = token_file.read()
        with open(os.path.abspath(general.SECURE_DIR.get('Android')) + '/' + general.DBAC_FILE_NAME, encoding='utf-8') as dbac_file:
            dbac = json.load(dbac_file)
        with open(os.path.abspath(general.SECURE_DIR.get('Android')) + '/' + general.SSH_FILE_NAME, encoding='utf-8') as ssh_file:
            ssh = json.load(ssh_file)
    else:
        if general.BETA_MODE == False:
            with open(os.path.abspath(general.SECURE_DIR.get('Linux')) + '/' + general.TOKEN_FILE_NAME, encoding='utf-8') as token_file:
                token = token_file.read()
        else:
            with open(os.path.abspath(general.SECURE_DIR.get('Linux')) + '/' + general.BETA_TOKEN_FILE_NAME, encoding='utf-8') as token_file:
                token = token_file.read()
        with open(os.path.abspath(general.SECURE_DIR.get('Linux')) + '/' + general.DBAC_FILE_NAME, encoding='utf-8') as dbac_file:
            dbac = json.load(dbac_file)
        with open(os.path.abspath(general.SECURE_DIR.get('Linux')) + '/' + general.SSH_FILE_NAME, encoding='utf-8') as ssh_file:
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
if general.BETA_MODE:
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

msglog = msglogger.Msglog(logger)

for ext in filter(lambda x: x.endswith('.py'), os.listdir('./exts')):
    bot.load_extension('exts.' + os.path.splitext(ext)[0])