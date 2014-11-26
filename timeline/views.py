from django.shortcuts import get_object_or_404, render
import facebook
import pprint
import urlparse
import time
import operator

from datetime import datetime

class Found(Exception): pass

graph = facebook.GraphAPI("CAACEdEose0cBAPho1gB2CUgJjON8xXR9AkA3ybR1RXU3A8f5bQoAtYZBuyPk7U8MvWahNozVDavQSe4J0tGviEL2t0BWqnUpY3cI4RErrMcAQqQtawQWxrapaZCxydciWtZB6r2bbDjnkb67QBo9Hna5Q3xYx213hayoThNJnG2v2ucStofG3NPtYwb0Ex6BI4p4M1iJfJ465ZBnm25N")
pp = pprint.PrettyPrinter(indent=2)
friends = {}
wishesCounter = {}

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
        print "no more birthdays"

    pp.pprint(friends)
    print(len(friends))

    wishesCounterSorted = sorted(wishesCounter.items(), key=operator.itemgetter(1))
    pp.pprint(wishesCounterSorted)

    for user, wishCount in enumerate(wishesCounterSorted):
        print user
        print wishCount
        print friends[wishesCounterSorted[user]], wishCount

    return render(request, 'index.html', {})

def yearlyBirthdays(currentYear, day, month):
    try:
        # Last birthday date
        birthdayDate = datetime(year=currentYear, month=int(month), day=int(day))
        birthdayTimestampStart = time.mktime(birthdayDate.timetuple())
        birthdayTimestampEnd = birthdayTimestampStart + 24 * 60 * 60

        # Last birthday timestamp
        until = birthdayTimestampEnd

        while True:
            feed = graph.get_connections("me", "feed", until=until, limit=1000)
            i = 0
            for post in feed['data']:
                postTimestamp = time.mktime(time.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S+0000'))
                if (postTimestamp < birthdayTimestampStart):
                    raise Found
                posterId = post["from"]["id"]
                friends[posterId] = post["from"]["name"]
                if posterId in wishesCounter.keys():
                    wishesCounter[posterId] += 1
                else:
                    wishesCounter[posterId] = 1
                i = i + 1

            nextUrl = feed['paging']['next']
            parsed = urlparse.urlparse(nextUrl)
            until = int(urlparse.parse_qs(parsed.query)['until'][0])
    except Found:
        print i, "birthdays in", currentYear