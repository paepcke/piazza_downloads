import csv
import json
import math
import networkx as nx
import matplotlib.pyplot as plt

from constants import *
from networkx.algorithms.approximation import clique
from networkx.readwrite import json_graph
from util import *

'''
This class creates a network from the edge lists using python Networkx module. 
It contains attributes and methods related to the network we create.
We create a directed weighted graph where the nodes are the users enrolled for that course
on Piazza, edge from A to B implies that A has commented on B's post and the edge weight suggests
 the total number of comments made by A on B's posts in all posts ever created by B.

Methods
-------
    - init(): 
            The init function initializes the graph. 
    - get_general_properties(): 
            Calculates all network parameters
    - write_graph(): 
            Writes a network to '.graphml' file for Gephi visualizations
'''

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

    def get_general_properties(self,best_students=None,best_instructors=None,students=None,instructors=None,sub=False,rest_students=None, rest_instructors=None):
        self.num_nodes =  self.G.number_of_nodes()
        self.num_edges =  self.G.number_of_edges()
        self.active_nodes = sum([1 for i in self.G.degree().values() if i!=0])
        self.density =  nx.density(self.G)
        self.in_degree = sum(self.G.in_degree().values())
        self.out_degree = sum(self.G.out_degree().values())
        self.degree = sum(self.G.degree().values())
        self.weighted_in_degree = sum(self.G.in_degree(weight='weight').values())
        self.weighted_out_degree = sum(self.G.out_degree(weight='weight').values())
        self.weighted_degree=sum(self.G.degree(weight='weight').values())
        self.nodes_with_self_loops = len(self.G.nodes_with_selfloops())
        self.scc = len(max(nx.strongly_connected_components(self.G),key=len))
        self.wcc = len(max(nx.weakly_connected_components(self.G),key=len))
        self.max_clique = list(clique.max_clique(self.H))
        self.betweenness_centrality = sum(nx.betweenness_centrality(self.G).values())
        self.closeness_centrality = sum(nx.closeness_centrality(self.G).values())
        self.degree_centrality = sum(nx.degree_centrality(self.G).values())
        self.eigenvector_centrality = sum(nx.eigenvector_centrality(self.G,max_iter=1000).values())
        self.clustering_coeff =  sum(nx.clustering(self.H).values())
        #self.simple_cycles = len(list(nx.simple_cycles(self.G)))
        #self.eccentricity = sum(nx.eccentricity(self.G).values())/float(self.num_nodes)
        #self.connectivity = self.G.all_pairs_node_connectivity()/float(self.num_nodes)
        #print nx.is_connected(self.H)
        #print nx.diameter(self.G)
        #self.hub,self.auth=nx.hits(self.H,max_iter=1000)
        #self.hub = sum(self.hub.values())/float(self.num_nodes)
        #self.auth = sum(self.auth.values())/float(self.num_nodes)
        self.max_pagerank = max(nx.pagerank(self.G, alpha=0.9).values())

        self.best_student_params = None
        self.best_ins_params = None

        self.param_list =[self.G.in_degree(weight='weight'),self.G.out_degree(weight='weight'),self.G.degree(weight='weight'),nx.pagerank(self.G, alpha=0.9)]

        if sub:
            self.best_student_params = find_average(best_students,self.param_list)
            self.best_ins_params = find_average(best_instructors,self.param_list)
            self.student_median = find_median(rest_students,self.param_list)

        if not sub:
            # calculation for parameters for best students, taking top 10% students
            limit1 = int(math.ceil(0.1*len(students)))
            limit2 = int(math.ceil(0.1*len(instructors)))

            best_indeg_student,best_outdeg_student,best_weighteddeg_student,best_pagerank_student = get_best_parameters(students, limit1, self.param_list)
            # calculation for parameters for best instructors, taking top 2 instructors
            best_indeg_ins,best_outdeg_ins,best_weighteddeg_ins,best_pagerank_ins = get_best_parameters(instructors, limit2, self.param_list)
            return [best_indeg_student,best_outdeg_student,best_weighteddeg_student,best_pagerank_student],[best_indeg_ins,best_outdeg_ins,best_weighteddeg_ins,best_pagerank_ins]


    def write_graph(self,path=None):
        if path: new_file = path
        else:
            new_file = self.path[:len(self.path)-len(self.path.split('/')[-1])]+'graph.graphml'
        nx.write_graphml(self.G,new_file)
        print new_file+ ' written...'

    def draw_graph(self):
        nx.draw(self.G, node_color='c',edge_color='k',pos=nx.spring_layout(self.G,scale=7) )
        plt.draw()
        plt.show()

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

