"""
I have adapted this code to my requirements, but originally it was developed by Max Leiserson!
https://stackoverflow.com/questions/19964266/scipy-dendrogram-to-json-for-d3-js-tree-visualisation
https://gist.github.com/mdml/7537455
Last visited: 23.12.2021
"""

import sys
import json
import scipy.spatial
import scipy.cluster
import matplotlib.pyplot as plt

from functools import reduce


def add_node(node, parent):
    # First create the new node and append it to its parent's children
    newnode = dict(node_id=node.id, children=[])
    parent["children"].append(newnode)

    # Recursively add the current node's children
    if node.left:
        add_node(node.left, newnode)
    if node.right:
        add_node(node.right, newnode)


def label_tree(n, id2name):
    # If the node is a leaf, then we have its name
    if len(n["children"]) == 0:
        leafnames = [id2name[n["node_id"]]]

    # If not, flatten all the leaves in the node's subtree
    else:
        leafnames = reduce(lambda ls, c: ls + label_tree(c, id2name), n["children"], [])

    # Delete the node id since we don't need it anymore and
    # it's a cleaner JSON
    del n["node_id"]

    # Labeling convention: "-"-separated leaf names
    n["name"] = "-".join(sorted(map(str, leafnames)))

    return leafnames


def w2v_to_json(model, name):
    # Expanding python's max recursion limit, if data is >1000
    default_rec = sys.getrecursionlimit()
    if default_rec < len(model.wv.index_to_key):
        sys.setrecursionlimit(len(model.wv.index_to_key) * 2)

    # Cluster hierarchical using scipy
    clusters = scipy.cluster.hierarchy.linkage(model.wv.vectors, method='single')
    t = scipy.cluster.hierarchy.to_tree(clusters, rd=False)

    # Create a Dendro dictionary
    ddata = scipy.cluster.hierarchy.dendrogram(clusters,
                                               orientation='left',
                                               leaf_label_func=lambda v: str(model.wv.index_to_key[v]),
                                               leaf_font_size=5)
                                               # no_plot=True)

    # Create dictionary for labeling nodes by their IDs
    labels = ddata['ivl']
    id2name = dict(zip(range(len(labels)), labels))

    # Draw dendrogram using matplotlib
    #plt.figure(1)
    scipy.cluster.hierarchy.dendrogram(clusters, labels=labels, orientation='left', no_plot=True)
    #plt.show()

    # Initialize nested dictionary for d3, then recursively iterate through tree
    d3dendro = dict(children=[], name="Root1")
    add_node(t, d3dendro)

    label_tree(d3dendro["children"][0], id2name)

    # Output to JSON
    json.dump(d3dendro, open("./json-files/" + name + ".json", "w"), sort_keys=True, indent=4)

    # Resetting max recursion limit
    sys.setrecursionlimit(default_rec)
    
def w2v_to_json_mod(model, name):
    # Expanding python's max recursion limit, if data is >1000
    default_rec = sys.getrecursionlimit()
    if default_rec < len(model.wv.index_to_key):
        sys.setrecursionlimit(len(model.wv.index_to_key) * 2)

    # Cluster hierarchical using scipy
    clusters = scipy.cluster.hierarchy.linkage(model.wv.vectors, method='single')
    t = scipy.cluster.hierarchy.to_tree(clusters, rd=False)

    # Create a Dendro dictionary
    ddata = scipy.cluster.hierarchy.dendrogram(clusters,
                                               #orientation='left',
                                              # truncate_mode = 'lastp',
                                              # p = 5,
                                               leaf_rotation = 90.,
                                               leaf_label_func=lambda v: str(model.wv.index_to_key[v]),
                                               leaf_font_size=5)
                                               # no_plot=True)

    # Create dictionary for labeling nodes by their IDs
    labels = ddata['ivl']
    id2name = dict(zip(range(len(labels)), labels))

    # Draw dendrogram using matplotlib
    plt.figure(1)
    scipy.cluster.hierarchy.dendrogram(clusters, labels=labels, orientation='left', no_plot=True)
    plt.show()
    
    # Initialize nested dictionary for d3, then recursively iterate through tree
    d3dendro = dict(children=[], name="Root1")
    add_node(t, d3dendro)

    label_tree(d3dendro["children"][0], id2name)

    # Output to JSON
    json.dump(d3dendro, open("./json-files/" + name + ".json", "w"), sort_keys=True, indent=4)

    # Resetting max recursion limit
    sys.setrecursionlimit(default_rec)

    return clusters, labels, d3dendro