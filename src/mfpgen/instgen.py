import os
import argparse
import sys
from pathlib import Path

from rngenerators.rngenerators import RNGenerators
from environments.metric_tree import rndtree_metric
from constants import *


def mfptgen():
    args = argParser(sys.argv[:])
    # Generate individual random number generators for each instance
    Generator = RNGenerators(args.grid, args.size, args.load)
    rnd_generators, sq, grid, N, n_seeds, exp_selected = Generator.Create()
    if args.load in ('no', 'false', 'f', 'n', '0', 'False'):
        exp_string = str(n_seeds) + " " + str(sq.entropy) + " " + str(grid) + " " + str(N) + "\n"
        fle = Path('Experiments/Seeds')
        # Write Experiment string
        seeds_file = open(fle, 'a')
        seeds_file.write(exp_string)
        seeds_file.close()
        # Create Master Experiment Path if is new
        # TODO: Number of experiments can ba obtained by the seeds file
        n_experiments = len(next(os.walk('Experiments'))[1])  # Get number of next experiment
        master_path = "Experiments/Experiment_" + str(n_experiments)
        if not os.path.exists(master_path):
            os.mkdir(master_path)
    else:
        master_path: str = "Experiments/Experiment_" + str(exp_selected)
        if not os.path.exists(master_path):
            os.mkdir(master_path)
    # Convert grid string to array
    grid = [int(element) for element in grid.split(",")]

    # Experiment Environment Parameters
    # TODO: Avoid "experiment label in exp_config"
    exp_config = {'experiment': {}}
    exp_config['experiment']['env_type'] = 'rnd_tree'
    exp_config['experiment']['env_metric'] = 'metric'
    exp_config['experiment']['instances'] = N

    # Configurable Experiment Parameters
    exp_config['experiment']['scale'] = SCALE
    exp_config['experiment']['root_degree'] = ROOT_DEGREE
    exp_config['experiment']['Env_Update'] = UPDATE
    exp_config['experiment']['delta'] = [DELTA_DOWN,
                                         DELTA_UP]  # [A,B] We want agent at a distance between A% - B% of total scale
    ############################################
    c = 0
    # Create N instances for each Tree Size Experiment in Grid
    for n_nodes in grid:
        node_path = master_path + "/" + 'Size_' + str(n_nodes) + '/'
        if not os.path.exists(node_path):
            os.mkdir(node_path)
        file = 'img_' + str(n_nodes)
        batch_generators = rnd_generators[c:c + N]  # Partition Generators total/N
        rndtree_metric(exp_config, node_path, file, n_nodes, batch_generators)  # Create Instance
        c += N


def argParser(args):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''\
            Generate Experiment Instances or Load a seed to reproduce 
            previously created instances.
            ''',
        epilog='''python instgen.py -l f -g 10,20,30,40 -s 5'''
    )
    parser.add_argument(
        '--load', '-l', type=str,
        help="Load Experiments or Create New One")
    parser.add_argument(
        '--grid', '-g', type=str,
        help="Set of experiments Tree size")
    parser.add_argument(
        '--size', '-s', type=int,
        help="Number of instances for each node size")
    return parser.parse_known_args(args)[0]


# Init Program
mfptgen()
