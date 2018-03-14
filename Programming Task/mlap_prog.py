import sys
import task1
import task2
import task3
import task4


# Converts the raw input in the .dat file into an array of episodes
def decode_data(coords_given, raw_input):
    input_data = []
    current_episode = []
    
    for line in raw_input.split("\n"):
        if not line.strip():
            input_data.append(current_episode)
            current_episode = []
            continue
            
        if coords_given:
            split_line = line.split(" ")
        
            coords = []
            coord_vals = split_line[0].split(",")
            for coord in coord_vals:
                coord_val = coord.replace("(", "").replace(")", "")
                coords.append(int(coord_val))

            current_episode.append({"coords": coords, "reward": int(split_line[1])})
        else:
            current_episode.append({"reward": int(line)})
    
    # Removes any empty episodes from the array
    input_data.remove([])
    return input_data

arguments = sys.argv
arguments.pop(0)

if len(arguments) != 2:
    raise Exception("Exactly two input parameters should be given - the task number (1-4) and a data file.")

try:
    program = int(arguments[0])
    
    with open(arguments[1], 'r') as f:
        raw_input = f.read()
        
        coords_given = True         # Coords given in data file 1
        if 1 < program <= 4 or arguments[1] == 'task2.dat':
            coords_given = False    # Coords NOT given in data file 2
        elif program != 1 or arguments[1] != 'task1.dat':
            raise Exception("Unknown data file.")
        input_data = decode_data(coords_given, raw_input)

        tasks = {
            2: task2,
            3: task3,
            4: task4
        }
        if program == 1 and coords_given:
            task1.run(input_data)
        elif not coords_given:
            tasks[program].run(input_data)
        else:
            if 1 <= program <= 4:
                raise Exception("Incorrect data file given for this task.")
            else:
                raise Exception("Task specified (" + str(program) + ") could not be found.")
except ValueError:
    raise Exception("First argument should be an integer value specifying the task to run.")
