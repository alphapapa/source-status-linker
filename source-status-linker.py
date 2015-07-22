#!/usr/bin/env python

# * source-status-linker.py
# ** Imports

import datetime
import cgi
import re
import string

from collections import defaultdict, namedtuple
from sortedcontainers import SortedSet

# ** Classes
class User(object):
    def __init__(self, name=None, id=None):
        self.name = cgi.escape(name) if name else id
        self.id = convertSteamIDtoCommunityID(id)

# ** Constants
steamProfileURLprefix = 'https://steamcommunity.com/profiles/%s'

REGEXP_NEW = re.compile(r'U:[0-9]:[0-9]+')
REGEXP_OLD = re.compile('STEAM_[0-9]:[0-9]:[0-9]+')

htmlStart = """Content-type: text/html; charset=utf-8

<html>
<head>
    <title>source-status-linker</title>
    <style type="text/css">
        @font-face {
            font-family: 'TF2 Build';
            font-style: normal;
            font-weight: normal;
            src: local('TF2 Build'), url('tf2build.woff') format('woff');
        }
        @font-face {
            font-family: 'TF2 Secondary';
            font-style: normal;
            font-weight: normal;
            src: local('TF2 Secondary'), url('tf2secondary.woff') format('woff');
        }
        A {
            color: #b65a1a;
            font-family: sans-serif;
            font-weight: bold;
        }
        BODY {
            background: #3b3833;
            color: #ede5ce;
            font-family: TF2 Secondary, sans-serif;
            font-size: 150%;
            font-weight: bold;
            margin: 2em;
        }
        INPUT {
            background: #a89a7f;
            border: solid;
            border-color: #a89a7f;
            border-radius: 8px;
            color: #ede5ce;
            font-family: TF2 Build;
            font-size: 100%;
            margin: 0.25em;
            padding: 0.25em;
        }
        TEXTAREA {
            background: #7c7268;
            color: #ede5ce;
        }
        .header {
            font-size: 150%;
            font-family: TF2 Build;
            font-weight: bold;
        }
        .title {
            font-family: TF2 Build;
            font-size: 150%;
        }
        .username {
            font-family: Verdana;
        }
    </style>
</head>
<body bgcolor="black" font="sans-serif">
"""

tableStart = "<table>"
rowStart = "<tr>"
rowEnd = "</tr>"
cellStart = "<td valign=\"top\" style=\"padding: 1em;\">"
cellEnd = "</td>"
tableEnd = "</table>"

googleHTML = """<span class="title">Google</span><br><form action="https://google.com/search"><input type="text" name="q"><br><input type="submit" value="Google Search"></form>"""

warshipsHTML = """<span class="title">World of Warships players</span><br><form action="http://worldofwarships.com/community/accounts/search/"><input type="text" name="search"><br><input type="submit" value="Search"></form>"""

formHTML = """<form method="post">
        <span class="title">Paste status output:</span><input type="submit" style="margin-left: 1em;"><br>
        <textarea name="data" rows="20" cols="80"></textarea>
    </form>"""

htmlEnd = """</body>
</html>"""

# ** Functions
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

def formatHeader(name, data=''):
    if data:
        data = """ <span style="font-size: 150%%">%s</span>""" % data

    return """<br><span class="header">%s:</span>%s""" % (name, data)

def formatLetterHeader(letter):
    return """<span class="header">%s</span><hr>""" % letter

def formatUser(user):
    global steamProfileURLprefix

    return """<a href="%s" class="username">%s</a><br>""" % (
        steamProfileURLprefix % user.id,
        user.name)

# ** Main
form = cgi.FieldStorage()
data = form.getvalue("data", None)

if data:
    # *** Form submitted

    data = data.split("\n")
    users = []

    hostname = None
    address = None
    mapName = None

    for line in data:

        if line.startswith('hostname'):
            # Get hostname
            hostname = line.split(':')[1].strip()

        elif line.startswith('udp'):
            # Get IP address
            address = line.split(':')[1].strip()

        elif line.startswith('map'):
            # Get map
            mapName = line.split(':')[1].split()[0].strip()

        elif line.startswith('#'):
            ID = REGEXP_NEW.findall(line) or REGEXP_OLD.findall(line)

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

        date = datetime.datetime.utcnow().strftime("%A, %d %B %Y %H:%M") + " UTC"

        alphabetGroups = [['A', 'B', 'C', 'D', 'E', 'F'],
                          ['G', 'H', 'I', 'J', 'K', 'L'],
                          ['M', 'N', 'O', 'P', 'Q', 'R'],
                          ['S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']]

        userGroups = groupUsers(users)

        print htmlStart
        print googleHTML
        print warshipsHTML

        # Print header info
        print tableStart
        print rowStart
        print cellStart

        print formatHeader('date', date)

        if hostname:
            print formatHeader('hostname', hostname)

        if address:
            print formatHeader('address', address)

        if mapName:
            print formatHeader('map', mapName)

        print cellEnd
        print rowEnd
        print tableEnd

        print tableStart
        print rowStart

        if userGroups['_'] or userGroups['0']:
            groups = ['_', '0']

            print cellStart

            for g in groups:
                if userGroups[g]:
                    print formatLetterHeader(g)
                    for user in userGroups[g]:
                        print formatUser(user)
                    print "<br><br>"

            print cellEnd

        # Print alphabetical names
        for letterGroup in alphabetGroups:
            print cellStart

            for letter in letterGroup:
                if letter in userGroups:
                    print formatLetterHeader(letter)
                    for user in userGroups[letter]:
                        print formatUser(user)
                    print "<br><br>"

            print cellEnd

        print rowEnd
        print tableEnd

        print htmlEnd

else:
    # *** No form submitted
    print htmlStart
    print googleHTML
    print warshipsHTML
    print formHTML
    print htmlEnd
