#!/usr/bin/env python
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

import redditbots
import reddit
import logging
import argparse
import sys
import urllib2
import time

def main(args):
    parser = argparse.ArgumentParser(description='Test a redditbot')
    parser.add_argument('file', type=file, help='file to use')
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--username', type=str, help='username to run with')
    parser.add_argument('--password', type=str, help='password to run with')

    options = parser.parse_args(args[1:])
    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    class TestBox(redditbots.TestingSandbox):
        def username(self):
            return options.username
        def password(self):
            return options.password

    botManager = redditbots.BotManager(TestBox)
    botManager.loadBot(options.file)
    botManager.triggerInit()

    r = botManager.getReddit()

    try:
        r_all = r.get_subreddit('all').get_new_by_date()

        print "Processing new submissions in /r/all"
        for post in r_all:
            botManager.triggerNewSubmission(post)

        print "Processing new comments"
        for comment in r.get_all_comments():
            botManager.triggerNewComment(comment)

        while botManager.processReplyQueue():
            time.sleep(5*60)
            pass
    except urllib2.URLError, e:
        print "Network error:", e

if __name__ == "__main__":
    main(sys.argv)
