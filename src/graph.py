import networkx as nx
import json
import csv
from networkx.readwrite import json_graph
from util import *
from networkx.algorithms.approximation import clique
from constants import *

class Graph:
    def __init__(self,path):
        self.path = path
        self.title = self.path.split('/')[-2].upper()
        self.nodes,self.weighted_edges = get_nodes_and_edges(path)
        self.nodes = list(self.nodes)
        self.edges = list(self.weighted_edges)
        #self.G = nx.read_edgelist(open(path,"rb"), delimiter=',', nodetype=str, create_using=nx.DiGraph(),data=(('weight',int),))
        self.G = nx.DiGraph()
        self.G.add_nodes_from(self.nodes)
        self.G.add_weighted_edges_from(self.weighted_edges)

        # making an undirected graph from G with edge weights as the sum of all the weights
        self.H  = nx.Graph()
        self.H.add_edges_from(self.G.edges_iter(),weight=0)
        for u, v, d in self.G.edges_iter(data=True):
            self.H[u][v]['weight'] += d['weight']

    def get_general_properties(self):
        self.num_nodes =  self.G.number_of_nodes()
        self.num_edges =  self.G.number_of_edges()
        self.density =  nx.density(self.G)
        self.in_degree = sum(self.G.in_degree().values())/float(self.num_nodes)
        self.out_degree = sum(self.G.out_degree().values())/float(self.num_nodes)
        self.degree = sum(self.G.degree().values())/float(self.num_nodes)
        self.weighted_degree=sum(self.G.degree(weight='weight').values())/float(self.num_nodes)
        self.nodes_with_self_loops = len(self.G.nodes_with_selfloops())
        self.scc = len(max(nx.strongly_connected_components(self.G),key=len))
        self.wcc = len(max(nx.weakly_connected_components(self.G),key=len))
        self.max_clique = list(clique.max_clique(self.H))
        self.betweenness_centrality = sum(nx.betweenness_centrality(self.G).values())/float(self.num_nodes)
        self.closeness_centrality = sum(nx.closeness_centrality(self.G).values())/float(self.num_nodes)
        self.degree_centrality = sum(nx.degree_centrality(self.G).values())/float(self.num_nodes)
        self.eigenvector_centrality = sum(nx.eigenvector_centrality(self.G).values())/float(self.num_nodes)
        self.clustering_coeff =  sum(nx.clustering(self.H).values())/float(self.num_nodes)
        #self.simple_cycles = len(list(nx.simple_cycles(self.G)))
        #self.eccentricity = sum(nx.eccentricity(self.G).values())/float(self.num_nodes)
        #self.connectivity = self.G.all_pairs_node_connectivity()/float(self.num_nodes)
        #print nx.is_connected(self.H)
        #print nx.diameter(self.G)
        self.hub,self.auth=nx.hits(self.H)
        self.hub = sum(self.hub.values())/float(self.num_nodes)
        self.auth = sum(self.auth.values())/float(self.num_nodes)
        self.max_pagerank = max(nx.pagerank(self.G, alpha=0.9).values())

    def write_graph(self):
        new_file = self.path[:len(self.path)-len(self.path.split('/')[-1])]+'graph.graphml'
        nx.write_graphml(self.G,new_file)
        print new_file+ ' written...'

# G1 = Graph("../data/cs229/fall15/result.csv")
# G1.get_general_properties()

'''
print G1.title
print '# nodes:',G1.num_nodes
print '# edges:',G1.num_edges
print '# nodes with self loops:',G1.nodes_with_self_loops
print 'Avg in-degree:',G1.in_degree
print 'Avg out-degree:',G1.out_degree
print 'Avg degree:',G1.degree
print 'Avg weighted degree:',G1.weighted_degree
print 'Density: ',G1.density
print '-------------Connectivity---------------'
print 'Maximum clique: ',G1.max_clique
print 'Size of largest strongly connected component:',G1.scc
print 'Size of largest weakly connected component:',G1.wcc
print '-------------Centralities---------------'
print 'Average Betweenness centrality:',G1.betweenness_centrality
print 'Average Closeness centrality:',G1.closeness_centrality
print 'Average Degree centrality:',G1.degree_centrality
print 'Average Eigenvector centrality:',G1.eigenvector_centrality
print 'Average Clustering Coefficient:',G1.clustering_coeff
print '------------HITS-----------------------'
print 'Average Hub score:', G1.hub
print 'Average Authority score: ',G1.auth
print 'Max PageRank value: ',G1.max_pagerank
print G1.title
'''
#print 'Number of simple cycles:',G1.simple_cycles
#print 'Eccentricity of graph:',G1.eccentricity
#G1.write_graph()

def stats(course):
    f_out = open(DATA_DIRECTORY+course+'/statistics.csv','w')
    fieldnames = ['Course','Nodes', 'Edges','Avg In Degree','Avg Out Degree','Avg Degree','Avg Weighted Degree', 'Density', 'Largest Strongly Connected Component','Largest Weakly Connected Component', 'Average Betweenness Centrality', 'Average Closeness Centrality', 'Average Degree Centrality', 'Average Eigenvector Centrality', 'Average Clustering Coefficient', 'Average Hub Score', 'Average Authority Score', 'Max Pagerank']
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()

    for root, dirs, files in os.walk(DATA_DIRECTORY+course+'/'):
        for dir in dirs:
            G =  Graph(root+dir+'/network.csv')
            G.get_general_properties()
            writer.writerow({fieldnames[0]:G.title,
                fieldnames[1]:G.num_nodes,
                fieldnames[2]:G.num_edges,
                fieldnames[3]:G.in_degree,
                fieldnames[4]:G.out_degree,
                fieldnames[5]:G.degree,
                fieldnames[6]:G.weighted_degree,
                fieldnames[7]:G.density,
                fieldnames[8]:G.scc,
                fieldnames[9]:G.wcc,
                fieldnames[10]:G.betweenness_centrality,
                fieldnames[11]:G.closeness_centrality,
                fieldnames[12]:G.degree_centrality,
                fieldnames[13]:G.eigenvector_centrality,
                fieldnames[14]:G.clustering_coeff,
                fieldnames[15]:G.hub,
                fieldnames[16]:G.auth,
                fieldnames[17]:G.max_pagerank})










