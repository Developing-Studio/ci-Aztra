import aiomysql
import logging
from discord.ext import commands
from . import msglogger, checks, emojictrl, embedmgr
import sqlite3

class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emj: emojictrl.Emoji = bot.datas.get('emojictrl')
        self.msglog: msglogger.Msglog = bot.datas.get('msglog')
        self.logger: logging.Logger = bot.datas.get('logger')
        self.pool: aiomysql.Connection = bot.datas.get('pool')
        self.errlogger = bot.datas.get('errlogger')
        self.pinglogger = bot.datas.get('pinglogger')
        self.prefix = bot.command_prefix[0]
        self.eventcogname = bot.datas.get('eventcogname')
        self.embedmgr: embedmgr.EmbedMgr = bot.datas.get('embedmgr')

    def getlistener(self, name):
        listeners = self.bot.get_cog(self.eventcogname).get_listeners()
        listeners_filter = list(filter(lambda x: x[0] == name, listeners))
        if listeners_filter:
            return listeners_filter[0][1]