def stats(course,divide=False,all_stats=False):
    if not os.path.exists('../stats/'+course):
        os.makedirs('../stats/'+course)
    f_out = open('../stats/'+course+'/average_stats.csv','w')

    if all_stats:
        f_out_all_stats = open('../stats/'+course+'/stats.csv','w')

        fieldnames_all = ['Offering','Nodes','Edges','Weighted In Degree','Weighted Out Degree','Weighted Degree','Density','Active Participants', 'Size of largest strongly connected component', 'Size of largest weakly connected component']
        writer_all = csv.DictWriter(f_out_all_stats, fieldnames=fieldnames_all)
        writer_all.writeheader()

    for root, dirs, files in os.walk(DATA_DIRECTORY+course+'/'):
        for course_dir in sorted(dirs,key=lambda d:d[-2:]):
            print course_dir
            fieldnames = ['Course','Nodes', 'Edges','Avg In Degree','Avg Out Degree','Avg Degree','Avg Weighted Degree', 'Density', 'Largest Strongly Connected Component','Largest Weakly Connected Component', 'Average Betweenness Centrality', 'Average Closeness Centrality', 'Average Degree Centrality', 'Average Eigenvector Centrality', 'Average Clustering Coefficient', 'Average Hub Score', 'Average Authority Score', 'Max Pagerank']
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            G =  Graph(root+course_dir+'/network.csv')
            print root+course_dir+'/network.csv'
            #G.write_graph()
            instructors, students = identify_instructors(root+course_dir)
            best_student_params, best_ins_params = G.get_general_properties(students=students,instructors=instructors)

            # top students and instructors
            best_students = [k.keys() for k in best_student_params]

            print 'Weighted out degrees :',best_students[1]
            best_instructors = [k.keys() for k in best_ins_params]
            rest_students = [list(set(students)-set(best_students[i])) for i in range(len(best_students))]
            rest_instructors = [list(set(instructors)-set(best_instructors[i])) for i in range(len(best_instructors))]

            writer.writerow({
                fieldnames[0]:G.title,
                fieldnames[1]:G.num_nodes,
                fieldnames[2]:G.num_edges,
                fieldnames[3]:G.in_degree/float(G.num_nodes),
                fieldnames[4]:G.out_degree/float(G.num_nodes),
                fieldnames[5]:G.degree/float(G.num_nodes),
                fieldnames[6]:G.weighted_degree/float(G.num_nodes),
                fieldnames[7]:G.density,
                fieldnames[8]:G.scc,
                fieldnames[9]:G.wcc,
                fieldnames[10]:G.betweenness_centrality/float(G.num_nodes),
                fieldnames[11]:G.closeness_centrality/float(G.num_nodes),
                fieldnames[12]:G.degree_centrality/float(G.num_nodes),
                fieldnames[13]:G.eigenvector_centrality/float(G.num_nodes),
                fieldnames[14]:G.clustering_coeff/float(G.num_nodes),
                fieldnames[15]:0,#G.hub,
                fieldnames[16]:0,#G.auth,
                fieldnames[15]:G.max_pagerank})
            if divide:
                if not os.path.exists('../stats/'+course+'/'+course_dir):
                    os.makedirs('../stats/'+course+'/'+course_dir)
                f_out_sub_student = open('../stats/'+course+'/'+course_dir+'/top_statistics_student.csv','w')
                f_out_sub_ins = open('../stats/'+course+'/'+course_dir+'/top_statistics_instructor.csv','w')
                f_out_sub_median_students = open('../stats/'+course+'/'+course_dir+'/median_statistics_student.csv','w')
                print '../stats/'+course+'/'+course_dir+'/top_statistics_student.csv',
                print '../stats/'+course+'/'+course_dir+'/median_statistics_student.csv'

                fieldnames_sub = ['Week','Weighted In Degree','Weighted Out Degree','Weighted Degree', 'Pagerank']
                writer_sub_student = csv.DictWriter(f_out_sub_student, fieldnames=fieldnames_sub)
                writer_sub_student.writeheader()

                writer_sub_ins = csv.DictWriter(f_out_sub_ins, fieldnames=fieldnames_sub)
                writer_sub_ins.writeheader()

                writer_sub_median = csv.DictWriter(f_out_sub_median_students, fieldnames=fieldnames_sub)
                writer_sub_median.writeheader()


                for i in range(1,20):
                    if os.path.exists(root+course_dir+'/subnetwork'+str(i)+'.csv'):
                        #print root+course_dir+'/subnetwork'+str(i)+'.csv'
                        G_sub =  Graph(root+course_dir+'/subnetwork'+str(i)+'.csv')
                        #G_sub.write_graph(root+course_dir+'/subnetwork'+str(i)+'.graphml')

                        G_sub.get_general_properties(best_students=best_students,best_instructors=best_instructors,sub=True, students=students,rest_students=rest_students, rest_instructors=rest_instructors)

                        writer_sub_student.writerow({
                        fieldnames_sub[0]: i,
                        fieldnames_sub[1]:G_sub.best_student_params[0],
                        fieldnames_sub[2]:G_sub.best_student_params[1],
                        fieldnames_sub[3]:G_sub.best_student_params[2],
                        fieldnames_sub[4]:G_sub.best_student_params[3]
                        })

                        writer_sub_ins.writerow({
                        fieldnames_sub[0]: i,
                        fieldnames_sub[1]:G_sub.best_ins_params[0],
                        fieldnames_sub[2]:G_sub.best_ins_params[1],
                        fieldnames_sub[3]:G_sub.best_ins_params[2],
                        fieldnames_sub[4]:G_sub.best_ins_params[3]
                        })

                        if G_sub.student_median:
                            writer_sub_median.writerow({
                            fieldnames_sub[0]: i,
                            fieldnames_sub[1]:G_sub.student_median[0],
                            fieldnames_sub[2]:G_sub.student_median[1],
                            fieldnames_sub[3]:G_sub.student_median[2],
                            fieldnames_sub[4]:G_sub.student_median[3]
                            })
                        else:
                            writer_sub_median.writerow({
                            fieldnames_sub[0]: i,
                            fieldnames_sub[1]:-10,
                            fieldnames_sub[2]:-10,
                            fieldnames_sub[3]:-10,
                            fieldnames_sub[4]:-10
                            })


                    else: 
                        break

            if all_stats:
                writer_all.writerow({
                                fieldnames_all[0]:course_dir.upper(),
                                fieldnames_all[1]:G.num_nodes,
                                fieldnames_all[2]:G.num_edges,
                                fieldnames_all[3]:G.weighted_in_degree,
                                fieldnames_all[4]:G.weighted_out_degree,
                                fieldnames_all[5]:G.weighted_degree,
                                fieldnames_all[6]:G.density,
                                fieldnames_all[7]:G.active_nodes,
                                fieldnames_all[8]:G.scc,
                                fieldnames_all[9]:G.wcc
                                })



                