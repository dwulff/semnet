# IO functions:
#
# * Read graph from file
# * Write graph to file
# * Read fluency data from file

import textwrap
import numpy as np

# package not very necessary and a cause of trouble on many machines
try: import matplotlib.pyplot as plt
except: print "Warning: Failed to import matplotlib"

# sibling functions
from helper import *

# write graph to GraphViz file (.dot)
def drawDot(g, filename, labels={}):
    if type(g) == np.ndarray:
        g=nx.to_networkx_graph(g)
    if labels != {}:
        nx.relabel_nodes(g, labels, copy=False)
    nx.drawing.write_dot(g, filename)

# draw graph
def drawG(g,Xs=[],labels={},save=False,display=True):
    if type(g) == np.ndarray:
        g=nx.to_networkx_graph(g)
    nx.relabel_nodes(g, labels, copy=False)
    #pos=nx.spring_layout(g, scale=5.0)
    pos = nx.graphviz_layout(g, prog="fdp")
    nx.draw_networkx(g,pos,node_size=1000)
#    for node in range(numnodes):                    # if the above doesn't work
#        plt.annotate(str(node), xy=pos[node])       # here's a workaround
    if Xs != []:
        plt.title(Xs)
    plt.axis('off')
    if save==True:
        plt.savefig('temp.png')                      # need to parameterize
    if display==True:
        plt.show()

# ** DEPRECATED
# helper function converts binary adjacency matrix to base 36 string for easy storage in CSV
# binary -> int -> base62
def graphToHash(a,numnodes):
    def baseN(num,b,numerals="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])
    return str(numnodes) + '!' + baseN(int(''.join([str(i) for i in flatten_list(a)]),2), 62)

# ** DEPRECATED
# see graphToHash function
def hashToGraph(graphhash):
    numnodes, graphhash = graphhash.split('!')
    numnodes=int(numnodes)
    graphstring=bin(int(graphhash, 36))[2:]
    zeropad=numnodes**2-len(graphstring)
    graphstring=''.join(['0' for i in range(zeropad)]) + graphstring
    arrs=textwrap.wrap(graphstring, numnodes)
    mat=np.array([map(int, s) for s in arrs])
    return mat

# so far only uses first two columns (node1 and node2), can't use another column to filter rows
# only makes symmetric (undirected) graph
# not optimized
def read_csv(fh):
    fh=open(fh,'r')
    items={}
    idx=0
    biglist=[]
    for line in fh:
        line=line.rstrip()
        twoitems=line.split(',')[0:2]
        biglist.append(twoitems)
        for item in twoitems:
            if item not in items.values():
                items[idx]=item
                idx += 1
    graph=np.zeros((len(items),len(items)))
    for twoitems in biglist:
        idx1=items.values().index(twoitems[0])
        idx2=items.values().index(twoitems[1])
        graph[idx1,idx2]=1
        graph[idx2,idx1]=1
    return graph, items

# read Xs in from user files
def readX(subj,category,filepath):
    if type(subj) == str:
        subj=[subj]
    game=-1
    cursubj=-1
    Xs=[]
    irts=[]
    items={}
    idx=0
    with open(filepath) as f:
        for line in f:
            row=line.split(',')
            if (row[0] in subj) & (row[2] == category):
                if (row[1] != game) or (row[0] != cursubj):
                    Xs.append([])
                    irts.append([])
                    game=row[1]
                    cursubj=row[0]
                item=row[3]
                irt=row[4]
                if item not in items.values():
                    items[idx]=item
                    idx += 1
                itemval=items.values().index(item)
                if itemval not in Xs[-1]:   # ignore any duplicates in same list resulting from spelling corrections
                    Xs[-1].append(itemval)
                    irts[-1].append(int(irt)/1000.0)
    numnodes = len(items)
    return Xs, items, irts, numnodes

def write_csv(gs, fh, subj="NA"):
    fh=open(fh,'w',0)
    if isinstance(gs,nx.classes.graph.Graph):       # write nx graph
        edges=set(flatten_list([gs.edges()]))
        for edge in edges:
            fh.write(subj    + "," +
                    edge[0]  + "," +
                    edge[1]  + "\n")
    else:                                           # write matrix
        onezero={True: '1', False: '0'}        
        edges=set(flatten_list([gs[i].edges() for i in range(len(gs))]))
        for edge in edges:
            edgelist=""
            for g in gs:
                edgelist=edgelist+","+onezero[g.has_edge(edge[0],edge[1])]
            fh.write(subj    + "," +
                    edge[0]  + "," +
                    edge[1]  + 
                    edgelist + "\n")
    return
