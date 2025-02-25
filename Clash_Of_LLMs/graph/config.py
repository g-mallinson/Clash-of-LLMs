import os

# USER PROVIDED PARAMETERS
# ------------------------------------------------------------------------------------------------------------

# (string) Type of graph to create ("erdos-renyi", "r-tree", or "custom")
GRAPH_TYPE = "erdos-renyi"

# (int) Number of nodes in the network
NUM_NODES = 200   

# (float) Probability of creating an edge between two nodes     
EDGE_CREATION_PROB = 0.1

# (int) Branching factor, i.e., number of children that a non-leaf node will have (only for "r-tree" graph)
R_TREE_BRANCHING_FACTOR = 3

# (string) Path to the CSV file containing the network structure (only for "custom" graph)
CSV_PATH = "./network.csv"

# (int) Number of steps to simulate between each message
NUM_STEPS = 10              

# (float) Scaling factor for the logistic function's sensitivity (0 < ALPHA <= 1)             
ALPHA = 0.3                 

# (bool) Assign random colours to the nodes in the network when created (True or False)
RANDOM_START = False

# ------------------------------------------------------------------------------------------------------------

# function to validate the user provided parameters
def validate_params():
    if GRAPH_TYPE not in ["erdos-renyi", "r-tree", "custom"]:
        print("Invalid graph type. Please choose from 'erdos-renyi', 'r-tree', or 'custom'.")
        return False
    
    if NUM_NODES <= 0:
        print("Number of nodes should be a positive integer.")
        return False
    
    if GRAPH_TYPE == "r-tree" and (R_TREE_BRANCHING_FACTOR <= 0 
                                   or not isinstance(R_TREE_BRANCHING_FACTOR, int)):
        print("Branching factor should be a positive integer.")
        return False
    
    if GRAPH_TYPE == "custom" and not os.path.exists(CSV_PATH):
        print("Invalid path to the CSV file.")
        return False
    
    if NUM_STEPS <= 0:
        print("Number of steps should be a positive integer.")
        return False
    
    if not 0 < ALPHA <= 1:
        print("Alpha should be in the range (0, 1).")
        return False
    
    return True