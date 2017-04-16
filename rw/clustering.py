import numpy as np

# given list of cluster lengths, compute average cluster size of each list, then return avearge of that
# also works on single list
def avgClusterSize(clist):
    avglist=[]
    for l in clist:
        avglist.append(np.mean(l))
    return np.mean(avglist)

def avgNumIntrusions(ilist):
    if isinstance(ilist[0],list):
        return np.mean([len(i) for i in ilist])
    else:
        return len(ilist)

# given list of cluster lengths, compute average number of cluster switches of each list, then return avearge of that
# also works on single list
def avgNumClusterSwitches(clist):
    avgnum=[]
    for l in clist:
        avgnum.append(len(l)-1)
    return np.mean(avgnum)

# report average cluster size for list or nested lists
def clusterSize(l, scheme, clustertype='fluid'):
    # only convert items to labels if list of items, not list of lists
    if isinstance(l[0], list):
        clusters=l
    else:
        clusters=labelClusters(l, scheme)
    
    csize=[]
    curcats=set([])
    runlen=0
    clustList=[]
    firstitem=1
    for inum, item in enumerate(clusters):
        if isinstance(item, list):
            clustList.append(clusterSize(item, scheme, clustertype=clustertype))
        else:
            newcats=set(item.split(';'))
            if 'unknown' in newcats:
                #print "Warning: Unknown category for item '", l[inum], "'. Add this item to your category labels or results may be incorrect!"
                pass
            if newcats.isdisjoint(curcats) and firstitem != 1:      # end of cluster, append cluster length
                csize.append(runlen)
                runlen = 1
            else:                                                   # shared cluster or start of list
                runlen += 1
            
            if clustertype=="fluid":
                curcats = newcats
            elif clustertype=="static":
                curcats = (curcats & newcats)
                if curcats==set([]):
                    curcats = newcats
            else:
                raise ValueError('Invalid cluster type')
        firstitem=0
    csize.append(runlen)
    if sum(csize) > 0:
        clustList += csize
    return clustList

# returns labels in place of items for list or nested lists
# provide list (l) and coding scheme (external file)
def labelClusters(l, scheme):
    cf=open(scheme,'r')
    cats={}
    for line in cf:
        line=line.rstrip()
        cat, item = line.split(',')
        cat=cat.lower().replace(' ','').replace("'","").replace("-","") # basic clean-up
        item=item.lower().replace(' ','').replace("'","").replace("-","")
        if item not in cats.keys():
            cats[item]=cat
        else:
            if cat not in cats[item]:
                cats[item]=cats[item] + ';' + cat
    labels=[]
    for inum, item in enumerate(l):
        if isinstance(item, list):
            labels.append(labelClusters(item, scheme))
        else:
            item=item.lower().replace(' ','')
            if item in cats.keys():
                labels.append(cats[item])
            else:
                labels.append("unknown")
    return labels

def intrusions(l, scheme):
    labels=labelClusters(l, scheme)
    if isinstance(labels[0], list):
        intrusion_items=[]
        for listnum, nested_list in enumerate(labels):
            intrusion_items.append([l[listnum][i] for i, j in enumerate(nested_list) if j=="unknown"])
    else:
        intrusion_items = [l[i] for i, j in enumerate(labels) if j=="unknown"]
    return intrusion_items
    
def perseverations(l):
    perseveration_items=[] 
    for ls in l:
        perseveration_items.append(list(set([item for item in ls if ls.count(item) > 1])))
    return perseveration_items


def avgNumPerseverations(l):
    return np.mean([len(i)-len(set(i)) for i in l])


# ** UNTESTED // modified from usf_cogsci.py
# avg num cluster types per list
def numClusters(data):
    numclusts_real=np.mean([len(set(flatten_list([j.split(';') for j in i]))) for i in labelClusters(data,scheme)])
    return numclusts_real

