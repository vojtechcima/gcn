from ..graph import Arc, ArcType, Node, NodeType, Graph, GraphType, GraphSet
from ..gcn import GCN

import tensorflow as tf
import numpy as np

tf.compat.v1.disable_eager_execution()


def test():
    nt = NodeType(4, name="A")
    n1 = Node(nt, [1,2,3])
    n2 = Node(nt, [1,2,3])
    n3 = Node(nt, [1,2,3])
    at = ArcType(nt, nt, name="A")
    a1 = Arc(at, n1, n2)
    a2 = Arc(at, n1, n3)
    gt = GraphType([nt], [at])
    g = Graph(gt)
    g.add_node(n1)
    g.add_node(n2)
    g.add_node(n3)
    g.add_arc(a1)
    g.add_arc(a2)

def test2():
    def gen_graph():
        nt = NodeType(4, name="A")
        n1 = Node(nt, [1,2,3])
        at = ArcType(nt, nt, name="A")
        a1 = Arc(at, n1, n1)
        gt = GraphType([nt], [at])
        g = Graph(gt)
        g.add_node(n1)
        g.add_arc(a1)
        return g, nt, at
    g1, nt1, at1 = gen_graph()
    g2, _, _ = gen_graph()
    assert len(g1.nodes) == 1
    assert len(g1.arcs) == 1
    assert len(g2.nodes) == 1
    assert len(g2.arcs) == 1
    assert g1.get_nodes_np(nt1).shape == (1, nt1.vector_size)
    assert g1.get_arcs_np(at1).shape == (1, 2)

def test3():
    # Define graph structure
    nt1 = NodeType(16)
    nt2 = NodeType(8)
    at_nt2_nt2 = ArcType(nt2, nt2)
    at_nt1_nt2 = ArcType(nt1, nt2)
    gt = GraphType([nt1, nt2],[at_nt2_nt2, at_nt1_nt2])

    # Create graph instance
    g = Graph(gt)
    god = Node(nt1)
    g.add_node(god)
    for _ in range(3):
        n = Node(nt2)
        g.add_node(n)
        g.add_arc(Arc(at_nt1_nt2, god, n))
    for i in range(len(g.nodes[nt2]) - 1):
        g.add_arc(Arc(at_nt2_nt2, g.nodes[nt2][i], g.nodes[nt2][i+1]))
        g.add_arc(Arc(at_nt2_nt2, g.nodes[nt2][i+1], g.nodes[nt2][i]))
    
    gcn = GCN(gt, 2, {nt1: [tf.keras.layers.Dense(units=32, activation=tf.nn.leaky_relu)],
                      nt2: [tf.keras.layers.Dense(units=16, activation=tf.nn.leaky_relu)]})
    ol = tf.keras.layers.Dense(units=1, activation=tf.nn.sigmoid)

    nn_output = ol(gcn.outputs[nt1])

    labels = tf.compat.v1.placeholder(tf.float32, shape=(None, 1), name="labels")
    loss = tf.compat.v1.losses.mean_squared_error(labels=labels, predictions=nn_output)
    trainer = tf.compat.v1.train.AdamOptimizer().minimize(loss)

    y = np.array([[0.2]])
    y_ = np.array([[0]])

    with tf.compat.v1.Session() as sess:
        tf.compat.v1.global_variables_initializer().run(session=sess)
        for _ in range(500):
            i += 1
            fd = {}
            for nt in g.graph_type.node_types:
                fd[gcn.inputs[nt]] = g.get_nodes_np(nt)
            for at in g.graph_type.arc_types:
                fd[gcn.inputs[at]] = g.get_arcs_np(at)
            fd[labels] = y
            _, y_, _ = sess.run([loss, nn_output, trainer], feed_dict=fd)
    assert round(y[0, 0] - y_[0, 0], 2) == 0.00


