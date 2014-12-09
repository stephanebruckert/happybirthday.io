from django.shortcuts import get_object_or_404, render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.conf import settings

from datetime import datetime

import facebook
import pprint
import time
import requests
import operator
import urlparse

class Found(Exception):
    pass

pp = pprint.PrettyPrinter(indent=2)

friends = None
wishesCounter = None
words = None
wishesByYear = None
longestWishes = None

yearLabels = None
yearNews = None
yearSames = None
yearLosts = None

def index(request):
    return render_to_response("index.html", {"FACEBOOK_APP_ID": settings.FACEBOOK_APP_ID})

def redirect(request):
    code = request.GET.get("code")
    newUrl = 'https://graph.facebook.com/oauth/access_token?client_id=' \
    +settings.FACEBOOK_APP_ID+'&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fredirect' \
    +'&client_secret='+settings.FACEBOOK_SECRET_KEY+'&code='+code
    r = requests.get(newUrl)
    parsed = urlparse.parse_qsl(r.text)
    request.session["access_token"] = str(parsed[0][1])
    return HttpResponseRedirect(reverse('stats'))


def stats(request):
    # INITS
    context = {}
    wishesCounter = {}
    words = {}
    wishesByYear = {}

    yearLabels = []
    yearNews = []
    yearSames = []
    yearLosts = []
    yearAll = []

    wordLabels = []
    wordCount = []

    graph = facebook.GraphAPI(request.session["access_token"])

    # USER INFO
    picture = graph.get_connections("me", "picture")["url"]
    pp.pprint(picture)
    friends = graph.get_connections("me", "friends", limit=1)
    pp.pprint(friends)
    totalFriends = friends["summary"]["total_count"]
    profile = graph.get_object("me")
    pp.pprint(profile)
    birthday = profile["birthday"]

    # TIME INFO
    conv = time.strptime(birthday, "%m/%d/%Y")
    day = time.strftime("%d", conv)
    month = time.strftime("%m", conv)
    currentYear = datetime.now().year

    # LOOP YEARS
    try:
        while currentYear >= 2004:
            print currentYear
            yearlyBirthdays(request, graph, currentYear, day, month, friends, wishesCounter, words, wishesByYear)
            currentYear -= 1
    except KeyError:
        print "no more birthdays"

    friendsWhoWished = len(friends)

    # WISHES COUNTER
    wishesCounterSorted = sorted(wishesCounter.items(), key=operator.itemgetter(1), reverse=True)[:15]
    wishesGrid = {}
    for user, wishCount in enumerate(wishesCounterSorted):
        pic = graph.get_connections(wishCount[0], "picture", limit=1)
        friendName = friends[wishCount[0]]
        wishesGrid[friendName] = {}
        wishesGrid[friendName]["years"] = wishCount[1]
        wishesGrid[friendName]["url"] = pic["url"]

    # LineChart data
    lineChart = diffByYear(wishesByYear, friends)
    all = 0
    for key, value in lineChart.iteritems():
        yearLabels.append(key)
        yearNews.append(len(value["new"]))
        yearSames.append(len(value["same"]))
        yearLosts.append(len(value["lost"]))
        yearAll.append(len(value["new"]) + len(value["same"]))
        all += len(value["new"]) + len(value["same"])

    # WordChart data
    wordChart = getTopWords(words)
    for key, value in wordChart:
        wordLabels.append(key.encode('utf-8'))
        wordCount.append(value)

    longestWishes = getLongestWishes(wishesByYear, friends)

    context["wishes_grid"] = wishesGrid
    context["diff"] = lineChart
    context["years_charts_labels"] = yearLabels
    context["years_charts_new"] = yearNews
    context["years_charts_same"] = yearSames
    context["years_charts_lost"] = yearLosts
    context["years_charts_all"] = yearAll
    context["picture"] = picture
    context["word_chart"] = wordChart
    context["longest_wishes"] = longestWishes
    context["friends_who_wished"] = friendsWhoWished
    context["word_chart_labels"] = wordLabels
    context["word_chart_count"] = wordCount
    context["total_friends"] = totalFriends
    context["all"] = all

    return render(request, 'stats.html', context)

