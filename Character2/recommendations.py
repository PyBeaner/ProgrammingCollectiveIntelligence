#! encoding=utf8
from math import sqrt

critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
                         'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
                         'The Night Listener': 3.0},
           'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,
                            'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 3.5},
           'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
                                'Superman Returns': 3.5, 'The Night Listener': 4.0},
           'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
                            'The Night Listener': 4.5, 'Superman Returns': 4.0,
                            'You, Me and Dupree': 2.5},
           'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                            'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
                            'You, Me and Dupree': 2.0},
           'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
                             'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
           'Toby': {'Snakes on a Plane': 4.5, 'You, Me and Dupree': 1.0, 'Superman Returns': 4.0}}


# returns person1 and person2's 欧几里得距离
def sim_distance(prefs, person1, person2):
    # shared items
    si = {}
    for item in prefs[person1]:
        si[item] = 1

    if (len(si) == 0): return 0

    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                          for item in prefs[person1] if item in prefs[person2]])

    return 1 / (1 + sqrt(sum_of_squares))


# returns p1 and p2's 皮尔逊相关系数
def sim_pearson(prefs, p1, p2):
    # share items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]: si[item] = 1

    n = len(si)
    if (n == 0): return 1

    sum1 = sum([prefs[p1][item] for item in si])
    sum2 = sum([prefs[p2][item] for item in si])

    sum1Sq = sum([pow(prefs[p1][item], 2) for item in si])
    sum2Sq = sum([pow(prefs[p2][item], 2) for item in si])

    pSum = sum([prefs[p1][item] * prefs[p2][item] for item in si])

    num = pSum - (sum1 * sum2 / n)
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0: return 0
    r = num / den
    return r

def topMatches(prefs,person,n=5,similarity=sim_pearson):
    scores = [(similarity(prefs,person,other),other) for other in prefs if other!=person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

def getRecommendations(prefs,person,similarity=sim_pearson):
    totals = {}
    simSums = {}
    for other in prefs:
        if other==person:continue
        sim = similarity(prefs,person,other)
        if sim<=0:continue

        for item in prefs[other]:
            if item not in prefs[person] or prefs[person][item]==0:
                totals.setdefault(item,0)
                totals[item]+=prefs[other][item]*sim
                simSums.setdefault(item,0)
                simSums[item] += sim

    rankings = [(total/simSums[item],item) for item ,total in totals.items()]
    rankings.sort()
    rankings.reverse()
    return rankings


if (__name__ == "__main__"):
    r = sim_distance(critics, "Lisa Rose", "Gene Seymour")
    print(r)

    r2 = sim_pearson(critics,"Lisa Rose", "Gene Seymour")
    print(r2)

    print("calculating the top matches(Pearson):")
    r3 = topMatches(critics,person="Lisa Rose")
    print(r3)

    print("calculating the top matches(欧几里得):")
    r3 = topMatches(critics,"Lisa Rose",5,sim_distance)
    print(r3)

    print("getting recommendation")
    r4 = getRecommendations(critics,"Toby",sim_pearson)
    print(r4)
