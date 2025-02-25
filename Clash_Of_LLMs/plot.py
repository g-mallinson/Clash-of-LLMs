from enum import Enum
from numpy import random
from pyvis.network import Network
import networkx as nx
import io
import time
import csv

blueSideColour = "#0571b0"
redSideColour = "#ca0020"
undecidedColour = "#bababa"
   
backgroundColour = "#222222"            

def getRandomTeamColour():
    """
    randomly choose one of the team colours
    
    Returns:
        a randomly chosen colour representing the blue side, red side or undecided
    """
    side = random.randint(0, 3)
    if (side == 0):
         return blueSideColour
    if (side == 1):
        return redSideColour
    if (side == 2):
        return undecidedColour
        

class GameGraph:
    def __init__(self):
        self.network = Network("100%", "100%", bgcolor=backgroundColour)
        self.network.inherit_edge_colors(False)
        
    def exportGraphAsCSV(self, outputPath):
        """
        export the current graph as a CSV file
        
        Args:
            outputPath (string): path to the output file

        Returns:
            Bool: True if the export is successful, False if an error occured
        """
        # 'rows' key is the node name, and the value is an array of the node name, colour and edges
        # rows structure example: {0: [0, 'red', '1,2'], 1: [1, 'grey', '0,'], 2: [2, 'blue', '1,']}
        rows = {}
        
        # add the node colours to 'rows' and setup the node connections string
        for node in self.graph.nodes.items():
            # 'node' structure example: (0, {'color': 'red', 'size': 10})
            # first value is it's name, second is a dictionary of node data
            nodeName = node[0]
            nodeColour = node[1]["color"]
            rows[nodeName] = [nodeName, nodeColour, ""]
        
        # add all edges to the rows dictionary
        for edge in self.graph.edges.items():
            # 'edge' structure example: ((1, 4), {'width': 1})
            # first value is a tuple if the source and destination node, second is a dictionary of edge data
            nodeSource = edge[0][0]
            nodeDestination = edge[0][1]
            rows[nodeSource][2] += f"{nodeDestination},"
        
        try:
            # write the dictionary to a CSV file
            with open(outputPath, 'w', newline='') as file: # newline='' is required, otherwise extra lines will be added to the CSV
                csvwriter = csv.writer(file)
                for row in rows.values():
                    csvwriter.writerow(row)
        except:
            print("unable to write row to CSV export file.")      
            return False
    
        return True  
    
    def importCSVGraph(self, inputPath):
        """
        Import a graph from a CSV file.
        CSV structure:
            Column 1: (string) Name of the node
            Column 2: (string) Colour of the node
            Column 3: {string) Comma-seperated list of node names that the current node connects to
        E.g.
            1,red,"1,2,3,4,"
            2,blue,"2,"
            3,grey,"4,"
            4,red,"3,1"
        
        Args:
            inputPath (string): path to the CSV file being imported

        Returns:
            Bool: true if importing succeeded, false if it failed
        """
        self.graph = nx.Graph()
        
        try:
            with open(inputPath, 'r') as file:
                csvreader = csv.reader(file)
                for row in csvreader:
                    if len(row) != 3:
                        print("CSV isn't formatted correctly.")
                        return False
                    
                    name = row[0]
                    colour = row[1]
                    connections = row[2]
                    
                    connectionsList = []
                    try:
                        for connection in connections.split(','):
                            if connection == '': # prevents the extra comma from being added
                                continue
                            
                            connectionsList.append(int(connection))
                    except:
                        print("CSV has an invalid connection.")
                        return False
                    
                    self.graph.add_node(name, color=colour)
                    for connection in connectionsList:
                        self.graph.add_edge(name, connection)
        except:
            print("unable to open CSV file.")      
            return False
        
        return True
    
    def load_external_graph(self, external_graph):
        """
        load an external graph into the current graph

        Args:
            external_graph (NetworkX graph): the graph to be loaded
        """
        self.graph = external_graph
        
    
    def setNodeColour(self, nodeIndex, colour):
        """set a node's colour

        Args:
            nodeIndex (int): index of the node
            colour (string): the node colour
        """
        self.graph.nodes[nodeIndex]["color"] = colour
    
    # 
    def randomiseNodeColours(self):
        """
        randomise the current node colours
        """
        for nodeIndex in range(self.graph.number_of_nodes()):
            self.setNodeColour(nodeIndex, getRandomTeamColour())
    
    def createErdosRenyiGraph(self, nodeCount, edgeCreationProbability = 0.1):
        """
        create an Erdos Renyi graph. Client recommended this graph.

        Args:
            nodeCount (int): count of nodes in the graph
            edgeCreationProbability (float, optional): probability of an edge between two nodes being created (default is 0.1)
        """
        self.graph = nx.erdos_renyi_graph(nodeCount, edgeCreationProbability)
        self.randomiseNodeColours()

    def createRaryTreeGraph(self, nodeCount, nodeChildCount = 3):
        """
        create a rary tree graph. Simple and easily visualised.

        Args:
            nodeCount (int): count of nodes in the graph
            nodeChildCount (int, optional): count of children that a non-leaf node will have (default is 3)
        """
        self.graph = nx.full_rary_tree(nodeChildCount, nodeCount)
        self.randomiseNodeColours()
        
    def createLobsterGraph(self, expectedNodeCount):
        """
        create a lobster graph. Graph can be randomly small or large, and can slow initial graph loading down if it is large.
        More for fun than functionality as the graph topology can be interesting.

        Args:
            expectedNodeCount (int): expected number of nodes in the graph.
        """
        # I've used 0.6 and 0.1 as probabilities as they gve a good mix of graphs.
        # Some probabilites make massive graphs, so i thought it was best to not allow the user to change it
        self.graph = nx.random_lobster(expectedNodeCount, 0.6, 0.1)
        self.randomiseNodeColours()
    
    def createDuplicationDivergenceGraph(self, nodeCount, keepEdgeProbability = 0.3):
        """
        create a duplication divergence graph. Inspired by biological networks.

        Args:
            nodeCount (int): count of nodes in the graph
            keepEdgeProbability (float, optional): probability of duplicated node edges staying connected (default is 0.3)
        """
        self.graph = nx.duplication_divergence_graph(nodeCount, keepEdgeProbability)
        self.randomiseNodeColours()
    
    def createConnectedCavemanGraph(self, groupCount, groupSize):
        """
        create a connected caveman graph. Each group is mostly isolated from the other groups.

        Args:
            groupCount (int): number of groups in the graph
            groupSize (int): count of nodes in each group
        """
        self.graph = nx.connected_caveman_graph(groupCount, groupSize)
        self.randomiseNodeColours()
        
    def createSmallWorldGraph(self, nodeCount, nodeEdgeCount = 3, edgeRewireProbability = 0.2):
        """
        create a Newman Watts Strogatz (Small World) graph. Seen in neural networks and neuron topologies.

        Args:
            nodeCount (int): count of nodes in the graph
            nodeEdgeCount (int, optional): count of edges that a node has (Default is 3)
            edgeRewireProbability (float, optional): probability that an edge is re-wired to another node (Default is 0.2)
        """
        self.graph = nx.newman_watts_strogatz_graph(nodeCount, nodeEdgeCount, edgeRewireProbability)
        self.randomiseNodeColours()
    
    def createBarabasiAlbertGraph(self, nodeCount, nodeConnectionCount = 2):
        """
        create a Barabasi Albert graph. Simulates a network with a few "popular" nodes that have more conenctions than others.

        Args:
            nodeCount (int): count of nodes in the graph
            nodeConnectionCount (int, optional): count of the edges nodes have when initially generated (default is 2)
        """
        self.graph = nx.barabasi_albert_graph(nodeCount, nodeConnectionCount)
        self.randomiseNodeColours()
    
    def getNodeCount(self):
        """
        get the current graph's node count

        Returns:
            int: the count of nodes in the current graph
        """
        return self.graph.number_of_nodes()
    
    def to_html(self):
        """
        exports a HTML representation of the graph

        Returns:
            string: the converted HTML graph
        """
        self.network.from_nx(self.graph)
        return self.network.generate_html()
    
    def showGraphLocally(self):  
        """
        for testing only, opens the current graph as a local webpage
        """
        self.network.from_nx(self.graph)
        self.network.show('nx.html', notebook=False)

