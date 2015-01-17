#!/usr/bin/python

# V8
# threading! Cython!

import networkx as nx
import numpy as np
import random
import operator
import math
import matplotlib.pyplot as plt
import time
import scipy.stats as ss
import matplotlib.animation as animation
import multiprocessing as mp
import genz
import pyximport
pyximport.install(setup_args={'include_dirs':[np.get_include()]},pyimport=True)

# random walk given an adjacency matrix that hits every node; returns a list of tuples
def random_walk(g,s=None):
    if s is None:
        s=random.choice(range(len(a)))
    walk=[]
    unused_nodes=set(range(len(a)))
    unused_nodes.remove(s)
    while len(unused_nodes) > 0:
        p=s
        s=random.choice([x for x in nx.all_neighbors(g,s)]) # follow random edge
        walk.append((p,s))
        if s in unused_nodes:
            unused_nodes.remove(s)
    return walk

# flat list from tuple walk
def path_from_walk(walk):
    path=list(zip(*walk)[0]) # first element from each tuple
    path.append(walk[-1][1]) # second element from last tuple
    return path

# tuple walk from flat list
def walk_from_path(path):
    walk=[]
    for i in range(len(path)-1):
        walk.append((path[i],path[i+1])) 
    return walk

# Unique nodes in random walk preserving order
# (aka fake participant data)
# http://www.peterbe.com/plog/uniqifiers-benchmark
def observed_walk(walk):
    seen = {}
    result = []
    for item in path_from_walk(walk):
        if item in seen: continue
        seen[item] = 1
        result.append(item)
    return result

def genX(g):
    return observed_walk(random_walk(g))

# first hitting times for each node
def firstHit(walk):
    firsthit=[]
    path=path_from_walk(walk)
    for i in observed_walk(walk):
        firsthit.append(path.index(i))
    return zip(observed_walk(walk),firsthit)

# generate random walk that results in observed x (using rho function)
def genZfromX(x, theta):
    x2=x[:]                  # make a local copy
    x2.reverse()
    
    path=[]                  # z to return
    path.append(x2.pop())    # add first two x's to z
    path.append(x2.pop())

    while len(x2) > 0:
        if random.random() < theta:
            # add random hidden node
            possibles=set(path) # choose equally from previously visited nodes
            possibles.discard(path[-1]) # but exclude last node (node cant link to itself)
            path.append(random.choice(list(possibles)))
        else:
            # first hit!
            path.append(x2.pop())
    return walk_from_path(path)

# log probability of random walk Z on link matrix A
def logprobZ(walk,a):
    t=a/sum(a.astype(float))                        # transition matrix
    logProbList=[]
    for i,j in walk:
        logProbList.append(math.log(t[i,j]))
    logProb=sum(logProbList)
    logProb=logProb + math.log(1/float(len(a)))     # base rate of first node when selected uniformly
    return logProb

# wrapper for genZfromXG using multithreading
def threadZ(x,graph,numz):
    zarr=[]
    for i in range(numz):
        zarr.append(genZfromXG(x,graph))
    return zarr

# log probability of a graph (no prior)
def logprobG(graph):
    probG=0
    for x in Xs:
        result=[]
        starttime=time.time()
        if threading==0:
            zGs=[genz.genZfromXG(x,graph) for i in range(numsamples)] # without threading
        else:
            pool = mp.Pool(processes=numthreads)
            sperthread=numsamples/numthreads  # distribute samples evenly among threads
            for i in range(numthreads):
                if i+1==numthreads:
                    sperthread= sperthread + (numsamples % numthreads) # in case it's not divisible evenly
                result.append(pool.apply_async(genz.threadZ, [x, graph, sperthread]))
            zGs= reduce(operator.add,[i.get() for i in result])
            pool.close()
        print time.time()-starttime
        loglist=[logprobZ(i,graph) for i in zGs]
        logmax=max(loglist)
        loglist=[i-logmax for i in loglist]                          # log trick: subtract off the max
        probZG=math.log(sum([math.e**i for i in loglist])) + logmax  # add it back on
        probG=probG+probZG
    return probG
        
# Generate a connected Watts-Strogatz small-world graph
# (n,k,p) = (number of nodes, each node connected to k-nearest neighbors, probability of rewiring)
# k has to be even, tries is number of attempts to make connected graph
def genG(n,k,p,tries=1000):
    g=nx.connected_watts_strogatz_graph(n,k,p,tries) # networkx graph
    a=np.array(nx.adjacency_matrix(g).todense())     # adjacency matrix
    #i=nx.incidence_matrix(g).todense()              # incidence matrix
    return g, np.array(a, dtype=np.int32)