def test4():
    # Define graph structure
    nt1 = NodeType(8)
    at_right = ArcType(nt1, nt1)
    at_left = ArcType(nt1, nt1)
    gt = GraphType([nt1], [at_left, at_right])
    g = Graph(gt)

    # Create graph instance
    for _ in range(3):
        n = Node(nt1)
        g.add_node(n)
    for i in range(len(g.nodes[nt1]) - 1):
        g.add_arc(Arc(at_right, g.nodes[nt1][i], g.nodes[nt1][i+1]))
        g.add_arc(Arc(at_left, g.nodes[nt1][i+1], g.nodes[nt1][i]))
    
    assert len(g.nodes[nt1]) == 3

    gcn = GCN(gt, 3, {nt1: [tf.keras.layers.Dense(units=32, activation=tf.nn.leaky_relu)]})
    ol = tf.keras.layers.Dense(units=1,activation=tf.nn.sigmoid)

    nn_output = ol(gcn.outputs[nt1])
    print(nn_output)

    labels = tf.compat.v1.placeholder(tf.float32, shape=(None, 1), name="labels")
    loss = tf.compat.v1.losses.mean_squared_error(labels=labels, predictions=nn_output)
    trainer = tf.compat.v1.train.AdamOptimizer().minimize(loss)

    y = np.array([[0.2], [0.9], [0.4]])
    #y_ = np.array([[0]])

    with tf.compat.v1.Session() as sess:
        tf.compat.v1.global_variables_initializer().run(session=sess)
        #for _ in range(500):
        for _ in range(500):
            i += 1
            fd = {}
            for nt in g.graph_type.node_types:
                fd[gcn.inputs[nt]] = g.get_nodes_np(nt)
            for at in g.graph_type.arc_types:
                fd[gcn.inputs[at]] = g.get_arcs_np(at)
            fd[labels] = y
            print(len(g.nodes[nt1]))
            print(fd)
            l, y_, _, o = sess.run([loss, nn_output, trainer, gcn.outputs[nt1]], feed_dict=fd)
            print(l)
            print(y_)
            print(o)
    assert round(y[0, 0] - y_[0, 0], 2) == 0.00


def test5():
    def gen_graph(graph_type, n_nodes):
        g = Graph(graph_type)
        god = Node(graph_type.node_types[1])
        g.add_node(god)
        for _ in range(n_nodes):
            n = Node(graph_type.node_types[0])
            g.add_node(n)
            g.add_arc(Arc(graph_type.arc_types[1], god, n))
        for i in range(len(g.nodes[nt1]) - 1):
            g.add_arc(Arc(graph_type.arc_types[0], g.nodes[nt1][i], g.nodes[nt1][i+1]))
            g.add_arc(Arc(graph_type.arc_types[0], g.nodes[nt1][i+1], g.nodes[nt1][i]))
        return g

    nt1 = NodeType(4)
    nt2 = NodeType(8)
    at_nt1_nt1 = ArcType(nt1, nt1)
    at_nt2_nt1 = ArcType(nt2, nt1)
    gt = GraphType([nt1, nt2],[at_nt1_nt1, at_nt2_nt1])
    g1 = gen_graph(gt, 2)
    assert g1.get_nodes_np(nt1).shape == (2, 4)
    assert g1.get_nodes_np(nt2).shape == (1, 8)
    assert g1.get_arcs_np(at_nt1_nt1).shape == (2, 2)
    assert g1.get_arcs_np(at_nt2_nt1).shape == (2, 2)
    g2 = gen_graph(gt, 3)
    assert g2.get_nodes_np(nt1).shape == (3, 4)
    assert g2.get_arcs_np(at_nt1_nt1).shape == (4, 2)
    assert g2.get_arcs_np(at_nt2_nt1).shape == (3, 2)
    g1.append(g2)
    assert g1.get_nodes_np(nt1).shape == (5, 4)
    assert np.all(g1.get_arcs_np(at_nt1_nt1) == np.array([[0, 1], [1, 0],[2, 3], [3, 2], [3, 4], [4, 3]]))
    assert g1.get_arcs_np(at_nt1_nt1).shape == (6, 2)
    assert g1.get_arcs_np(at_nt2_nt1).shape == (5, 2)


def test6():
    nt1 = NodeType(4)
    nt2 = NodeType(8)
    at_bi = ArcType(nt1, nt2, bidirectional=True)
    gt = GraphType((nt1, nt2), (at_bi,))
    n1 = Node(nt1)
    n2 = Node(nt1)
    n3 = Node(nt2)
    a1 = Arc(at_bi, n1, n3)
    a2 = Arc(at_bi, n2, n3)
    g = Graph(gt)
    g.add_node(n1)
    g.add_node(n2)
    g.add_node(n3)
    g.add_arc(a1)
    g.add_arc(a2)

    gcn = GCN(gt, 3, {nt1: [tf.keras.layers.Dense(units=32, activation=tf.nn.leaky_relu)],
                      nt2: [tf.keras.layers.Dense(units=32, activation=tf.nn.leaky_relu)]})
    ol = tf.keras.layers.Dense(units=1,activation=tf.nn.sigmoid)

    nn_output = ol(gcn.outputs[nt2])
    print(nn_output)

    labels = tf.compat.v1.placeholder(tf.float32, shape=(None, 1), name="labels")
    loss = tf.compat.v1.losses.mean_squared_error(labels=labels, predictions=nn_output)
    trainer = tf.compat.v1.train.AdamOptimizer().minimize(loss)

    y = np.array([[2.0]])

    with tf.compat.v1.Session() as sess:
        tf.compat.v1.global_variables_initializer().run(session=sess)
        for _ in range(1):
            fd = {}
            for nt in g.graph_type.node_types:
                fd[gcn.inputs[nt]] = g.get_nodes_np(nt)
            for at in g.graph_type.arc_types:
                fd[gcn.inputs[at]] = g.get_arcs_np(at)
            fd[labels] = y
            #print(len(g.nodes[nt1]))
            #print(fd)
            l, y_, _, o = sess.run([loss, nn_output, trainer, gcn.outputs[nt2]], feed_dict=fd)
            #print(l)
            #print(y_)
            #print(o)


