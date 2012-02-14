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

import logging

class Bot(object):
    def __init__(self, sandbox):
        super(Bot, self).__init__()
        self.log = logging.getLogger("redditbot.Bots.%s"%(self.__class__.__name__))
        self.__sbox = sandbox

    def login(self):
        self.__sbox.login()

    @property
    def database(self):
        return self.__sbox.database

    def queueReply(self, post, text):
        self.__sbox.queueReply(post, text)

    def onInit(self):
        pass

    def onNewSubmission(self, post):
        pass

    def onNewComment(self, comment):
        pass

    def queueAction(self, action):
        pass

    def onDBOpen(self, db, version):
        return version
