import math
from em_algorithm import EMAlgorithm


def run(input_data):
    size = 4  # Size of the grid: 4x4

    initialisation_dist = {(math.floor(x / size), x % size): 1 / size**2 for x in range(size**2)}
    transition_dist = {  # A
        (math.floor(x / size), x % size):
            initialisation_dist.copy()
        for x in range(size ** 2)
    }
    emission_dist = {
        (math.floor(x / size), x % size): {
            j - 1: 1 / 3
            for j in range(3)
        } for x in range(size ** 2)
    }

    EMAlgorithm(
        input_data,
        initialisation_dist,
        {  # A
            (math.floor(x / size), x % size):
                initialisation_dist.copy()
            for x in range(size ** 2)
        },
        {
            (math.floor(x / size), x % size): {
                j - 1: 1 / 3
                for j in range(3)
            } for x in range(size ** 2)
        }
    ).run()