def test7():
    nt1 = NodeType(4)
    at1 = ArcType(nt1, nt1)
    gt = GraphType((nt1,), (at1,))

    gcn = GCN(gt, 1, {nt1: [tf.keras.layers.Dense(units=32, activation=tf.nn.leaky_relu)]})

    ol = tf.keras.layers.Dense(units=1,activation=tf.nn.sigmoid)
    nn_output = ol(gcn.outputs[nt1])

    labels = tf.compat.v1.placeholder(tf.float32, shape=(None, 1), name="labels")
    loss = tf.compat.v1.losses.mean_squared_error(labels=labels, predictions=nn_output)
    trainer = tf.compat.v1.train.AdamOptimizer().minimize(loss)

    y = np.array([[2.0]])

    g = Graph(gt)

    assert g.get_arcs_np(at1).shape == (0, 2)
    assert g.get_nodes_np(nt1).shape == (0, 4)

    with tf.compat.v1.Session() as sess:
        tf.compat.v1.global_variables_initializer().run(session=sess)
        for _ in range(1):
            fd = {}
            for nt in g.graph_type.node_types:
                fd[gcn.inputs[nt]] = g.get_nodes_np(nt)
            for at in g.graph_type.arc_types:
                fd[gcn.inputs[at]] = g.get_arcs_np(at)
            fd[labels] = y
            l, y_, _, o = sess.run([loss, nn_output, trainer, gcn.outputs[nt]], feed_dict=fd)


def test8():
    def gen_graph(gt, nt1, at1):
        n1 = Node(nt1)
        n2 = Node(nt1)
        n3 = Node(nt1)
        a1 = Arc(at1, n1, n3)
        a2 = Arc(at1, n2, n3)
        g = Graph(gt)
        g.add_node(n1)
        g.add_node(n2)
        g.add_node(n3)
        g.add_arc(a1)
        g.add_arc(a2)
        return g
    nt1 = NodeType(4)
    at1 = ArcType(nt1, nt1)
    gt = GraphType((nt1,), (at1,))
    graphs = [gen_graph(gt, nt1, at1) for _ in range(10)]
    labels = [[i] for i in range(10)]
    gs = GraphSet(graphs, labels)
    batch, labels, completed = gs.next_batch(10)
    assert len(labels) == 10
    assert completed == True
    assert gs.cursor == 0
    batch, labels, completed = gs.next_batch(4)
    assert len(labels) == 4
    assert isinstance(batch, Graph)
    assert len(batch.nodes[nt1]) == 4 * 3
    assert len(batch.arcs[at1]) == 4 * 2
    assert completed == False
    assert gs.cursor == 4
    batch, labels, completed = gs.next_batch(6)
    assert len(labels) == 6
    assert completed == True
    assert len(batch.nodes[nt1]) == 6 * 3
    assert len(batch.arcs[at1]) == 6 * 2
    assert gs.cursor == 0
    batch, labels, completed = gs.next_batch(2)
    assert len(labels) == 2
    assert completed == False
    assert len(batch.nodes[nt1]) == 2 * 3
    assert len(batch.arcs[at1]) == 2 * 2
    assert gs.cursor == 2
    batch, labels, completed = gs.next_batch(10)
    assert len(labels) == 8
    assert completed == True
    assert len(batch.nodes[nt1]) == 8 * 3
    assert len(batch.arcs[at1]) == 8 * 2
    assert gs.cursor == 0
    all_samples, labels = gs.get_all_samples()
    assert len(labels) == 10
    assert len(all_samples.nodes[nt1]) == 10 * 3
    assert len(all_samples.arcs[at1]) == 10 * 2
