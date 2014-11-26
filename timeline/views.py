from django.shortcuts import get_object_or_404, render
import facebook
import pprint
import urlparse
import time
from datetime import datetime

class Found(Exception): pass

graph = facebook.GraphAPI("CAACEdEose0cBADUU9iuXTDKlOPQLPUyAwC3SYClOI5hcPvQnrae26ZCHMgaX8XfAOpEiebWJeYpODM57t7QNCXoBQkov9Hbi0Q9YLOS1ftZAubVGcBG22P1ZBZBfjKHF3HiAt9gWsbgCh4iGx0l1qmPoFKBxqNuKl5nIVpMmPeyqh9ZAGnJ4aXTi4hjbu0TeMZCCH9pJ9HYe0ZCMfmqtBtj")

def index(request):

    birthday = "11/04/1990"
    conv = time.strptime(birthday,"%m/%d/%Y")
    day = time.strftime("%d", conv)
    month = time.strftime("%m", conv)
    currentYear = datetime.now().year
    try:
        while currentYear > 2004:
            yearlyBirthdays(currentYear, day, month)
            currentYear = currentYear - 1
    except KeyError:
        print "error paging"

    return render(request, 'index.html', {})

def yearlyBirthdays(currentYear, day, month):
    try:
        # Last birthday date
        birthdayDate = datetime(year=currentYear, month=int(month), day=int(day))
        birthdayTimestampStart = time.mktime(birthdayDate.timetuple())
        birthdayTimestampEnd = birthdayTimestampStart + 24 * 60 * 60
        print birthdayTimestampEnd
        # Last birthday timestamp
        until = birthdayTimestampEnd

        while True:
            feed = graph.get_connections("me", "feed", until=until, limit=1000)
            pp = pprint.PrettyPrinter(indent=2)
            i = 0
            for post in feed['data']:
                postTimestamp = time.mktime(time.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S+0000'))
                if (postTimestamp < birthdayTimestampStart):
                    raise Found
                pp.pprint(post['created_time'])
                i = i + 1

            nextUrl = feed['paging']['next']
            parsed = urlparse.urlparse(nextUrl)
            until = int(urlparse.parse_qs(parsed.query)['until'][0])
            print until
    except Found:
        print i, "birthdays in", currentYear