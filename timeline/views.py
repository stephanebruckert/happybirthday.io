from django.shortcuts import get_object_or_404, render
import facebook
import pprint
import urlparse
import time
import operator

from datetime import datetime

class Found(Exception):
    pass

graph = facebook.GraphAPI("CAACEdEose0cBAGC048VzZATPsJstiHbuuQNVC6cxZCCMWrSZCv3kedSZBaGOzxFjvTZBZA8JFqDqgJJzKI4bJ8yAvybMmrrZCcwHnUSAUkdutp5ZB2h6dn28DsfP5VtbSSfwwTeaNHsZBvy3fSEq29l5t5do9GFf1rSCTilKTLA4y3amF6bXWqgabdfN3U1eqAIhPivcoxhnb7XX3WvipIeZAG")
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
    # INITS
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

    # USER INFO
    picture = (graph.get_connections("me", "picture"))["url"]
    friends = graph.get_connections("me", "friends", limit=1)
    totalFriends = friends["summary"]["total_count"]
    profile = graph.get_object("me")
    birthday = profile["birthday"]

    # TIME INFO
    conv = time.strptime(birthday, "%m/%d/%Y")
    day = time.strftime("%d", conv)
    month = time.strftime("%m", conv)
    currentYear = datetime.now().year

    # LOOP YEARS
    try:
        while currentYear >= 2004:

            yearlyBirthdays(currentYear, day, month, friends, wishesCounter, words, wishesByYear)
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
    pp.pprint(wishesGrid)

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

    context = {"wishes_grid": wishesGrid, "diff": lineChart,
               "years_charts_labels": yearLabels, "years_charts_new": yearNews, "years_charts_same": yearSames,
               "years_charts_lost": yearLosts, "years_charts_all": yearAll, "picture": picture, "word_chart": wordChart,
               "longest_wishes": longestWishes, "friends_who_wished": friendsWhoWished, "word_chart_labels": wordLabels,
               "word_chart_count": wordCount, "total_friends": totalFriends, "all": all}
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

