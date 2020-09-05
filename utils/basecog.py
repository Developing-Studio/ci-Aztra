import aiomysql
import logging
from discord.ext import commands
from . import msglogger, checks, aztra, emojictrl, datamgr, embedmgr
import sqlite3

class BaseCog(commands.Cog):
    def __init__(self, bot: aztra.Aztra):
        self.bot = bot
        self.config = bot.get_data('config')
        self.color = bot.get_data('color')
        self.emj: emojictrl.Emoji = bot.get_data('emojictrl')
        self.msglog: msglogger.Msglog = bot.get_data('msglog')
        self.logger: logging.Logger = bot.get_data('logger')
        self.pool: aiomysql.Connection = bot.get_data('pool')
        self.check: checks.Checks = bot.get_data('check')
        self.errlogger = bot.get_data('errlogger')
        self.pinglogger = bot.get_data('pinglogger')
        self.datadb: datamgr.DataDB = bot.get_data('datadb')
        self.awaiter = bot.get_data('awaiter')
        self.prefix = bot.command_prefix[0]
        self.eventcogname = bot.get_data('eventcogname')
        self.embedmgr: embedmgr.EmbedMgr = bot.get_data('embedmgr')

    def getlistener(self, name):
        listeners = self.bot.get_cog(self.eventcogname).get_listeners()
        listeners_filter = list(filter(lambda x: x[0] == name, listeners))
        if listeners_filter:
            return listeners_filter[0][1]