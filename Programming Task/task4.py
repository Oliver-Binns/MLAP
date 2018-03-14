import math
import random, pprint

from em_algorithm import EMAlgorithm

walls = [
    [(0, 1), (1, 1)],
    [(0, 2), (1, 2)],
    [(1, 3), (2, 3)],
    [(1, 2), (2, 2)],
    [(3, 2), (3, 1)],
    [(1, 0), (2, 0)]
]


def random_array(size):
    r = [random.random() for _ in range(size)]
    s = sum(r)
    return [i / s for i in r]


def full_grid(size):
    return {
        (math.floor(index / size), index % size): value for index, value in enumerate(random_array(size ** 2))
    }


def is_valid_cell(cell):
    if 0 <= cell[0] <= 3 and 0 <= cell[1] <= 3:
        return True
    return False


def wall_between(cell, cell2):
    if [cell, cell2] in walls:
        return True
    elif [cell2, cell] in walls:
        return True
    return False


def grid_dist(size, cell_no):
    origin = [math.floor(cell_no / size), cell_no % size]
    included = [tuple(origin)]
    for i in range(4):
        adjacent_cell = origin.copy()
        adjacent_cell[int(math.floor(i / 2))] += 1 + ((i % 2) * -2)

        if is_valid_cell(adjacent_cell):
            if not wall_between(tuple(origin), tuple(adjacent_cell)):
                included.append(tuple(adjacent_cell))

    distribution = {
        (math.floor(index / size), index % size): 0
        for index, value in enumerate(random_array(size ** 2))
    }

    probabilities = random_array(len(included))
    for index, cell in enumerate(included):
        distribution[cell] = probabilities[index]
    return distribution


def run(input_data):
    # Run 10 randomly initialised runs:
    for run in range(10):
        print("Random Run", run + 1, ":")
        size = 4

        # Randomly Create Distributions for Initialisation, Emission, Transition..
        em_algorithm = EMAlgorithm(
            input_data,
            full_grid(size),
            {  # A
                (math.floor(x / size), x % size):
                    grid_dist(size, x)
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
