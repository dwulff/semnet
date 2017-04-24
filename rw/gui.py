import rw as rw
import numpy as np
import os, sys
import networkx as nx

def list_subjects_and_categories(command):
    subjects=[]
    categories=[]
    with open(command['fullpath'],'r') as fh:
        header=fh.readline().split(',')
        subj_idx = header.index("id")
        cat_idx = header.index("category")
        for line in fh:
            line=line.split(',')
            if line[subj_idx] not in subjects:
                subjects.append(line[subj_idx])
            if line[cat_idx] not in categories:
                categories.append(line[cat_idx])
    return { "type": "list_subjects_and_categories",
             "subjects": subjects, 
             "categories": categories,
             "subject": subjects[0],
             "category": categories[0] }

def jsonGraph(g, items):
    from networkx.readwrite import json_graph
    json_data = json_graph.node_link_data(g)
    
    json_data['edges'] = json_data['links']
    json_data.pop('links', None)
    json_data.pop('directed', None)
    json_data.pop('multigraph', None)
    json_data.pop('graph', None)
    
    for i, j in enumerate(json_data['edges']):
        json_data['edges'][i]['id'] = i
    
    for i, j in enumerate(json_data['nodes']):
        json_data['nodes'][i]['label']=items[j['id']]
    
    return json_data

def data_properties(command):
    def cluster_scheme_filename(x):
        current_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        schemes = { "Troyer": "/../schemes/troyer_animals.csv",
                    "Troyer-Hills": "/../schemes/troyer_hills_animals.csv",
                    "Troyer-Hills-Zemla": "/../schemes/troyer_hills_zemla_animals.csv" }
        filename = current_dir + schemes[x]
        return filename
    
    def spelling_filename(x):
        current_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
        schemes = { "Zemla": "/../schemes/zemla_spellfile.csv",
                    "None": None }
        if schemes[x]:
            filename = current_dir + schemes[x]
        else:                                   # if "None" don'tm append directory
            filename = schemes[x]
        return filename
    
    command = command['data_parameters']
    Xs, items, irts, numnodes = rw.readX(command['subject'], command['category'], command['fullpath'], spellfile=spelling_filename(command['spellfile']))
    Xs = rw.numToAnimal(Xs, items)
    cluster_sizes = rw.clusterSize(Xs, cluster_scheme_filename(command['cluster_scheme']), clustertype=command['cluster_type'])
    avg_cluster_size = rw.avgClusterSize(cluster_sizes)
    avg_num_cluster_switches = rw.avgNumClusterSwitches(cluster_sizes)
    num_lists = len(Xs)
    avg_items_listed = np.mean([len(i) for i in Xs])
    avg_unique_items_listed = np.mean([len(set(i)) for i in Xs])
    intrusions = rw.intrusions(Xs, cluster_scheme_filename(command['cluster_scheme']))
    avg_num_intrusions = rw.avgNumIntrusions(intrusions)
    perseverations = rw.perseverations(Xs)
    avg_num_perseverations = rw.avgNumPerseverations(Xs)

    return { "type": "data_properties", 
             "num_lists": num_lists,
             "avg_items_listed": avg_items_listed,
             "intrusions": intrusions,
             "perseverations": perseverations,
             "avg_num_intrusions": avg_num_intrusions,
             "avg_num_perseverations": avg_num_perseverations,
             "avg_unique_items_listed": avg_unique_items_listed,
             "avg_num_cluster_switches": avg_num_cluster_switches,
             "avg_cluster_size": avg_cluster_size }

def network_properties(command):
    subj_props = command['data_parameters']
    command = command['network_parameters']
    Xs, items, irts, numnodes = rw.readX(subj_props['subject'], subj_props['category'], subj_props['fullpath'])

    def no_persev(x):
        seen = set()
        seen_add = seen.add
        return [i for i in x if not (i in seen or seen_add(i))]

    toydata=rw.Data({
            'numx': len(Xs),
            'trim': 1,
            'jump': 0.0,
            'jumptype': "stationary",
            'priming': 0.0,
            'startX': "stationary"})
    fitinfo=rw.Fitinfo({
            'startGraph': "goni_valid",
            'goni_size': 2,
            'goni_threshold': 2,
            'followtype': "avg", 
            'prior_samplesize': 10000,
            'recorddir': "records/",
            'prune_limit': 100,
            'triangle_limit': 100,
            'other_limit': 100})
   
    
    if command['network_method']=="RW":
        bestgraph = rw.noHidden(Xs, numnodes)
    elif command['network_method']=="Goni":
        bestgraph = rw.goni(Xs, numnodes, td=toydata, valid=0, fitinfo=fitinfo)
    elif command['network_method']=="U-INVITE":
        no_persev_Xs = [no_persev(x) for x in Xs]       # U-INVITE doesn't work with perseverations
        bestgraph, ll = rw.uinvite(no_persev_Xs, toydata, numnodes, fitinfo=fitinfo,debug=False)
  
    nxg = nx.to_networkx_graph(bestgraph)

    node_degree = np.mean(nxg.degree().values())
    nxg_json = jsonGraph(nxg, items)
    clustering_coefficient = nx.average_clustering(nxg)
    try:
        aspl = nx.average_shortest_path_length(nxg)
    except:
        aspl = "disjointed graph"
    
    return { "type": "network_properties",
             "node_degree": node_degree,
             "clustering_coefficient": clustering_coefficient,
             "aspl": aspl,
             "graph": nxg_json }

def quit(command): 
    return { "type": "quit",
             "status": "success" }

def error(msg):
    return { "type": "error",
             "msg": msg }
