import numpy as np
import json
import os
import networkx as nx

class ExperimentLog:
    """
    A class used to save experiment information
    Attributes
    ----
    path: str
        formatted string that contains the path of saved instance
    file_name: str
        formatted string that contains the name of saved instance file

    Methods
    ---
    log_save(stats)
        Save .json file containing instance parameters
    """

    def __init__(self, path, file_name):
        """
        :param path: str
             formatted string that contains t
        :param file_name: str
            formatted string that contains the name of saved instance file
        """
        self.path = path
        self.file = file_name + '.json'
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.full_path = os.path.join(self.path, self.file)

    def log_save(self, stats):
        with open(self.full_path, 'w') as fp:
            json.dump(stats, fp)


def rndtree_metric(config, path, file, n_nodes, rnd_generators):
    """ Creates N instances for a determined Size Tree with metric distances.

    Create a random 'networkx' tree object, adds an external 'agent' node, and fill his original adjacency matrix
    with escalated metric distances between all nodes. Also, saves instance parameters and draws initial graph
    configuration.

    Parameters
    ---------------
    :param config: dic
        A dictionary containing experiment configuration variables
    :param path: str
        Path to save instance
    :param file: str
        Contains the file name
    :param n_nodes: int
        Total number of nodes in graph
    :param rnd_generators: default_generator
        batch of N random number generators for each instance
    :return:
        Initial_agent_position: int array
        Node_List: dic
        Forest: ete3
        time: int
        max_budget: int
        Config: Array containing environment or metric config
        Plotting: Array containing drawing config
    """
    for instance in range(config['experiment']['instances']):
        instance_path = path + "Instance_" + str(instance) + "/"  # Create Instance Specific Folder
        N = n_nodes
        n_instances = config['experiment']['instances']  # Number of instances per Node Size
        scale = config['experiment']['scale']  # Edge distance scale
        r_degree = config['experiment']['root_degree']  # Force Tree to have a root degree of this size
        env_update = config['experiment']['Env_Update']  # Update ratio of environment respect to agent
        delta = config['experiment']['delta']

        # Random Variables. Use rnd_generator specific to each instance.
        # Generate Only Trees with fire root node with desired degree
        starting_fire = rnd_generators[instance].integers(0, N - 1)
        rootd_check = True
        while rootd_check:
            tree_seed = rnd_generators[instance].integers(2 ** 32 - 1)
            T = nx.random_tree(n=N, seed=int(tree_seed))
            pos = nx.spring_layout(T, seed=int(tree_seed), scale=scale)  # Use a spring layout to draw nodes
            if T.degree[starting_fire] == r_degree:
                rootd_check = False
        # Limit agent distance from root
        limit_agent_radius_inf = delta[0] * scale
        limit_agent_radius_sup = delta[1] * scale

        # Needed Structures
        T_Ad = np.zeros((N + 1, N + 1))  # Adjacency Matrix that contains distances for all nodes including agent
        all_nodes = {}  # Dictionary to store all nodes
        saved_nodes = []  # Array of saved nodes for Drawing
        initial_pos = N  # Put agent as last node in Graph
        instance_ = {}  # dictionary to save instance parameters

        # Save Instance
        logger = ExperimentLog(instance_path, 'instance_info')  # Create Logger Class to store instance parameters

        # Fill Adjacency Matrix with escalated distances in layout (without agent)
        for row in range(0, N):
            for column in range(row, N):
                if row == column:
                    T_Ad[row][column] = 0
                else:
                    x_1 = pos[row][0]
                    x_2 = pos[column][0]
                    y_1 = pos[row][1]
                    y_2 = pos[column][1]
                    T_Ad[row][column] = np.sqrt((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2)

        # Force agent to be at limit distance from ignition vertex
        ref_x, ref_y = pos[starting_fire][0], pos[starting_fire][1]  # Get ignition vertex position reference
        x_offset = rnd_generators[instance].uniform(limit_agent_radius_inf, limit_agent_radius_sup)
        if rnd_generators[instance].random() < 0.5:
            x_offset = x_offset * -1
        y_offset = rnd_generators[instance].uniform(limit_agent_radius_inf, limit_agent_radius_sup)
        if rnd_generators[instance].random() < 0.5:
            y_offset = y_offset * -1
        a_x_pos = ref_x + x_offset
        a_y_pos = ref_y + y_offset

        # Adding Agent Node to Full Adjacency Matrix (Agent is added to last row and column 'N')
        for node in range(0, N):
            x_1 = pos[node][0]
            x_2 = a_x_pos
            y_1 = pos[node][1]
            y_2 = a_y_pos
            T_Ad[node][N] = np.sqrt((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2)

        # Create a Symmetric Matrix with upper part of T_Ad (For symmetric distances)
        T_Ad_Sym = np.triu(T_Ad) + np.tril(T_Ad.T)

        # Add Agent Node to Tree and add his escalated position
        T.add_node(N)
        pos[N] = [a_x_pos, a_y_pos]

        # Draw Instance
        remaining_nodes, burnt_nodes = DrawingInstance(pos, T, starting_fire, N, instance_path, file)

        levels = nx.single_source_shortest_path_length(T, starting_fire)  # Level of nodes in rooted Tree
        root_degree = T.degree[starting_fire]
        degrees = list(T.degree)  # Degree of each node in rooted Tree
        max_degree = max(degrees, key=lambda item: item[1])[1]
        max_level = max(levels.values())  # Level of Tree

        nx.write_adjlist(T, instance_path + 'MFF_Tree.adjlist')  # Saving Full Distance Matrix
        np.save(instance_path + "FDM_MFFP.npy", T_Ad_Sym)  # Saving Numpy array full distance matrix

        # Instance Variables
        instance_['N'] = N
        instance_['seed'] = int(tree_seed)
        instance_['scale'] = scale
        instance_['start_fire'] = int(starting_fire)
        instance_['a_pos_x'] = int(a_x_pos)
        instance_['a_pos_y'] = int(a_y_pos)
        instance_['tree_height'] = max_level
        instance_['root_degree'] = root_degree
        instance_['max_degree'] = max_degree
        instance_['delta'] = T_Ad[starting_fire][N]
        logger.log_save(instance_)

        # Save position layout as .json file
        for element in pos:
            pos[element] = list(pos[element])
        with open(instance_path + 'layout_MFF.json', 'w') as layout_file:
            layout_file.write(json.dumps(pos))
        layout_file.close()

        # File created for Backtracking Algorithm
        output_file = instance_path + "BCKTRCK.mfp"
        write_FFP_file(n_nodes, T.edges(), pos, starting_fire, output_file)

        # CREATE A SUMMARY FILE FOR EACH INSTANCE
        output_file = instance_path + "SUMMARY.mfp"
        write_FFP_summary(instance_, output_file)
