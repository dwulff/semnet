import rw

outfile='tmp.csv'
header=1

toygraphs=rw.Toygraphs({
        'numgraphs': 10,
        'graphtype': "steyvers",
        'numnodes': 160,
        'numlinks': 6,
        'prob_rewire': .3})

toydata=rw.Toydata({
        'numx': [20],
        'trim': .7,
        'jump': 0.0,
        'jumptype': "stationary",
        'startX': "stationary"})

irts=rw.Irts({
        'data': [],
        'irttype': "gamma",
        'beta': (1/1.1),
        'irt_weight': 0.9,
        'rcutoff': 20})

fitinfo=rw.Fitinfo({
        'tolerance': 1500,
        'startGraph': "naiverw",
        'prob_multi': 1.0,
        'prob_overlap': 0.5})

# optionally, pass a methods argument
# default is methods=['fe','rw','uinvite','uinvite_irt'] 
for td in toydata:
    rw.toyBatch(toygraphs, td, outfile, irts=irts, start_seed=1,methods=['uinvite'],header=header,debug="F")
    header=0
