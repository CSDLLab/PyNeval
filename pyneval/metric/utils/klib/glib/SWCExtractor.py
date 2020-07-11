import os
import codecs

class Vertex(object):
    '''Define a Vertex class represent a node in SWC structure'''
    def __init__(self, idx, itype, x, y, z, r, p_idx):
        """ Constructor
            idx: id
            itype: node type
            x,y,z: 3d position
            r: radius
            p_idx: parent index
        """
        self.idx = idx
        self.itype = itype
        self.pos = [x,y,z]
        self.r = r
        self.p_idx = p_idx

    def getChilds(self, graph):
        ''' Get children's id of this node.
            Input:
                graph(dict<int,set<int>>)
            Output:
                list
        '''
        neighbors = list(graph[self.idx])
        return list(filter(lambda x:x!=self.p_idx, neighbors))

    def __str__(self):
        """ Convert Vertex to string
            when print(Vertex()) is called, this function will be called
        """
        return 'id{1}:{0}\n'.format(self.idx,type(self.idx)) \
               + 'itype{1}:{0}\n'.format(self.itype,type(self.itype)) \
               + 'pos{1}:{0}\n'.format(self.pos,type(self.pos)) \
               + 'r{1}:{0}\n'.format(self.r,type(self.r)) \
               + 'pid{1}:{0}\n'.format(self.p_idx,type(self.p_idx))

def extractSWC(file_path):
    """ Extract the sturcture of swc file
        Input:
            file_path:str path to swc file
        Output:
            nodes:dict vertex list information
            graph:dict the topo of each node
    """
    nodes = {} # id:Vertex
    graph = {} # id:Set(id)

    f = open(file_path)
    # f = codecs.open(file_path, "r",encoding='utf-8', errors='ignore')

    count = 0
    for line in f:
        if not line.startswith('#'):
            args = line.split(' ')
            args = list(filter(None,args)) # *Remove all empty string

            if len(args) == 7:
                if args[-1].endswith(os.linesep): # *Remove line separater
                    args[-1] = args[-1][:-len(os.linesep)]

                    args = list(map(float,args)) # *Convert data type to float
                    args[0] = int(args[0])
                    args[1] = int(args[1])
                    args[-1] = int(args[-1])

                    v1 = args[0]
                    v2 = args[-1]

                    vertex = Vertex(*args[:]) # *Construct a class using list as parameter
                    if vertex.idx not in nodes: # Add vertex
                        nodes[vertex.idx]  = vertex

                    if v2 > 0 and v1 > 0: # Add edge to graph

                        if not v1 in graph:
                            graph[v1] = set([v2])
                        else:
                            graph[v1].add(v2)

                        if not v2 in graph:
                            graph[v2] = set([v1])
                        else:
                            graph[v2].add(v1)

                    else:
                        pass

    return nodes, graph
