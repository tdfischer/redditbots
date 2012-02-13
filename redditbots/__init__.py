# Copyright (c) 2012 by Trever Fischer <tdfischer@fedoraproject.org>
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#

import reddit
import logging
import sys
from sandbox import *
from bot import Bot

__all__ = ["Bot", "BotManager", "BotSandbox", "TestingSandbox"]

class LoggingMixin(object):
    def __init__(self, name=None):
        if name is None:
            name = self.__class__.__name__
        self._log = logging.getLogger(name)

class BotManager(object):
    def __init__(self, sandbox=BotSandbox):
        super(BotManager, self).__init__()
        self._log = logging.getLogger("redditbot.BotManager")
        self._sbox = sandbox
        self.__bots = []
        self.__currentLogin = None
        self._reddit = reddit.Reddit(user_agent='redditbots/0.1')
        self.__dbs = {}

    def getReddit(self):
        return self._reddit

    def loginBot(self, bot):
        if (self.__currentLogin is bot):
            return
        print "Logging in again"
        self._reddit.login(bot.username(), bot.password())
        self.__currentLogin = bot

    def getBotDB(self, bot):
        if not (bot in self.__dbs):
            self.__dbs[bot] = sqlite3.connect("/tmp/%s.sqlite3"%(bot.getBot().__class__.__name__))
        return self.__dbs[bot]

    def __genHook(hookName):
        def f(self, *args, **kwargs):
            self.runHook(hookName, *args, **kwargs)
        f.__doc__ = "Convienence method for runHook(%s)"%(hookName)
        return f

    def addBot(self, bot):
        self._log.debug("Registering bot %s", bot)
        self.__bots.append(bot)

    def loadBot(self, stream):
        self._log.debug("Loading bot from %s", stream.name)
        sbox = self._sbox(self)
        code = stream.read()
        code = sbox.compile(code, stream.name, 'exec')
        sbox.eval(code)
        self.addBot(sbox)

    triggerNewSubmission = __genHook('newSubmission')
    triggerNewComment = __genHook('newComment')

    def runHook(self, hookName, *args, **kwargs):
        """Runs a hook"""
        hookName = "on"+hookName[0].upper()+hookName[1:]
        for bot in self.__bots:
            self._log.debug("Running hook %s on %s", hookName, bot.getBot())
            if hasattr(bot.getBot(), hookName):
                handler = getattr(bot.getBot(), hookName)
                handler(*args, **kwargs)