# returns both networkx graph G and link matrix A
def genGfromZ(walk):
    #numnodes=len(observed_walk(walk))
    a=np.zeros((numnodes,numnodes))
    for i in set(walk):
        a[i[0],i[1]]=1
        a[i[1],i[0]]=1 # symmetry
    a=np.array(a.astype(int))
    #g=nx.from_numpy_matrix(a)      # too slow, not necessary
    return a

# helper function for optimization
def timer(times):
    t1=time.time()
    for i in range(times):
        genZfromXG(x,a) # insert function to time here
    t2=time.time()
    return t2-t1

# constrained random walk
# generate random walk on a that results in observed x 
# if we had IRT data, this might be a good solution: http://cnr.lwlss.net/ConstrainedRandomWalk/
def genZfromXG(x,a):
    # restrict walk to only the next node in x OR previously visited nodes
    possibles=np.zeros(len(a),dtype=int)
    possibles[[x[0],x[1],x[2]]] = 1
    walk=[(x[0], x[1])]      # add first two Xs to random walk
    pos=2                    # only allow items up to pos
    newa=np.copy(a)                          ## 
    for i in range(len(newa)):               ## these lines sped up code a lot but look a bit sloppy
        newa[i][np.where(possibles==0)[0]]=0 ##
    while len(x[pos:]) > 0:
        p=walk[-1][1]
        pruned_links=np.flatnonzero(newa[p]) ##
        s=random.choice(pruned_links)
        walk.append((p,s))
        if s in x[pos:]:
            pos=pos+1
            if len(x[pos:]) > 0:
                possibles[x[pos]] = 1
                newa=np.copy(a) ##
                for i in range(len(newa)): ##
                    newa[i][np.where(possibles==0)[0]]=0 ##
    return walk


# Draw graph
def drawG(g,save=False,display=True):
    pos=nx.spring_layout(g)
    nx.draw_networkx(g,pos,with_labels=True)
#    nx.draw_networkx_labels(g,pos,font_size=12)
#    for node in range(numnodes):                    # sometimes the above doesn't work
#        plt.annotate(str(node), xy=pos[node])       # here's a workaround
    plt.title(x)
    plt.axis('off')
    if save==True:
        plt.savefig('temp.png')
    if display==True:
        plt.show()

# return small world statistic of a graph
def smallworld(a):
    g_sm=nx.from_numpy_matrix(a)
    c_sm=nx.average_clustering(g_sm)
    l_sm=nx.average_shortest_path_length(g_sm)
    c_rand= (numedges*2.0)/(numnodes*(numnodes-1))     # same as edge density for a random graph
    l_rand= math.log(numnodes)/math.log(2*numlinks)  # see humphries & gurney (2006) eq 11
    #l_rand= (math.log(numnodes)-0.5772)/(math.log(2*numlinks)) + .5 # alternative from fronczak, fronczak & holyst (2004)
    s=(c_sm/c_rand)/(l_sm/l_rand)
    return s

if __name__ == "__main__":
    numnodes=20             # number of nodes in graph
    numlinks=4              # initial number of edges per node (must be even)
    probRewire=.2           # probability of re-wiring an edge
    numedges=numlinks*10    # number of edges in graph
    
    theta=.5                # probability of hiding node when generating z from x (rho function)
    numx=2                  # number of Xs to generate

    threading=1              # use multi-threading? speeds up code a bit
    numthreads=2            # number of threads to deploy
    numsamples=100          # number of sample z's to estimate likelihood

    # Generate small-world graph
    g,a=genG(numnodes,numlinks,probRewire) 
    
    # Generate fake participant data
    Xs=[genX(g) for i in range(numx)]

    # generate initial graph (lead graph)
    Z=[]
    for x in Xs:
        Z= Z + genZfromX(x,theta)
    lead=genGfromZ(Z)      
    cost=sum(sum(np.array(abs(lead-a)))) # cost of lead graph

       
    edgelist=[(i,j) for i in range(numnodes) for j in range(numnodes) if i>j] # list all edges
    random.shuffle(edgelist)
   
    lpLead = logprobG(lead)   # set lead LP
    est_costs=[]
    est_costs.append(logprobG(lead))

    for edge in edgelist:
        poss=np.copy(lead)
        flip=edgelist.pop()
        poss[flip]= 1-poss[flip]    # flip random edges
        lpPoss = logprobG(poss)
        if lpPoss > lpLead:
            # check to make sure new G is possible
            cost=sum(sum(np.array(abs(lead-a))))
            # print lpPoss, ">", lpLead, "cost: ", cost
            lead=poss
            lpLead=lpPoss
            est_costs.append(lpLead)
        else:
            # accept with some probability
            # math.e**(lpPoss-lpLead)
            # print lpPoss, "<", lpLead
            pass

#    plt.scatter(costs[0:len(est_costs)],est_costs)
#    plt.show(block=False)
