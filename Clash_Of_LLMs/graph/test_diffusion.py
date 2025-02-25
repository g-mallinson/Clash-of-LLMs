from matplotlib import pyplot as plt
import networkx as nx
from Clash_Of_LLMs.backend.graph.simulator import Network
import numpy as np
import imageio
import os

def get_color(graph):
    color_dict = dict({0:"red",1:"blue",2:"grey"})
    color = list(dict(graph.nodes(data="visited")).values())
    color = [color_dict[i] for i in color]
    return color

def makeGif(networks, name):
    os.mkdir("frames")
    
    counter=0
    images = []
    for i in range(0,len(networks)):
        plt.figure(figsize = (8,8))

        colour = get_color(networks[i])
        pos = nx.kamada_kawai_layout(networks[i])
        nx.draw(networks[i],  node_color = colour, arrowsize=20, pos = pos)
        plt.savefig("frames/" + str(counter)+ ".png")
        images.append(imageio.imread("frames/" + str(counter)+ ".png"))
        counter += 1
        plt.close()

    imageio.mimsave(name, images)

    os.rmdir("frames")

network = Network()
network.init_sources()

for i in range(0, 100):
    network.add_node()

nodes = list(network.graph.nodes)
for i in range(0, 300):
    if i == 0:
        node_1 = nodes[0]
    else:
        node_1 = np.random.choice(nodes)
    
    node_2 = np.random.choice(nodes)
    
    if node_1 != node_2:
        network.add_edge(node_1, node_2)
        

pos = nx.kamada_kawai_layout(network.graph)
colour = [network.get_colour(node) for node in network.graph.nodes]
plt.figure(figsize=(12, 12))
nx.draw(network.graph, pos=pos, node_color=colour)


visited = []
networks = [network.graph.copy()]
for i in range(0, 50):
    network.simulate_spread(0.5, 0.01)
    visited.append(sum(list(dict(network.graph.nodes(data="visited")).values())))
    networks.append(network.graph.copy())
    
plt.figure(figsize=(12, 12))
colour = [network.get_colour(node) for node in network.graph.nodes]

nx.draw(network.graph, pos=pos, node_color=colour)

plt.figure()
t = np.arange(0,len(visited),1)
plt.plot(t, visited)
plt.xlabel("Time")
plt.ylabel("Visited Nodes")
plt.title("Information Spread Over Time")

plt.show()

makeGif(networks, "network.gif")