from pathlib import Path
import numpy as np

class CreateGenerators:
    """
    Create Random Number Generators

    :param N: Number of Instances generated
    :param Load: Selection fLag for load on experiment or create one
    :param grid: Array of Total Tree Nodes [10 20 30]
    :param n_seeds: Number of existing experiment seeds
    :param exp_selected: Selected Experiment
    """

    def __init__(self, grid, N, Load, defpath=None):
        self.N = N
        self.Load = Load
        self.grid = grid
        self.n_seeds = 0
        self.exp_selected = 0

        if defpath is None:
            path = Path.cwd() / 'Experiments' / "Seeds"
        else:
            path = Path(defpath)

        # Generate a Seed_Sequence with  default entropy
        if self.Load in ('no', 'false', 'f', 'n', '0'):
            self.rnd_sq = np.random.SeedSequence()
            with open(path, 'r') as fp:
                self.n_seeds = len(fp.readlines())
            print("Generating New Seed Sequence: {s}".format(s=self.rnd_sq.entropy))
        # Select from current seed directory to reproduce experiment
        else:
            print("Loading a Seed Sequence")
            if not path.exists() or not path.is_file():
                raise ValueError('Experiment Path either does not exists or is not a File')
            file = open(path, 'rt')
            # Display Seeds with their selection index
            f = file.readlines()
            for line in f:
                print(line)
                self.n_seeds += 1
            file.close()

            while True:
                select = int(input("Insert index for desired seed to reproduce experiment: "))
                self.exp_selected = select
                if select >= 0 and select < self.n_seeds:
                    break
                print('Error: {} is not a valid option, please try again'.format(select))
            print("\nYou have selected experiment: {}".format(f[select]))

            self.grid = f[select].split()[2]
            self.N = int(f[select].split()[3])
            self.rnd_sq = np.random.SeedSequence(int(f[select].split()[1]))

        grid_ = [int(element) for element in self.grid.split(",")]
        self.experiments = len(grid_)
        self.total_instances = self.experiments * self.N

    def Create(self):
        children = self.rnd_sq.spawn(self.total_instances)  # Spawn children for every instance
        generators = [np.random.default_rng(s) for s in children]  # Create default generators for each instance
        return generators, self.rnd_sq, self.grid, self.N, self.n_seeds, self.exp_selected