# create dicts for passing instead of passing many variables
# fill in missing variables with defaults

import warnings
from helper import dotdict

def Toydata(toydata):
    tdkeys=toydata.keys()
    if 'trim' not in tdkeys:
        toydata['trim'] = 1.0           # each list covers full graph by default
    if 'jump' not in tdkeys:
        toydata['jump'] = 0.0           # no jumping in data by default
    if 'jumptype' not in tdkeys:
        toydata['jumptype']="uniform"   # or stationary
    if 'start' not in tdkeys:
        toydata['start']="uniform"      # or stationary
    if 'numx' not in tdkeys:
        raise ValueError('Must specify \'numx\' in toydata!')
    
    return dotdict(toydata)

def Toygraphs(toygraphs):
    tgkeys=toygraphs.keys()
    if 'numgraphs' not in tgkeys:
        toygraphs['numgraphs'] = 1
    if 'graphtype' not in tgkeys:
        raise ValueError('Must specify \'graphtype\' in toygraphs!')
    if 'numnodes' not in tgkeys:
        raise ValueError('Must specify \'numnodes\' in toygraphs!')
    if toygraphs['graphtype'] == "smallworld":
        if 'numlinks' not in tgkeys:
            raise ValueError('Must specify \'numlinks\' in toygraphs!')
        if 'probRewire' not in tgkeys:
            raise ValueError('Must specify \'probRewire\' in toygraphs!')

    return dotdict(toygraphs)
        
def Irtinfo(irtinfo):
    irtkeys=irtinfo.keys()
    if 'irttype' not in irtkeys:
        if len(irtinfo) > 0:        # error unless empty dict (no IRTs)
            raise ValueError('Must specify \'irttype\' in irtinfo!')
        else:
            irtinfo['irttype']="none"
            return dotdict(irtinfo)

    if 'irt_weight' not in irtkeys:
        irtinfo['irt_weight'] = 0.9
        warnings.warn("Using default IRT weight of 0.9")
    else:
        if (irtinfo['irt_weight'] > 1.0) or (irtinfo['irt_weight'] < 0.0):
            raise ValueError('IRT weight must be between 0.0 and 1.0')
    if irtinfo['irttype'] == "gamma":
        if 'beta' not in irtkeys:
            irtinfo['beta'] = (1/1.1)
            warnings.warn("Using default beta (Gamma IRT) weight of "+str(irtinfo['beta']))
    if irtinfo['irttype'] == "exgauss":
        if 'tau' not in irtkeys:
            irtinfo['tau'] = 0.5
            warnings.warn("Using default tau (Ex-Gaussian IRT) weight of "+str(irtinfo['tau']))
        if 'sig' not in irtkeys:
            irtinfo['sig'] = 0.5
            warnings.warn("Using default sig (Ex-Gaussian IRT) weight of "+str(irtinfo['sig']))

    
    return dotdict(irtinfo)
