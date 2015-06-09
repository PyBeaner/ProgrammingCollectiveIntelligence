import time
import random
import math

people = [
    ("Seymour","BOS"),
    ("Franny","DAL"),
    ("Zooey","CAK"),
    ("Walt","MIA"),
    ("Buddy","ORD"),
    ("Les","OMA"),
]

# LaGuardia airport in New York
destination = "LGA"

flights = {}
#
for line in open("schedule.txt").readlines():
    origin,dest,depart,arrive,price = line.strip().split(",")
    flights.setdefault((origin,dest),[])

    # add
    flights[(origin,dest)].append((depart,arrive,int(price)))

def getminutes(t):
    x = time.strptime(t,"%H:%M")
    return x[3]*60+x[4]

# a list numbers represent their choices
# [1,4,3,2,7,3,6,3,2,4,5,3] # twice the number of people(outbound and return flights)
# represent a nice table of someone's schedule
def printschedule(r):
    for d in range(int(len(r)/2)):
        name = people[d][0]
        origin = people[d][1]
        out = flights[(origin,destination)][r[d]]
        ret = flights[(destination,origin)][r[d+1]]
        print("%10s%10s %5s-%5s $%3s %5s-%5s $%3s" % (name,origin,out[0],out[1],out[2], ret[0],ret[1],ret[2]))

def schedulecost(sol):
    totalprice = 0
    latestarrival = 0
    earliestdep = 24*60
    totalwait = 0

    for d in range(int(len(sol)/2)):
        origin = people[d][1]
        outbound = flights[(origin,destination)][sol[2*d]]
        returnf = flights[(destination,origin)][sol[2*d+1]]

        # total cost(in and out)
        totalprice += outbound[2]+returnf[2]
        arrivial = getminutes(outbound[1])
        if arrivial>latestarrival:latestarrival=arrivial
        depart = getminutes(returnf[0])
        if depart<earliestdep:earliestdep=depart

    for d in range(int(len(sol)/2)):
        origin = people[d][1]
        outbound = flights[(origin,destination)][sol[2*d]]
        returnf = flights[(destination,origin)][sol[2*d+1]]

        totalwait+=latestarrival-getminutes(outbound[1])
        totalwait+=getminutes(returnf[0])-earliestdep

    # extra day of car rental(50)
    if latestarrival>earliestdep:totalprice+=50
    return totalprice+totalwait # $1 for one minute

# domain: [0,8]*len(people)*2
def randomoptimize(domain,costf):
    best = 999999999
    bestsol = None

    for i in range(1000):
        sol = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
        cost = costf(sol)
        if cost<best:
            best = cost
            bestsol = sol

    return bestsol

def hillclimboptimize(domain,costf):
    # create a initial solution
    sol = [random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]

    while 1:
        # neighboring solutions
        neighbors = []
        for j in range(len(domain)):
            if sol[j]<domain[j][1]:
                neighbor = sol[0:j] + [sol[j]+1] + sol[j+1:]
                neighbors.append(neighbor)
            if sol[j]>domain[j][0]:
                neighbor = sol[0:j] + [sol[j]-1] + sol[j+1:]
                neighbors.append(neighbor)

        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            # print("calculating solution:%s" % str(neighbors[j]))
            cost = costf(neighbors[j])
            if cost<best:
                best = cost
                sol = neighbors[j]

        # no neighbor is better
        if current == best:
            break
    return sol

if __name__ == "__main__":
    # s = [1,4,3,2,7,3,6,3,2,4,5,3]
    # printschedule(s)
    # cost = schedulecost(s)
    # print(cost)
    domain = [[0,8]]*len(people)*2
    # sol = randomoptimize(domain,schedulecost)
    sol = hillclimboptimize(domain,schedulecost)
    print("The best solution is:")
    printschedule(sol)
    print("it would cost:%f" % schedulecost(sol))