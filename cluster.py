from collections import defaultdict
from random import random
from math import sqrt

def strip_symbols(word):
    out = ""
    for char in word:
        if char.isalpha():
            out += char
    return out

def wordize(phrase):
    words = [strip_symbols(word.lower()) for word in phrase.split()]
    words = filter(lambda w: len(w) > 1 and w not in ('the', 'to', 'and', 'of',
        'in', 'for', 'with', 'is', 'on', 'you', 'how', 'that', 'an', 'it',
        'this', 'from', 'by', 'using', 'your', 'my', 'as', 'at', 'are',
        'what', 'its', 'we', 'can', 'about', 'do', 'why', 'now',
        'was', 'when', 'be'), words)
    return tuple(words)

def cluster(phrases, k):
    phrases = [wordize(p) for p in phrases]
    
    words = set()
    for p in phrases:
        words += p

    return kmean(phrases, words, k)
# There are n dimentions, for n words
# Each phrase is at either 0, if the word does not appear, or
# 1 if it does.
def phrase_dist(phrase, k):
    d = 0
    for word, v in k.iteritems():
        if word in phrase:
            d += (1 - v)**2
        else:
            d += v ** 2
    return sqrt(d)

def kmean(phrases, words, knum):
    ks = []
    cl_asign = {} 
    for i in range(0, knum):
        ks.append({})
        for word in words:
            ks[i][word] = random()/(2*len(words) / (float(sum((len(p) for p in phrases))) / len(phrases)))

    while 1:
        print "Iterating"
        for phrase in phrases:
            min_dist = 10000000000000
            min_k = -1
            for i, k in enumerate(ks):
                dist = phrase_dist(phrase, k)
                if (dist < min_dist):
                    min_dist = dist
                    min_k = i

            cl_asign[phrase] = min_k

        sums = []
        cnts = []
        for k in ks:
            sums.append(defaultdict(lambda: 0))
            cnts.append(0)
        for phrase, cl in cl_asign.iteritems():
            for word in phrase:
                sums[cl][word] += 1
            cnts[cl] += 1

        moved = False
        for cl, words in enumerate(sums):
            for word, val in words.iteritems():
                pos = float(val) / cnts[cl]
                if pos != ks[cl][word]:
                    moved = True
                    ks[cl][word] = pos

        if not moved:
            break

    return ks, cl_asign


if __name__ == "__main__":
    from couchdb import Server

    serv = Server('http://campdoc:campdoc@localhost:5984/')
    db = serv['reddit_data']
    phrases = [db[doc_id]['title'] for doc_id in db]

    cl, phr = cluster(phrases, 10)

    cl_sets = []
    for c in cl:
        cl_sets.append([])
    for p, c in phr.iteritems():
        cl_sets[c].append(p)

    for i, c in enumerate(cl):
        print ""
        print "Cluster %d" % i
        print "%d items" % len(cl_sets[i])
        print "-----------"
        print "Highest value words:"
        words = [(w, p) for w, p in c.iteritems()]
        words.sort(lambda a, b: 1 if a[1] < b[1] else 0 if a[1] == b[1] else -1)
        print "\n".join((":".join((str(i) for i in w)) for w in words[:10]))

        print ""
        print "Example phrases:"
        print "\n".join((" ".join((p for p in c)) for c in cl_sets[i][:10]))