def demoPlotFunctionality():
    """
    for testing only, used to test the graph functionality
    """
    graph = GameGraph()
    graph.createErdosRenyiGraph(20)
    
    for i in range(3):
        graph.showGraphLocally()
        
        side = random.randint(0, 3)
        nodeIndex = random.randint(0, graph.getNodeCount())
        
        if (side == 0):
            graph.setNodeColour(nodeIndex, blueSideColour)
        if (side == 1):
            graph.setNodeColour(nodeIndex, redSideColour)
        if (side == 2):
            graph.setNodeColour(nodeIndex, undecidedColour)


def render_graph(n, p):
    """
    generates a new graph and renders it as HTML

    Returns:
        string: HTML representation of the graph
    """
    game_graph = GameGraph()
    game_graph.createErdosRenyiGraph(n, p)
    graph_html = game_graph.to_html()

    start = graph_html.index("<div class=\"card\" style=\"width: 100%\">")
    return graph_html[start:]

def demoCSVImporting():
    """
    for testing only, used to test the graph import function
    """
    graph = GameGraph()
    if graph.importCSVGraph("C:\\Users\\LJ\\Desktop\\output.csv") == True:
        graph.showGraphLocally()

def demoCSVExporting():
    """
    for testing only, used to test the graph export function 
    """
    graph = GameGraph()
    graph.createErdosRenyiGraph(20)
    graph.showGraphLocally()
    graph.exportGraphAsCSV("C:\\Users\\LJ\\Desktop\\output.csv")