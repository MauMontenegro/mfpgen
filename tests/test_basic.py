from context import mfpgen
from mfpgen.rngenerators.rngenerators import RNGenerators
import pytest

@pytest.fixture
def experiment_handler():
    return [10,20,30],10,"F"

def test_experiment_dimensions(experiment_handler):
    sample_generator = RNGenerators(experiment_handler)
    rnd_generators, sq, grid, N, n_seeds, exp_selected = sample_generator.Create()
    assert len(rnd_generators) == 10 * 3
    assert len(grid) == 3