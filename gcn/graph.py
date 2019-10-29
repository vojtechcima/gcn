import numpy as np


class ArcType:
    def __init__(self, from_nt, to_nt, name="", bidirectional=False):
        assert isinstance(from_nt, NodeType)
        assert isinstance(to_nt, NodeType)
        self.name = name
        self.from_nt = from_nt
        self.to_nt = to_nt
        self.counter = 0
        self.bidirectional = bidirectional


class Arc:
    def __init__(self, arc_type, from_node, to_node):
        assert isinstance(arc_type, ArcType)
        assert isinstance(from_node, Node)
        assert isinstance(to_node, Node)
        assert from_node.node_type == arc_type.from_nt
        assert to_node.node_type == arc_type.to_nt
        self.arc_type = arc_type
        self.from_node = from_node
        self.to_node = to_node
        self.id = self.arc_type.counter
        self.arc_type.counter += 1


class NodeType:
    def __init__(self, vector_size, name=""):
        self.name = name
        self.vector_size = vector_size
        self.counter = 0


class Node:
    def __init__(self, node_type, values=None):
        assert isinstance(node_type, NodeType)
        if not values:
            values = []
        assert len(values) <= node_type.vector_size
        self.node_type = node_type
        self.values = np.concatenate((np.array(values), np.zeros(node_type.vector_size - len(values))))
        self.id = self.node_type.counter
        self.node_type.counter += 1


class GraphType:
    def __init__(self, node_types, arc_types):
        self.node_types = node_types
        self.arc_types = arc_types


class Graph:
    def __init__(self, graph_type):
        assert isinstance(graph_type, GraphType)
        self.nodes = {}
        self.arcs = {}
        self.graph_type = graph_type
        for at in graph_type.arc_types:
            self.arcs[at] = []
        for nt in graph_type.node_types:
            self.nodes[nt] = []

    def add_arc(self, arc):
        assert isinstance(arc, Arc)
        self.arcs[arc.arc_type].append(arc)

    def add_node(self, node):
        assert isinstance(node, Node)
        self.nodes[node.node_type].append(node)

    def get_nodes_np(self, node_type):
        assert isinstance(node_type, NodeType)
        nodes = []
        for n in self.nodes[node_type]:
            nodes.append(n.values)
        return np.array(nodes)

    def append(self, graph):
        assert isinstance(graph, Graph)
        assert graph.graph_type == self.graph_type
        for nt in graph.nodes:
            self.nodes[nt] += graph.nodes[nt]
        for at in graph.arcs:
            self.arcs[at] += graph.arcs[at]

    def get_arcs_np(self, arc_type, idx_shift_from=0, idx_shift_to=0):
        assert isinstance(arc_type, ArcType)
        arcs = []
        for a in self.arcs[arc_type]:
            arcs.append([self.nodes[arc_type.from_nt].index(a.from_node) + idx_shift_from,
                         self.nodes[arc_type.to_nt].index(a.to_node) + idx_shift_to])
        return np.array(arcs)

    def get_nodes_degrees(self):
        degrees = {}
        for at in self.arcs:
            if at.from_nt not in degrees:
                degrees[at.from_nt] = {}
            for a in self.arcs[at]:
                if a.from_node not in degrees[at.from_nt]:
                    degrees[at.from_nt][a.from_node] = 0
                degrees[at.from_nt][a.from_node] += 1
        return degrees
