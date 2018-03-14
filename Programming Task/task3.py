import math
import random

from em_algorithm import EMAlgorithm


def random_array(size):
    r = [random.random() for _ in range(size)]
    s = sum(r)
    return [i / s for i in r]


def grid_dist(size):
    return {
        (math.floor(index / size), index % size): value for index, value in enumerate(random_array(size ** 2))
    }


def run(input_data):
    # Run 10 randomly initialised runs:
    for run in range(10):
        print("Random Run", run + 1, ":")

        size = 4

        # Randomly Create Distributions for Initialisation, Emission, Transition..
        em_algorithm = EMAlgorithm(
            input_data,
            grid_dist(size),
            {  # A
                (math.floor(x / size), x % size):
                    grid_dist(size)
                for x in range(size ** 2)
            },
            {
                (math.floor(x / size), x % size): {
                    index - 1: probability
                    for index, probability in enumerate(random_array(3))
                } for x in range(size ** 2)
            }
        )

        em_algorithm.run()
