from enum import Enum
import math

class Direction(Enum):
    IDENT = 0
    UP = 2
    LEFT = -1
    DOWN = -2
    RIGHT = 1

#The goal of MLE: find Theta = (Initial, Emission, Transition), such that p(Data | Theta) is maximum

#a -> x: 2
#a -> y: 3
#a -> z: 3


#Coin;
#Theta(pheads, ptails); pheads + ptails = 1

#h, h, h, t, t
#p(Data | Theta)
#p(<h, h, h, t, t> | Theta)
#p(<h, h, h, t, t> | <pheads, ptails>)

# Compute MLEs
def run(input_data):
    initialisation = {}
    initialisation_total = 0

    size = 4  # Size of the Grid; 4x4
    transition = {(math.floor(x / size), x % size): {"total": 0} for x in range(size**2)}
    emission = {(math.floor(x / size), x % size): {"total": 0} for x in range(size**2)}

    for episode in input_data:
        previous_cell = None
        for index, time in enumerate(episode):
            coords = tuple(time['coords'])
            reward = time['reward']

            if previous_cell is None:
                #Initialisation
                initialisation_total += 1
                if coords not in initialisation:
                    initialisation[coords] = 1
                else:
                    initialisation[coords] += 1
            else:
                #Transition
                if coords not in transition[previous_cell]:
                    transition[previous_cell][coords] = 1
                else:
                    transition[previous_cell][coords] += 1
                transition[previous_cell]["total"] += 1

            if reward not in emission[coords]:
                emission[coords][reward] = 1
            else:
                emission[coords][reward] += 1
            emission[coords]["total"] += 1

            previous_cell = coords

    print("\nInitialisation MLE: ")
    for key, value in initialisation.items():
        print("P(h1 = " + str(key) + ") = ", round(value / initialisation_total, 3))

    print("\nTransition MLE: ")
    for origin, value in transition.items():
        print("From", str(origin))

        if len(value) == 1:  # All items contain the TOTAL element
            print("Undefined")

        for destination, count in value.items():
            if destination is not "total":
                print("P(ht+1 = " + str(destination) + " | ht = " + str(origin) + ") =", round(count / value["total"], 3))

        print("")

    print("\nEmission MLE: ")
    for cell, value in emission.items():
        print(str(cell), "emits")

        if len(value) == 1:  # All items contain the TOTAL element
            print("Undefined")

        for emission, count in value.items():
            if emission is not "total":
                pad = ""
                if emission >= 0:
                    pad = " "

                print("P(vt = " + pad + str(emission) + " | ht = " + str(cell) + ") =", round(count / value["total"], 3))

        print("")
