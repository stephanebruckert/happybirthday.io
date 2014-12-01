from django.shortcuts import get_object_or_404, render
import facebook
import pprint
import urlparse
import time
import operator

from datetime import datetime

class Found(Exception): pass

graph = facebook.GraphAPI("CAACEdEose0cBACT6lHAMZCjnJh1B0b6zvxFXOrh2Y0CNnZAtQQSrizc7SbkudLUcrgb97fNmDgz2qS9ekAf4rnRmrAFLnEpkLZBpsvjPfRgrualEvg0MWZAGprf9SPJN4MLNrJAEc01BfJSTcehNI1a8f0AgyCFOVUyuEuWpGlYpJ9fFifDIF3ZBxqZBnywcSbZAUwM5qOogDsBIZAKI6Coi")
pp = pprint.PrettyPrinter(indent=2)


def index(request):
    birthday = "11/04/1990"
    conv = time.strptime(birthday,"%m/%d/%Y")
    day = time.strftime("%d", conv)
    month = time.strftime("%m", conv)
    currentYear = datetime.now().year

    friends = {}
    wishesCounter = {}
    words = {}
    wishesByYear = {}

    try:
        while currentYear > 2004:
            yearlyBirthdays(currentYear, day, month, friends, wishesCounter, words, wishesByYear)
            currentYear -= 1
    except KeyError:
        print "no more birthdays"

    print(len(friends), "friends wished you HB")

    wishesCounterSorted = sorted(wishesCounter.items(), key=operator.itemgetter(1))

    for user, wishCount in enumerate(wishesCounterSorted):
        print friends[wishCount[0]], wishCount[1]

    wordsSorted = sorted(words.items(), key=operator.itemgetter(1))

    pp.pprint(wordsSorted)
    pp.pprint(wishesByYear)
    pp.pprint(diffByYear(wishesByYear))
    return render(request, 'index.html', {"words": wordsSorted, "wishes": wishesCounterSorted, "diff": diffByYear(wishesByYear)})

def yearlyBirthdays(currentYear, day, month, friends, wishesCounter, words, wishesByYear):
    wishesByYear[currentYear] = {}
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
                if post["type"] != "status":
                    print post["type"]
                if "message" in post:
                    print post["message"]
                    post_words = post["message"].split()
                    sort_words(words, post_words)
                if "likes" in post:
                    if len(post["likes"]["data"]) > 2:
                        print len(post["likes"]["data"]), "likes"
                postTimestamp = time.mktime(time.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S+0000'))
                if (postTimestamp < birthdayTimestampStart):
                    raise Found
                posterId = post["from"]["id"]
                friends[posterId] = post["from"]["name"]
                if posterId in wishesCounter.keys():
                    wishesCounter[posterId] += 1
                else:
                    wishesCounter[posterId] = 1
                i += 1
                wishesByYear[currentYear][post["from"]["id"]] = post["from"]

            nextUrl = feed['paging']['next']
            parsed = urlparse.urlparse(nextUrl)
            until = int(urlparse.parse_qs(parsed.query)['until'][0])
    except Found:
        print i, "birthdays in", currentYear

def sort_words(words, post_words):
    for word in post_words:
        if word in words.keys():
            words[word] += 1
        else:
            words[word] = 1

def diffByYear(wishesByYear):
    diffByYear = {}
    for year in wishesByYear:
        diffByYear[year] = {}
        diffByYear[year]["new"] = {}
        diffByYear[year]["same"] = {}
        diffByYear[year]["lost"] = {}
        for friend in wishesByYear[year]:
            # Friend already posted last year
            if friend in wishesByYear[year-1].keys():
                diffByYear[year]["same"][friend] = wishesByYear[year][friend]
            # Friend didn't post last year
            else:
                diffByYear[year]["new"][friend] = wishesByYear[year][friend]
        if year-1 in wishesByYear:
            for friend in wishesByYear[year-1]:
                # Friend posted last year but not this year
                if friend not in wishesByYear[year].keys():
                    diffByYear[year]["lost"][friend] = wishesByYear[year-1][friend]

    return diffByYear

