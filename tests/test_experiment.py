from src.mfpgen.rngenerators.rngenerators import RNGenerators
import pytest

@pytest.fixture
def experiment_handler():
    return ["10,20,30",10,"f"]

def test_experiment_dimensions(experiment_handler):
    sample_generator = RNGenerators(experiment_handler[0],experiment_handler[1],experiment_handler[2])
    rnd_generators, sq, grid, N, n_seeds, exp_selected = sample_generator.Create()
    assert len(rnd_generators) == 10 * 3
    assert int(len(rnd_generators)/10) == 3
