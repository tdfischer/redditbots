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

from RestrictedPython import compile_restricted
from RestrictedPython.Guards import safe_builtins
import sys
from bot import Bot
import reddit
import sqlite3

class BotSandbox(object):
    def __init__(self, manager):
        super(BotSandbox, self).__init__()
        self._globals = self.defaultGlobals()
        self._import = __import__
        self._bot = None
        self._manager = manager

    def defaultGlobals(self):
        globs = dict(__builtins__ = safe_builtins)
        globs['dict'] = dict
        return globs

    def _getattr(self, obj, name, default = None):
        return getattr(obj, name, default)

    def username(self):
        raise NotImplementedError

    def password(self):
        raise NotImplementedError

    def _loadBot(self):
        for klass in self.getGlobals().values():
            if type(klass) == type:
                if issubclass(klass, Bot) and not (klass is Bot):
                    self._bot = klass()
                    self._bot.login = self.login
                    self._bot.getDatabase = self.getDatabase

    def getDatabase(self):
        db = self._manager.getBotDB(self)
        c = db.execute("PRAGMA user_version")
        version = c.fetchone()[0]
        newVersion = self._bot.onDBOpen(db, version)
        db.execute("PRAGMA user_version=%i"%(newVersion))
        return db

    def login(self):
        self._manager.loginBot(self)

    def getBot(self):
        if (self._bot is None):
            self._loadBot()
        return self._bot

    def _printer(self):
        return sys.stdout

    def setGlobal(self, *args):
        cur = self._globals
        for a in args[0:-2]:
            if not (a in cur):
                cur[a] = {}
            cur = cur.__getitem__(a)
        cur.__setitem__(args[-2], args[-1])

    def getGlobals(self):
        return self._globals

    def compile(self, code, filename, mode):
        return compile_restricted(code, filename, mode)

    def eval(self, code):
        botGlobals = self._globals.copy()
        botGlobals['__name__'] = code.co_name
        self._globals['__name__'] = code.co_name
        self._globals['_getattr_'] = self._getattr
        self._globals['_print_'] = self._printer
        self._globals['__builtins__']['__import__'] = self._import
        exec(code) in self._globals

class TestingSandbox(BotSandbox):
    def defaultGlobals(self):
        return globals()

    def compile(self, code, filename, mode):
        return compile(code, filename, mode)
