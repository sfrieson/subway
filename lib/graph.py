"""A small graph class to help manage Routes"""

class Vertex:
    def __init__ (self, id):
        self.id = id

    def __str__(self):
        return str(self.id)

    __repr__ = __str__

class Edge:
    def __init__(self, v1, v2):
        self.id = (v1, v2)
    
    def __str__(self):
        return '%s%s' % self.id

    def __getitem__(self, index):
        return self.id[index]

    __repr__ = __str__

class Graph:
    def __init__(self, vertices=[], edges=[]):
        self.vertices = set(vertices)
        self.edges = edges
    
    def add_vertex(self, id):
        """Accepts either a Vertex or an argument to create a Vertex and then adds it to the Graph"""
        if isinstance(id, Vertex):
            vertex = id
        else:
            vertex = Vertex(id)

        self.vertices.add(vertex)
        return vertex

    def add_edge(self, arg1, v2=None):
        """Accepts either an Edge to be added or two Vertices to create the edge with.
        If either Vertex is not already part of the Graph it will be added."""
        edge = None

        if isinstance(arg1, Edge):
            edge = arg1
            v1 = arg1.id[0]
            v2 = arg1.id[1]

        if edge is None:
            edge = Edge(v1, v2)

        if edge not in self.edges:
            self.edges.append(edge)

        if v1 not in self.vertices:
            self.vertices.add(v1)
        if v2 not in self.vertices:
            self.vertices.add(v2)

        return edge
    
    def __str__(self):
        return 'G(%s, %s)' % (
            '{%s}' % ', '.join(map(str, self.vertices)),
            '{%s}' % ', '.join(map(str, self.edges))
        )