def yearlyBirthdays(request, graph, currentYear, day, month, friends, wishesCounter, words, wishesByYear):
    wishesByYear[currentYear] = {}
    UTC_14 = 14 * 60 * 60
    UTC_12 = 12 * 60 * 60
    try:
        # Last birthday date
        birthdayDate = datetime(year=currentYear, month=int(month), day=int(day))

        # Timestamp beginning of the day
        birthdayTimestampStart = time.mktime(birthdayDate.timetuple())
        # Day starts 14 hours earlier when in timezone UTC+14
        birthdayTimestampStart -= UTC_14

        # Timestamp end of the day
        birthdayTimestampEnd = birthdayTimestampStart + 24 * 60 * 60
        # Day ends 12 hours later when in timezone UTC-12
        birthdayTimestampEnd += UTC_12

        # Last birthday timestamp
        until = birthdayTimestampEnd
        while True:
            feed = graph.get_connections("me", "feed", until=until, limit=1000)
            i = 0
            for post in feed['data']:
                #if post["type"] != "status":
                #    print post["type"]
                if "message" in post:
                    wishesByYear[currentYear][post["id"]] = {}
                    wishesByYear[currentYear][post["id"]]["user"] = post["from"]["id"]
                    wishesByYear[currentYear][post["id"]]["message"] = post["message"]
                    post_words = post["message"].split()
                    sort_words(words, post_words)
                    if "likes" in post:
                        wishesByYear[currentYear][post["id"]]["likes"] = len(post["likes"]["data"])

                postTimestamp = time.mktime(time.strptime(post['created_time'], '%Y-%m-%dT%H:%M:%S+0000'))

                posterId = post["from"]["id"]
                friends[posterId] = post["from"]["name"]
                if posterId not in wishesCounter.keys():
                    # Insert new friend
                    wishesCounter[posterId] = []
                if currentYear not in wishesCounter[posterId]:
                    # Add wish year by friend
                    wishesCounter[posterId].append(currentYear)

                # Check if last post of the day
                if (postTimestamp <= birthdayTimestampStart):
                    # Must be at the end of the loop
                    raise Found
                i += 1

            nextUrl = feed['paging']['next']
            parsed = urlparse.urlparse(nextUrl)
            until = int(urlparse.parse_qs(parsed.query)['until'][0])
    except Found:
        print i, "birthdays in", currentYear

def sort_words(words, post_words):
    for word in post_words:
        word = word.lower()
        word = ''.join(e for e in word if e.isalnum())
        if len(word) > 2:
            if word in words.keys():
                words[word] += 1
            else:
                words[word] = 1

def diffByYear(wishesByYear, friends):
    diffByYear = {}
    for year in wishesByYear:
        diffByYear[year] = {}
        diffByYear[year]["new"] = {}
        diffByYear[year]["same"] = {}
        diffByYear[year]["lost"] = {}
        for post in wishesByYear[year].values():
            if checkIfUserInArray(post["user"], wishesByYear[year-1]):
                # Friend already posted last year
                diffByYear[year]["same"][post["user"]] = friends[post["user"]]
            else:
                # Friend didn't post last year
                diffByYear[year]["new"][post["user"]] = friends[post["user"]]
        if year-1 in wishesByYear:
            for post in wishesByYear[year-1].values():
                # Friend posted last year but not this year
                if not checkIfUserInArray(post["user"], wishesByYear[year]):
                    diffByYear[year]["lost"][post["user"]] = friends[post["user"]]
    return diffByYear

def checkIfUserInArray(user, array):
    for post in array.values():
        if user == post["user"]:
            return True
    return False

def getLongestWishes(wishesByYear, friends):
    longestWishes = {}
    for year in wishesByYear:
        for post in wishesByYear[year]:
            longestWishes[post] = {}
            longestWishes[post]["len"] = len(wishesByYear[year][post]["message"])
            longestWishes[post]["message"] = wishesByYear[year][post]["message"]
            longestWishes[post]["user"] = friends[wishesByYear[year][post]["user"]]
            longestWishes[post]["year"] = year
    sortedLongestWishes = sorted(longestWishes.items(), key=operator.itemgetter(1), reverse=True)[:15]
    return sortedLongestWishes

def getTopWords(words):
    return sorted(words.items(), key=operator.itemgetter(1), reverse=True)[:20]