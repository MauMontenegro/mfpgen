import matplotlib.pyplot as plt
import networkx as nx

def write_FFP_file(dimension, edges, coords, fire, output_path):
    # Format file for c++ program
    with open(output_path, "w") as writer:
        writer.write("DIMENSION: {}\n".format(dimension))
        writer.write("FIRE_START: {}\n".format(fire))
        writer.write("FIREFIGHTER: {}\n".format(dimension))
        # Coord display
        writer.write("DISPLAY_DATA_SECTION\n")
        for i in range(dimension + 1):
            coord = coords[i]
            writer.write("{} {} {}\n".format(i, coord[0], coord[1]))
        # Edge section
        writer.write("EDGE_SECTION\n")
        for e in edges:
            writer.write("{} {}\n".format(e[0], e[1]))


def write_FFP_summary(instance, output_file):
    # Graph Summary file
    with open(output_file, "w") as writer:
        writer.write("TREE SEED: {}\n".format(instance["seed"]))
        writer.write("DIMENSION: {}\n".format(instance["N"]))
        writer.write("FIRE_START: {}\n".format(instance["start_fire"]))
        writer.write("FIREFIGHTER: {}\n".format(instance["N"]))
        writer.write("DELTA: {}\n".format(instance["delta"]))
        writer.write("ROOT DEGREE: {}\n".format(instance["root_degree"]))
        writer.write("MAX DEGREE: {}\n".format(instance["max_degree"]))
        writer.write("TREE HEIGHT: {}\n".format(instance["tree_height"]))
        writer.write("SCALE_DISTANCE: {}\n".format(instance["scale"]))


def DrawingInstance(layout, T, fire, N, path, file):
    """ Draw networkx Tree with current layout and node types

    :param layout: Tree nodes layout positions
    :param T: networkx Tree with agent position included
    :param fire: initial fire node
    :param N: Number of nodes
    :param path: path to save images
    :param file: name of file
    :return:
        List of actual burned nodes at t=0
        List of unlabeled nodes at t=0
    """
    # This is for get max and min labels in plot
    max_x_value = max(d[0] for d in layout.values())
    min_x_value = min(d[0] for d in layout.values())
    max_y_value = max(d[1] for d in layout.values())
    min_y_value = min(d[1] for d in layout.values())

    # Leaving only unlabeled nodes
    remaining_nodes = list(T.nodes)
    remaining_nodes.pop(fire)
    burnt_nodes = [fire]
    remaining_nodes.pop(-1)

    # Drawing Nodes
    fig, ax = plt.subplots()
    options = {"edgecolors": "tab:gray", "node_size": 300, "alpha": 1}
    nx.draw(T, layout, with_labels=True, font_size=10, ax=ax)
    nx.draw_networkx_nodes(T, layout, nodelist=burnt_nodes, node_color='#e33434', label="Ignition", **options)
    nx.draw_networkx_nodes(T, layout, nodelist=[N], node_color='#34e3e0', label="Firefighter", **options)
    nx.draw_networkx_nodes(T, layout, nodelist=remaining_nodes, node_color='#62fa69', label="Remaining", **options)

    # Drawing edges
    nx.draw_networkx_edges(T, layout, width=1.0, alpha=0.8, edge_color='#959895')

    # Labels and scale plotting
    plt.axis('on')
    plt.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
    # plt.xticks(np.arange(min_x_value, max_x_value, 1))
    # plt.yticks(np.arange(min_y_value, max_y_value, 1))
    plt.xlabel('X-Position', fontdict=None, labelpad=5)
    plt.ylabel('Y-Position', fontdict=None, labelpad=5)
    title_label = "MFP Tree Instance with {N} vertices".format(N=N)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    plt.legend(loc="lower left", ncol=1, bbox_to_anchor=(1, 0.5), labelspacing=1)
    plt.title(title_label)
    # nt=Network('500px', '500px')
    # nt.from_nx(T)
    # nt.show('nx.html')

    # Plotting and saving Image
    file_path = path + file + '.png'
    graph = plt.gcf()
    graph.savefig(file_path, format="PNG")
    plt.close()
    return remaining_nodes, burnt_nodes
