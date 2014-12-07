from django.shortcuts import get_object_or_404, render
import facebook
import pprint
import urlparse
import time
import operator

from datetime import datetime

class Found(Exception): pass

graph = facebook.GraphAPI("CAACEdEose0cBAJ0HujOb2On8yhi9Ah88mL5ruYi68AsB3fQfFZAWLwysGSgjGXRXIAMhZB1ylgJwZBZCu9XZBSpF5vORKeKZBZBy4bD6a7WQBUaL3nvMn5aPeWA3XdGUbsb1YBOp64g0K8KOqZBzLWaqPl72DjVeOCArH1SWtXJA1SDPoonRqYieMR0JxgVB8IxeiaZBTG3fZAAPVntOi9gKBK")
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

    yearLabels = []
    yearNews = []
    yearSames = []
    yearLosts = []

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

    lineChart = diffByYear(wishesByYear)
    for key, value in lineChart.iteritems():
        yearLabels.append(key)
        yearNews.append(len(value["new"]))
        yearSames.append(len(value["same"]))
        yearLosts.append(len(value["lost"]))

    pp.pprint(lineChart)
    pp.pprint(wordsSorted)
    pp.pprint(wishesByYear)
    pp.pprint(diffByYear(wishesByYear))

    context = {"words": wordsSorted, "wishes": wishesCounterSorted, "diff": lineChart,
               "years_charts_labels": yearLabels, "years_charts_new": yearNews, "years_charts_same": yearSames,
               "years_charts_lost": yearLosts}

    return render(request, 'index.html', context)


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

