#!/usr/bin/env python

import cgi
import re
import string

from collections import defaultdict, namedtuple
from sortedcontainers import SortedSet

class User(object):
    def __init__(self, name=None, id=None):
        self.name = cgi.escape(name) if name else id
        self.id = convertSteamIDtoCommunityID(id)

steamProfileURLprefix = 'https://steamcommunity.com/profiles/%s'

REGEXP_NEW = re.compile(r'U:[0-9]:[0-9]+')
REGEXP_OLD = re.compile('STEAM_[0-9]:[0-9]:[0-9]+')

htmlStart = """Content-type: text/html; charset=utf-8

<html>
<head>
    <title>source-status-linker</title>
    <style type="text/css">
        A {
            color: #d16016;
            font-family: sans-serif;
            font-weight: bold;
        }
        BODY {
            color: white;
            font-family: sans-serif;
            font-weight: bold;
        }
    </style>
</head>
<body bgcolor="black" font="sans-serif">
"""

tableStart = "<table><tr>"
cellStart = "<td valign=\"top\" style=\"padding: 2em;\">"
cellEnd = "</td>"
tableEnd = "</tr></table>"

formHTML = """<form action="https://google.com/search"><input type="text" name="q"><br><input type="submit" value="Google Search"></form><br><br>
    <form method="post">
        Paste status output:<input type="submit"><br>
        <textarea name="data" rows="20" cols="80"></textarea>
    </form>"""

htmlEnd = """</body>
</html>"""

def groupUsers(users):
    def makeSet():
        return SortedSet(key=lambda user: user.name.upper())

    groups = defaultdict(makeSet)

    for user in users:
        group = user.name[0].upper()
        if group not in string.ascii_uppercase:
            try:
                if int(group) in range(10):
                    group = '0'
            except:
                group = '_'

        groups[group].add(user)

    return groups

def oldToNew(steamID):
    _, universe, steamID = steamID.split(':')

    return "U:%s:%i" % (universe, int(steamID) * 2 + int(universe))

def convertSteamIDtoCommunityID(steamID):
    constant = 76561197960265728

    if "STEAM_" in steamID:
        steamID = oldToNew(steamID)

    _, universe, authID = steamID.split(':')
    communityID = (int(authID)) + constant

    return communityID

def formatUser(user):
    global steamProfileURLprefix

    return "<a href=\"%s\">%s</a><br>" % (
        steamProfileURLprefix % user.id,
        user.name)

# ** Main
form = cgi.FieldStorage()
data = form.getvalue("data", None)

if data:
    # *** Form submitted

    data = data.split("\n")
    users = []

    for line in data:

        if line.startswith('#'):
            ID = REGEXP_NEW.findall(line)

            if ID:
                ID = ID[0]
                name = re.search('"(.*)"', line)
                if name:
                    name = name.group(1)

                users.append(User(name, ID))

        else:
            IDs = REGEXP_NEW.findall(line) + REGEXP_OLD.findall(line)

            for i in IDs:
                users.append(User(None, i))

    if not users:
        # **** No users found
        print htmlStart
        print formHTML
        print htmlEnd

    elif len(users) == 1:
        # **** One user found
        print "Location: %s\n" % (steamProfileURLprefix % users[0].id)

    else:
        # **** Multiple users found

        alphabetGroups = [['A', 'B', 'C', 'D', 'E', 'F'],
                          ['G', 'H', 'I', 'J', 'K', 'L'],
                          ['M', 'N', 'O', 'P', 'Q', 'R'],
                          ['S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']]

        userGroups = groupUsers(users)

        print htmlStart
        print tableStart
        print cellStart

        # Print non-letter names
        if userGroups['_']:
            print "<br>%s<br><hr>" % '_'
            for user in userGroups['_']:
                print formatUser(user)

        # Print numbered names
        print "<br>%s<br><hr>" % '0'
        for user in userGroups['0']:
            print formatUser(user)

        # Print alphabetical names
        for letterGroup in alphabetGroups:
            print cellStart

            for letter in letterGroup:
                if letter in userGroups:
                    print "<br>%s<br><hr>" % letter
                    for user in userGroups[letter]:
                        print formatUser(user)

            print cellEnd

        print tableEnd
        print htmlEnd

else:
    # *** No form submitted
    print htmlStart
    print formHTML
    print htmlEnd
