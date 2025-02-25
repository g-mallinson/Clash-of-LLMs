import time
from Clash_Of_LLMs.backend.graph.simulator import Network
import pyvis.network
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from config import *

TEST_MESSAGE_POTENCY = 0.8

network = Network()
network.current_step = 0
network.initialise_node_attributes()
network.initialise_edge_weights()
team_nodes = network.source_nodes

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(15, 9))
pos = nx.spring_layout(network.graph, iterations=15, seed=42)
ax.axis('off')
plot_options = {"node_size": 10}
# Draw the initial graph
colour = [network.get_colour(node) for node in network.graph.nodes]
nx.draw(network.graph, pos=pos, node_color=colour, **plot_options)
# Draw source nodes with larger circles and a label
source_nodes = [node for node in network.graph.nodes if node in team_nodes]
source_node_colours = [network.get_colour(node) for node in source_nodes]
nx.draw_networkx_nodes(network.graph, pos=pos, nodelist=source_nodes, node_size=50, node_color=source_node_colours, ax=ax)


def update(num):
    if network.current_step % NUM_STEPS == 0:
        if network.prev_turn == "red":
            network.current_turn = "blue"
        else:
            network.current_turn = "red"
        network.reset_visited()
            
    # Track nodes that change colour
    changed_nodes = network.simulate_diffusion_step(network.current_turn, ALPHA, TEST_MESSAGE_POTENCY)
    
    # Update only the nodes that changed colour
    if changed_nodes:
        for node in changed_nodes:
            colour = network.get_colour(node)
        nx.draw_networkx_nodes(network.graph, pos=pos, nodelist=[node], node_color=colour, **plot_options)
    
    time.sleep(0.1)
    


# Animate the graph
ani = FuncAnimation(fig, update, save_count=50, repeat=False)

# Show the animation
plt.show()
