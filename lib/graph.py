"""A small graph class to help manage Routes"""

class Vertex:
    def __init__(self, id):
        self.id = id
        self.adjacent = None
    
    def add_adjacent(self, vertex=None):
        """Adds an adjacent vertex. If called without a vertex, it will make an empty set.
        Otherwise self.adjacent is None and assumed to not have been set."""

        if self.adjacent is None:
            self.adjacent = set()
        if vertex is not None:
            self.adjacent.add(vertex)

    def __str__(self):
        return 'V(%s)' % self.id

    __repr__ = __str__

class DirectedVertex(Vertex):
    def __init__(self, id):
        super().__init__(id)
        self.indegrees = None
        self.outdegrees = None

    def add_adjacent(self, direction=None, vertex=None):
        """Adds an adjacent vertex as an indegree or an outdegree. If called without a vertex and without a direction, it will make an empty set for each.
        Otherwise they are both None and assumed to not have been set."""
        super().add_adjacent(vertex)
        if self.indegrees is None:
            self.indegrees = set()
            self.outdegrees = set()

        if vertex is not None:
            if direction == 'in':
                    self.indegrees.add(vertex)
            if direction == 'out':
                self.outdegrees.add(vertex)

class Edge:
    def __init__(self, v1, v2):
        self.id = (v1, v2)
        self.v1 = v1
        self.v2 = v2
    
    def __str__(self):
        return 'Edge(%s,%s)' % self.id

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

    def get_all_degrees(self):
        return [(v, self.get_degrees(v)) for v in self.vertices]

    def get_degrees(self, v):
        if v.adjacent is None and v in self.vertices:
            if isinstance(v, DirectedVertex):
                indegree = 0
                outdegree = 0
                # Initialize each set
                v.add_adjacent('out')
                v.add_adjacent('in')
                for edge in self.edges:
                    if edge.v1 is v:
                        outdegree += 1
                        v.add_adjacent('out', edge.v2)
                    elif edge.v2 is v:
                        indegree += 1
                        v.add_adjacent('in', edge.v1)
                v.degrees = {'indegree': indegree, 'outdegree': outdegree}
            else:
                degree = 0
                for edge in self.edges:
                    if edge.v1 is v or edge.v2 is v:
                        degree += 1
                v.degrees = degree
        
        return v.degrees

    def depth_first(self, vertex, vertices=None, edges=None, visited=set()):
        """Does a depth first search starting at the given vertex. `edges and `vertices` callback functions, if supplied, will be called for each
        edge as it is travelled and each vertex as it is entered"""
        visited.add(vertex)

        if vertex.adjacent is None:
            self.get_degrees(vertex)
        
        if isinstance(vertex, DirectedVertex):
            # Traverse the outdegrees
            for v in vertex.outdegrees:
                if v not in visited:
                    if edges is not None:
                        edges(self.find_edge(vertex, v))
                    if vertices is not None:
                        vertices(v)
                    self.depth_first(v, vertices=vertices, edges=edges, visited=visited)
        else:
            # Traverse all adjacent
            for v in vertex.adjacent:
                if v not in visited:
                    if edges is not None:
                        edges(self.find_edge(vertex, v))
                    if vertices is not None:
                        vertices(v)
                    self.depth_first(v, vertices=vertices, edges=edges, visited=visited)
    
    def find_edge(self, v1, v2):
        edge = None
        expected = (v1, v2)
        for e in self.edges:
            if e.id == expected:
                edge = e
                break
        return edge
    
    def __str__(self):
        return 'G(%s, %s)' % (
            '{%s}' % ', '.join(map(str, self.vertices)),
            '{%s}' % ', '.join(map(str, self.edges))
        )
