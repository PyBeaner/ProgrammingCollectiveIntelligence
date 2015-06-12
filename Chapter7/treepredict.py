__author__ = 'PyBeaner'

my_data = [
    ['slashdot','USA','yes',18,'None'],
    ['google','France','yes',23,'Premium'],
    ['digg','USA','yes',24,'Basic'],
    ['kiwitobes','France','yes',23,'Basic'],
    ['google','UK','no',21,'Premium'],
    ['(direct)','New Zealand','no',12,'None'],
    ['(direct)','UK','no',21,'Basic'],
    ['google','USA','no',24,'Premium'],
    ['slashdot','France','yes',19,'None'],
    ['digg','USA','no',18,'None'],
    ['google','UK','no',18,'None'],
    ['kiwitobes','UK','no',19,'None'],
    ['digg','New Zealand','yes',12,'Basic'],
    ['slashdot','UK','no',21,'None'],
    ['google','UK','yes',18,'Basic'],
    ['kiwitobes','France','yes',19,'Basic']
]

column_names = ["referrer","country","xx","age","purchase"]

class decisionnode():
    def __init__(self,col=-1,value=None,results=None,tb=None,fb=None):
        self.col = col
        self.value = value
        self.results = results
        self.tb = tb
        self.fb = fb

# Divides a set on a specific column. Can handle numeric or nominal values
def divideset(rows,column,value):
    # Make a function to tells us if a row should is in the 1st(True) or the 2nd(False) group
    split_function = None
    if isinstance(value,int) or isinstance(value,float):
        split_function = lambda row:row[column]>=value
    else:
        split_function = lambda row:row[column]==value
    set1 = [row for row in rows if split_function(row)]
    set2 = [row for row in rows if not split_function(row)]
    return (set1,set2)

# Create counts of possible results (The last column of the row is the result)
def uniquecounts(rows):
    results = {}
    for row in rows:
        r = row[-1]
        if r not in results:results[r] = 0
        results[r]+=1
    return results

# Probability that a randomly placed item will be in the wrong category
def giniimpurity(rows):
    total = len(rows)
    counts = uniquecounts(rows)
    imp = 0
    for k1 in counts:
        p1 = float(counts[k1])/total
        # for k2 in counts:
        #     if k1==k2:continue
        #     p2 = float(counts[k2])/total
        #     imp+=p1*p2
        imp += p1*(1-p1)# p1 to select an randomly item in category(k1),and 1-p1 to put it in other categories
    return imp

# Entropy is the sum of p(x)log(p(x)) across all
def entropy(rows):
    from math import log
    counts = uniquecounts(rows)
    ret = 0.0
    for key in counts.keys():
        p = float(counts[key])/len(rows)
        ret -= p * log(p,2)
    return ret

def buildtree(rows,scoref=entropy):
    if len(rows)==0:return decisionnode()
    current_score = scoref(rows)
    # Set up some variables to track the best criteria
    best_gain = 0.0
    best_criteria = None
    best_sets = None

    column_count = len(rows[0])-1
    for col in range(0,column_count):
        # generate the list of different value in this column
        column_values = {}
        for row in rows:
            column_values[row[col]] = 1
        # try dividing
        for value in column_values.keys():
            set1,set2 = divideset(rows,col,value)
            # information again
            p = float(len(set1))/len(rows)
            gain = current_score-p*scoref(set1)-(1-p)*scoref(set2)
            # the bigger gain means set1,set2 is better with smaller impurity
            if gain>best_gain and len(set1)>0 and len(set2)>0:
                best_gain = gain
                best_criteria = col,value
                best_sets = set1,set2
    # create the subbranches
    if best_gain>0:
        trueBranch = buildtree(best_sets[0])
        falseBranch = buildtree(best_sets[1])
        return decisionnode(col=best_criteria[0],value=best_criteria[1],tb=trueBranch,fb=falseBranch)
    else:
        return decisionnode(results=uniquecounts(rows))

def printtree(tree,indent=""):
    if tree.results:
        print(str(tree.results))
    else:
        print(column_names[tree.col]+":"+str(tree.value)+"?")
        # branches
        print(indent+"T->")
        printtree(tree.tb,indent+" ")
        print(indent+"F->")
        printtree(tree.fb,indent+" ")

if __name__ == "__main__":
    g = giniimpurity(my_data)
    print(g)
    e = entropy(my_data)
    print(e)

    set1,set2 = divideset(my_data,2,"yes")
    # print(set1)
    # print(set2)
    print(giniimpurity(set1))
    print(entropy(set1))

    tree = buildtree(my_data,entropy)
    printtree(tree)
