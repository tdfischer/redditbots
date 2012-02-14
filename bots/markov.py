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
import random
import time

class MarkovBot(redditbots.Bot):
    def onDBOpen(self, db, curVersion):
        if curVersion == 0:
            db.execute('CREATE TABLE markov (word TEXT KEY, nextWord TEXT KEY, frequency INTEGER)')
            db.execute('CREATE UNIQUE INDEX wordPair ON markov (word, nextWord)')
        db.commit()
        return 1

    def addPair(self, first, second):
        c = self.database.cursor()
        if (first is None):
            c.execute("SELECT frequency FROM Markov WHERE word IS NULL and nextWord = ?", (second,))
        elif (second is None):
            c.execute("SELECT frequency FROM Markov WHERE word = ? AND nextWord IS NULL", (first,))
        else:
            c.execute("SELECT frequency FROM Markov WHERE word = ? AND nextWord = ?", (first, second))
        res = c.fetchone()
        if (res == None):
            c.execute("INSERT INTO Markov (word, nextWord, frequency) VALUES (?, ?, 0)", (first, second))
            self.database.commit()
        if (first is None):
            c.execute("UPDATE Markov SET frequency = frequency+1 WHERE word IS NULL AND nextWord = ?", (second,))
        elif (second is None):
            c.execute("UPDATE Markov SET frequency = frequency+1 WHERE word = ? AND nextWord IS NULL", (first,))
        else:
            c.execute("UPDATE Markov SET frequency = frequency + 1 WHERE word = ? AND nextWord = ?", (first, second))
        self.database.commit()

    def nextWord(self, current):
        c = self.database.cursor()
        if (current is None):
            c.execute("SELECT nextWord FROM Markov WHERE word IS NULL ORDER BY RANDOM() * frequency LIMIT 1")
        else:
            c.execute("SELECT nextWord FROM Markov WHERE word = ? ORDER BY RANDOM() * frequency LIMIT 1", (current,))
        res = c.fetchone()
        if (res == None):
            return None
        return res[0]
        
    def buildReply(self, word):
        if (word != None):
            phrase = (word,)
        else:
            phrase = ()
        current = self.nextWord(word)
        while(current != None):
            phrase += (current,)
            current = self.nextWord(current)
        return ' '.join(phrase)

    def onNewComment(self, comment):
        words = comment.body.split(' ')
        prev = None
        for next in words:
            self.addPair(prev, next)
            prev = next
        self.addPair(prev, None)

        if random.randint(0, 100) < 10:
            tries = 10
            randomWord = random.choice(words)
            reply = self.buildReply(randomWord)
            while tries > 0 and len(randomWord) > 6 and len(reply) > 30:
                tries = tries-1
                randomWord = random.choice(words)
                reply = self.buildReply(randomWord)
            if tries > 0:
                print comment.body,'->',reply
                self.queueReply(comment, reply)
