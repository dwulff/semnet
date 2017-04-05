# create dicts for passing instead of passing many variables
# fill in missing variables with defaults

import warnings
from helper import *
import numpy as np

def Toydata(toydata):
    tdkeys=toydata.keys()

    # full factorial of any list params
    for i in tdkeys:
        if isinstance(toydata[i],list):
            return flatten_list([Toydata(dict(toydata, **{i: j})) for j in toydata[i]])

    if 'trim' not in tdkeys:
        toydata['trim'] = 1.0           # each list covers full graph by default
    if 'jump' not in tdkeys:
        toydata['jump'] = 0.0           # no jumping in data by default
    if 'jumptype' not in tdkeys:
        toydata['jumptype']="uniform"   # or stationary
    if 'startX' not in tdkeys:
        toydata['startX']="uniform"      # or stationary
    if 'numx' not in tdkeys:
        raise ValueError("Must specify 'numx' in toydata!")
    if 'priming' not in tdkeys:
        toydata['priming']=0.0
    if 'priming_vector' not in tdkeys:
        toydata['priming_vector']=[]
    if 'jumponcensored' not in tdkeys:
        toydata['jumponcensored']=None

    return dotdict(toydata)

def Toygraphs(toygraphs):
    tgkeys=toygraphs.keys()
    
    # full factorial of any list params
    for i in tgkeys:
        if isinstance(toygraphs[i],list):
            return flatten_list([Toygraphs(dict(toygraphs, **{i: j})) for j in toygraphs[i]])

    if 'numgraphs' not in tgkeys:
        toygraphs['numgraphs'] = 1
    if 'graphtype' not in tgkeys:
        raise ValueError("Must specify 'graphtype' in toygraphs!")
    if 'numnodes' not in tgkeys:
        raise ValueError("Must specify 'numnodes' in toygraphs!")
    if toygraphs['graphtype'] == "wattsstrogatz":
        if 'numlinks' not in tgkeys:
            raise ValueError("Must specify 'numlinks' in toygraphs!")
        if 'prob_rewire' not in tgkeys:
            raise ValueError("Must specify 'prob_rewire' in toygraphs!")

    return dotdict(toygraphs)
        
def Irts(irts):
    irtkeys=irts.keys()

    # full factorial of any list params
    for i in irtkeys:
        if (isinstance(irts[i],list)) and (i != 'data'):       # 'data' is an exception to the rule
            return flatten_list([Irts(dict(irts, **{i: j})) for j in irts[i]])

    if 'data' not in irtkeys:
        irts['data']=[]

    if 'irttype' not in irtkeys:
        if len(irts['data']) > 0:        # error unless empty dict (no IRTs)
            raise ValueError("Must specify 'irttype' in irts!")
        else:
            irts['irttype']="none"

    if 'rcutoff' not in irtkeys:
        irts['rcutoff']=20

    if 'irt_weight' not in irtkeys:
        irts['irt_weight'] = 1.0
        #warnings.warn("Using default IRT weight of 0.9")
    else:
        if (irts['irt_weight'] > 1.0) or (irts['irt_weight'] < 0.0):
            raise ValueError('IRT weight must be between 0.0 and 1.0')
    if irts['irttype'] == "gamma":
        if 'beta' not in irtkeys:
            irts['beta'] = (1/1.1)
            #warnings.warn("Using default beta (Gamma IRT) weight of "+str(irts['beta']))
    if irts['irttype'] == "exgauss":
        if 'exgauss_lambda' not in irtkeys:
            irts['exgauss_lambda'] = 0.5
            #warnings.warn("Using default exgauss_lambda (Ex-Gaussian IRT) weight of "+str(irts['exgauss_lambda']))
        if 'exgauss_sigma' not in irtkeys:
            irts['exgauss_sigma'] = 0.5
            #warnings.warn("Using default exgauss_sigma (Ex-Gaussian IRT) weight of "+str(irts['exgauss_sigma']))

    return dotdict(irts)

def Fitinfo(fitinfo):
    fitkeys=fitinfo.keys()

    # full factorial of any list params
    for i in fitkeys:
        if isinstance(fitinfo[i],list):
            return flatten_list([Fitinfo(dict(fitinfo, **{i: j})) for j in fitinfo[i]])
    
    if 'directed' not in fitkeys:
        fitinfo['directed'] = False
    if 'startGraph' not in fitkeys:
        fitinfo['startGraph'] = "windowgraph_valid"
    if 'prune_limit' not in fitkeys:
        fitinfo['prune_limit'] = np.inf
    if 'triangle_limit' not in fitkeys:
        fitinfo['triangle_limit'] = np.inf
    if 'other_limit' not in fitkeys:
        fitinfo['other_limit'] = np.inf
    if 'windowgraph_size' not in fitkeys:
        fitinfo['windowgraph_size'] = 2
    if 'windowgraph_threshold' not in fitkeys:
        fitinfo['windowgraph_threshold'] = 2
    if 'record' not in fitkeys:
        fitinfo['record'] = False
    return dotdict(fitinfo)

