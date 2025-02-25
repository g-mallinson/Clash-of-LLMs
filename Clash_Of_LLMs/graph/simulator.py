import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx as nx
from pyvis.network import Network
import numpy as np
import random


import requests

from Clash_Of_LLMs.graph.message import Message

# Debugging and Animation Settings (for developers)
debugging = True
save_animation = True


class Simulator:
    """
    Class for simulating the spread of information in a network. The
    network is represented as a graph, with nodes representing
    individuals and edges representing connections between them. The
    simulation is based on the Independent Cascade (IC) model.

    Attributes
    ----------
    num_nodes : int, optional
        Number of nodes in the graph. The default is 50.
    network_type : str, optional
        Network topology. The default is "erdos_renyi".
    edge_probability : float, optional
        Probability of edge creation. The default is 0.01.
    source_activation_rate : float, optional
        Percentage of population initially receiving the message. The
        default is 0.1.
    base_influence_prob : float, optional
        Base probability of influence in the IC model. The default is
        0.1.
    backlash_threshold : float, optional
        Potency threshold for backlash to occur. The default is 0.8.
    backlash_factor : float, optional
        Factor for reduction of susceptibility during backlash. The
        default is 0.2.
    num_turns : int, optional
        Number of turns to simulate. The default is 10.
    steps_per_turn : int, optional
        Duration of message propogation between each team's turns
        (steps). The default is 2.
    autoplay_delay : float, optional
        Delay between steps in autoplay mode (seconds). The default is
        1.0.
    random_seed : int, optional
        Random seed for reproducibility. The default is 42.
    current_message : Message object
        The current message being propogated.
    use_random_start_alignments : bool, optional
        Whether to use randomised alignments when starting. The default
        is False.

    Methods
    -------
    create_network()
        Create a network with specified topology and parameters.
    initialize_node_attributes()
        initialize the nodes with random susceptibility and current
        alignment.
    create_messages(team)
        Create a list of messages for a given team.
    run_simulation()
        Run the simulation for the desired number of steps.
    introduce_message(team)
        Propogate messages for a given team.
    run_simulation()
        Run the simulation for the desired number of steps.
    activate_source_nodes(team, message)
        Activate initial nodes for a given team with the message.
    spread_message(active_nodes, message)
        Spread the message to neighboring nodes through the network.
    update_stats()
        Update the metrics for the simulation.
    visualise_network(turn)
        Visualise the network at a given turn.
    """

    def __init__(
        self,
        num_nodes=50,
        network_type="watts_strogatz",
        edge_probability=0.05,
        random_seed=42,
        use_random_start_alignments=False,
        source_activation_rate=0.1,
        base_influence_prob=0.5,
        backlash_threshold=0.8,
        backlash_factor=0.2,
        num_turns=40,
        steps_per_turn=2,
        autoplay=True,
        autoplay_delay=1.0,
        animate=True
    ):
        """
        Initialize the simulator with parameters.
        """
        # SIMULATION CONFIGURATION
        # Network parameters
        self.num_nodes = num_nodes
        self.network_type = network_type
        self.edge_probability = edge_probability
        self.random_seed = random_seed
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)
        self.use_random_start_alignments = use_random_start_alignments
        # Simulation parameters
        self.source_activation_rate = source_activation_rate
        self.base_influence_prob = base_influence_prob
        self.backlash_threshold = backlash_threshold
        self.backlash_factor = backlash_factor
        self.blue_energy = 70
        # Game parameters
        self.num_turns = num_turns
        self.steps_per_turn = steps_per_turn
        # Playback parameters
        self.autoplay = autoplay
        self.autoplay_delay = autoplay_delay
        # Debugging and Animation
        self.animate = animate

        # INITIALIZE DYNAMIC ATTRIBUTES
        # Simulation state
        self.current_team = "Red"  # Red team starts first
        self.current_step = 0
        self.turns_completed = 0
        self.simulation_running = False
        self.active_messages = []
        self.current_message = None
        self.history = [{"Red": 0, "Blue": 0, "Neutral": self.num_nodes}]
        self.frames = []  # Store graph data frame at each step
        
        
        self.G = self.create_network()
        self.initialize_node_attributes()
        
        # INITIALIZE CURRENT MESSAGES
        self.current_messages = {"Red": None, "Blue": None}


    def set_message(self, team, message):
        """
        Set the message for a given team.

        Parameters
        ----------
        team : str
            The team to set the message for ('Red' or 'Blue').
        message : Message object
            The message to set.
        """
        
        if team.capitalize() not in ["Red", "Blue"]:
            raise ValueError("Invalid team. Must be 'Red' or 'Blue'.")
        team = team.capitalize()
        self.current_team = team
        message.team = team
        potency_str = message.content.split("Potency =")[-1].strip().rstrip(".")
        message.content = f"{team} message, {message.content}"
        message.potency = float(potency_str) if potency_str else 0.0
        message.active_nodes = set()
        message.steps_remaining = self.steps_per_turn
        self.current_message = message
        self.current_messages[team] = message
        
        return message


    def introduce_message(self, team="Red"):
        """
        Introduces message to the network for a given team.

        Parameters
        ----------
        team : str
            The team to propogate messages for ('Red' or 'Blue')
            (default='Red').
        """
        print(f"{team.upper()} Team's Turn") if debugging else None
        message = self.current_messages[team]
        self.current_message = message
        print(f"\n### SELECTED MESSAGE: \n{message}") if debugging else None

        # Activate source nodes and initialize message attributes
        source_nodes = self.activate_source_nodes(team, message)
        message.active_nodes = set(source_nodes)
        message.steps_remaining = self.steps_per_turn
        self.active_messages.append(message)
            

    def create_network(self):
        """
        Create a network with specified topology and parameters.
        return: networkx graph
        """
        if self.network_type == "erdos_renyi":
            G = nx.erdos_renyi_graph(
                self.num_nodes, self.edge_probability, seed=self.random_seed
            )
        elif self.network_type == "barabasi_albert":
            G = nx.barabasi_albert_graph(self.num_nodes, 2, seed=self.random_seed)
        elif self.network_type == "watts_strogatz":
            G = nx.watts_strogatz_graph(
                self.num_nodes, 4, 0.1, seed=self.random_seed
            )
        return G

    def create_network_custom(
        self, 
        network_type="watts_strogatz",
        uncertainty=0.5, 
        n=50, 
        er_probability=0.05,
        ba_connections=2,
        ws_neighbours=4,
        ws_rewire_probability=0.1
    ):
        """
        Create a network with specified topology and parameters.

        Parameters
        ----------
        network_type : str
            Network topology.
        uncertainty : float
            Initial uncertainty of nodes.
        n : int
            Number of nodes in the graph.
        er_probability : float
            Probability of erdos renyi graph edge creation.
        ba_connections : int
            Number of barabasi albert initial node connections in the graph.
        ws_neighbours : int
            Number of watts strogatz graph neigbour edges in the graph.
        ws_rewire_probability : float
            Probability of watts strogatz graph edge rewiring.
        """
        # print("network_type:", network_type,
        #      "uncertainty", uncertainty,
        #      "n", n,
        #      "er_probability", er_probability,
        #      "ba_connections", ba_connections,
        #      "ws_neighbours", ws_neighbours,
        #      "ws_rewire_probability", ws_rewire_probability)
        
        if network_type == "erdos_renyi":
            G = nx.erdos_renyi_graph(n, er_probability, seed=self.random_seed)
        elif network_type == "barabasi_albert":
            G = nx.barabasi_albert_graph(n, ba_connections, seed=self.random_seed)
        elif network_type == "watts_strogatz":
            G = nx.watts_strogatz_graph(n, ws_neighbours, ws_rewire_probability, seed=self.random_seed)
        else:
            G = nx.erdos_renyi_graph(n, er_probability, seed=self.random_seed)

        self.G = G
        self.num_nodes = n
        self.edge_probability = er_probability if er_probability is not None else 0.05
        self.network_type = network_type

        # Reinitalize node attributes with new uncertainty
        self.uncertainty = uncertainty
        self.initialize_node_attributes(uncertainty=self.uncertainty)

        k_value = 3 / np.sqrt(self.num_nodes)
        self.pos = nx.spring_layout(
            self.G, k=0.1, iterations=1000, seed=self.random_seed
        )
        return G

    def initialize_node_attributes(self, uncertainty=2.0):
        """
        initialize the nodes with random susceptibility and current
        alignment.
        """
        for node in self.G.nodes:
            self.G.nodes[node]["susceptibility"] = np.random.uniform(0.0, 1.0)
            self.G.nodes[node]["alienated"] = False
            if self.use_random_start_alignments:
                self.G.nodes[node]["alignment"] = np.random.choice(["Red", "Blue"])
                self.G.nodes[node]["uncertainty"] = np.random.uniform(
                    -(uncertainty), uncertainty
                )
            else:
                self.G.nodes[node]["alignment"] = "Neutral"
                self.G.nodes[node]["uncertainty"] = uncertainty

            # ? Do I need to initialize an 'activated' attribute here?
        
        
    def activate_source_nodes(self, team, message):
        """
        Activate initial nodes for a given team with the message.

        Parameters
        ----------
        team : str
            The team to activate source nodes for ('Red' or 'Blue')             # ? Should each team only have one source node?
                                                                                # ? and should it be the same node each time, or perhaps one chosen according to some criteria?
            (default='Red').
        message : Message object
            The message to activate nodes with.

        Returns
        -------
        source_nodes : list
            List of nodes that are activated.
        """
        # Determine number of initial nodes to activate
        num_initial = int(self.source_activation_rate * self.num_nodes)

        # Select nodes to activate
        source_nodes = random.sample(list(self.G.nodes), num_initial)

        # Activate nodes
        for node in source_nodes:
            # ? Is an 'activated' attribute necessary?
            self.G.nodes[node]["alignment"] = team
        print(f"Source nodes activated: {len(source_nodes)}") if debugging else None

        return source_nodes


    def message_influence(self, node, message):
        U = self.G.nodes[node]["uncertainty"]
        Q = message.potency
        A = self.G.nodes[node]["alignment"]
        T = message.team
        # print(f"NODE {node} BEFORE message_influence A: {A} U: {U} T: {T} Q: {Q} Alienated?: {self.G.nodes[node]['alienated']}")
        if A != message.team:
            if message.team == "Red":
                alienation_threshold = (
                    -1
                )  # Q = 0.1 can only alienate U = -1.0; Q = 1 can alienate U < -1.0
                if U * Q * 10 <= alienation_threshold:
                    self.G.nodes[node]["alienated"] = True
            elif A == "Neutral":
                self.G.nodes[node]["uncertainty"] = 0.5
                self.G.nodes[node]["alignment"] = message.team
            elif U >= 0:
                if Q >= 0.5:
                    self.G.nodes[node]["alignment"] = self.switch(node)
                    self.G.nodes[node]["uncertainty"] = (
                        9 - Q * 10 - (U * 2)
                    ) / 10  # -0.3 < U < 0.4 range for nodes
                else:
                    if (U + Q) > 1.0:
                        self.G.nodes[node]["alignment"] = self.switch(node)
                        self.G.nodes[node]["uncertainty"] = 2.0 - (
                            U + Q
                        )  # 0.5 < U < 1.0 range for nodes
            elif -0.5 < U:
                self.G.nodes[node]["uncertainty"] += (
                    Q / 2
                )  # -0.5 < U < 0.5 range for nodes
            else:
                # nodes closer to U = -1.0 will resist potent messages more
                self.G.nodes[node]["uncertainty"] += (10 * Q) / (
                    100 * -(U)
                )  # -1.0 < U < -0.3 range for nodes
        else:
            if U >= 0:
                if Q >= 0.5:
                    self.G.nodes[node]["uncertainty"] = (
                        5 - (Q * 10) + (U * 5)
                    ) / 10  # -0.5 < U < 0.5 range for nodes
                else:
                    self.G.nodes[node]["uncertainty"] = U - (
                        2 * Q / 5
                    )  # -0.2 < U < 0.8 range for nodes
            elif -0.5 < U:
                self.G.nodes[node]["uncertainty"] = U - (
                    Q / 3
                )  # -0.8 < U < -0.5 range for nodes
            else:
                # nodes closer to U = -1.0 will be harder to make them more certain than they already are.
                self.G.nodes[node]["uncertainty"] = U - max(
                    (10 * Q) / (30 * (-U)) - 0.34, 0
                )  # -1.0 < U < -0.5 range for nodes
        # print(f"NODE {node} AFTER message_influence A: {self.G.nodes[node]['alignment']} U: {self.G.nodes[node]['uncertainty']} Alienated?: {self.G.nodes[node]['alienated']} ")

    def switch(self, node):
        if self.G.nodes[node]["alignment"] == "Blue":
            return "Red"
        return "Blue"
    

    def green_influence(self):
        for node in self.G.nodes:
            for neighbor in self.G.neighbors(node):
                if (
                    self.G.nodes[node]["uncertainty"]
                    < self.G.nodes[neighbor]["uncertainty"]
                ):
                    self.influence(node, neighbor)
                    

    def influence(self, sup_node, inf_node):
        A1 = self.G.nodes[sup_node]["alignment"]
        U1 = self.G.nodes[sup_node]["uncertainty"]
        A2 = self.G.nodes[inf_node]["alignment"]
        U2 = self.G.nodes[inf_node]["uncertainty"]
        c = 1000
        # print(f"BEFORE: NODE {sup_node} A = {A1} U = {U1} influences NODE {inf_node} A = {A2} U = {U2}")
        if A1 == A2:
            if U2 >= 0:
                if U1 >= 0:
                    self.G.nodes[inf_node]["uncertainty"] = U2 - (U2 - U1) / (
                        c / 5
                    )  # Change of unceratinty is 20% of the difference in uncertainty
                elif U1 > -0.5:
                    self.G.nodes[inf_node]["uncertainty"] = U2 - (U2 - U1) / (
                        c / 4
                    )  # Change of unceratinty is 25% of the difference in uncertainty
                else:
                    self.G.nodes[inf_node]["uncertainty"] = U2 - (U2 - U1) / (
                        c / 3
                    )  # Change of unceratinty is 33.33% of the difference in uncertainty
            elif U2 > -0.5:
                if U1 > -0.5:
                    self.G.nodes[inf_node]["uncertainty"] = U2 - (U2 - U1) / (
                        c / 10
                    )  # Change of unceratinty is 10% of the difference in uncertainty
                else:
                    self.G.nodes[inf_node]["uncertainty"] = U2 - (U2 - U1) / (
                        c / 5
                    )  # Change of unceratinty is 20% of the difference in uncertainty
            else:
                self.G.nodes[inf_node]["uncertainty"] = U2 - (U2 - U1) / (
                    c / 10
                )  # Change of unceratinty is 10% of the difference in uncertainty
        elif A2 == "Neutral":
            self.G.nodes[inf_node]["uncertainty"] = 0.5
            self.G.nodes[inf_node]["alignment"] = A1
        else:
            if U2 >= 0:
                if U1 >= 0:
                    if U2 + (U2 - U1) / (c / 5) > 1:
                        self.G.nodes[inf_node]["alignment"] = self.switch(inf_node)
                        self.G.nodes[inf_node]["uncertainty"] = 2 - (
                            U2 + (U2 - U1) / (c / 5)
                        )
                    else:
                        self.G.nodes[inf_node]["uncertainty"] = U2 + (U2 - U1) / (
                            c / 5
                        )  # Change of unceratinty is 20% of the difference in uncertainty
                elif U1 > -0.5:
                    if U2 + (U2 - U1) / (c / 4) > 1:
                        self.G.nodes[inf_node]["alignment"] = self.switch(inf_node)
                        self.G.nodes[inf_node]["uncertainty"] = 2 - (
                            U2 + (U2 - U1) / (c / 4)
                        )
                    else:
                        self.G.nodes[inf_node]["uncertainty"] = U2 + (U2 - U1) / (
                            c / 4
                        )  # Change of unceratinty is 25% of the difference in uncertainty
                else:
                    if U2 + (U2 - U1) / (c / 3) > 1:
                        self.G.nodes[inf_node]["alignment"] = self.switch(inf_node)
                        self.G.nodes[inf_node]["uncertainty"] = 2 - (
                            U2 + (U2 - U1) / (c / 3)
                        )
                    else:
                        self.G.nodes[inf_node]["uncertainty"] = U2 + (U2 - U1) / (
                            c / 3
                        )  # Change of unceratinty is 33.33% of the difference in uncertainty
            elif U2 > -0.5:
                if U1 > -0.5:
                    self.G.nodes[inf_node]["uncertainty"] = U2 + (U2 - U1) / (
                        c / 10
                    )  # Change of unceratinty is 10% of the difference in uncertainty
                else:
                    self.G.nodes[inf_node]["uncertainty"] = U2 + (U2 - U1) / (
                        c / 5
                    )  # Change of unceratinty is 20% of the difference in uncertainty
            else:
                self.G.nodes[inf_node]["uncertainty"] = U2 + (U2 - U1) / (
                    c / 10
                )  # Change of unceratinty is 10% of the difference in uncertainty
        # print(f"AFTER: NODE {sup_node} A = {A1} U = {U1} influences NODE {inf_node} A = {A2} U = {U2}")

    def energy_lost(self, potency):
        return (10*potency/3)**2.1


    def spread_active_messages(self):
        """
        Spread the active messages to neighboring nodes through the
        network. If a node is influenced, it adopts the alignment of the
        message, and becomes active for the next turn.
        """
        new_active_messages = []
        for active_message in self.active_messages:
            if active_message.steps_remaining > 0:
                content = active_message.content
                team = active_message.team
                current_active_nodes = active_message.active_nodes
                (
                    print(
                        f"\nACTIVE MESSAGE: {content} \nTEAM: {team} \nACTIVE NODES: {current_active_nodes} \nSTEPS REMAINING: {active_message.steps_remaining}\n"
                    )
                    if debugging
                    else None
                )

                new_active_nodes = set()

                for current_node in current_active_nodes:
                    for neighbor in self.G.neighbors(current_node):
                        if (
                            self.G.nodes[neighbor]["alienated"] == True
                            and team == "Red"
                        ):
                            continue
                        if (
                            neighbor in current_active_nodes
                            or neighbor in new_active_nodes
                        ):
                            continue

                        susceptibility = self.G.nodes[neighbor]["susceptibility"]
                        influence_probability = (
                            self.base_influence_prob
                            * active_message.potency
                            * susceptibility
                        )

                        if self.G.nodes[neighbor]["alignment"] != team:
                            influence_probability *= 0.8  # Reduce influence probability for nodes with opposite alignment

                        if random.random() < influence_probability:
                            old = self.G.nodes[neighbor]["alignment"]
                            self.message_influence(neighbor, active_message)
                            """ message_influence handles whether a
                            green agent swaps alignments given exposure
                            to the message """
                            # self.G.nodes[neighbor]['alignment'] = team
                            new_active_nodes.add(neighbor)
                            if self.G.nodes[neighbor]["alignment"] != old:
                                (
                                    print(
                                        f"Node {neighbor} influenced by node {current_node}, and changes to {self.G.nodes[neighbor]['alignment']} alignment from {old}."
                                    )
                                    if debugging
                                    else None
                                )

                self.green_influence()
                # Update active nodes for the message
                active_message.active_nodes = new_active_nodes
                active_message.steps_remaining -= 1
                new_active_messages.append(active_message)
                (
                    print(
                        f"### UPDATING ACTIVE NODES FOR MESSAGE \nNEW ACTIVE NODES: {new_active_nodes}\n"
                    )
                    if debugging
                    else None
                )
        # Update active messages
        self.active_messages = new_active_messages


    def initialize_simulation(self):
        """
        Reset simulation to initial state for a new run. Creates the
        network and prepares test messages for both teams.
        """
        # RESET SIMULATION STATE
        self.current_team = "Red"  # Red team starts first
        self.current_step = 0
        self.turns_completed = 0
        self.simulation_running = True
        self.active_messages = []
        self.history = [{"Red": 0, "Blue": 0, "Neutral": self.num_nodes}]

        # RECREATE NETWORK AND REINITIALIZE NODES
        self.G = self.create_network()
        self.initialize_node_attributes()

        self.current_messages = {"Red": None, "Blue": None}

        # REINITIALIZE METRICS
        self.initialize_metrics()

        print("### SIMULATION INITIALIZED\n.\n.\n.")
        

    def step_simulation(self):
        """
        Perform a single step of the simulation,
        """
        print("\n### SIMULATION STEP ###") if debugging else None
        self.num_steps = self.num_turns * self.steps_per_turn
        if self.current_step >= self.num_steps:
            self.simulation_running = False
            return {"status": "finished"}

        if self.turns_completed < self.num_turns:
            if self.current_step % self.steps_per_turn == 0:
                # Start a new turn
                print(f"\n--- {self.current_team} Team's Turn ---")
                self.introduce_message(team=self.current_team)
                for _ in range(self.steps_per_turn):
                    print(f"\nStep {self.current_step + 1}") if debugging else None
                    self.spread_active_messages()
                    self.update_stats()
                    self.get_frame_data(self.current_step + 1)
                    self.current_step += 1

                # Switch teams
                if self.current_team == "Red":
                    self.current_team = "Blue"
                else:
                    self.current_team = "Red"

                self.turns_completed += 1

                graph_data = self.get_graph_data()
                return {
                    "status": "running",
                    "data": graph_data,
                    "current_step": self.current_step,
                }
                
    def restart_simulation(self):
        """
        Restart the simulation with the current graph.
        """
        # RESET SIMULATION STATE
        self.current_team = "Red"  # Red team starts first
        self.current_step = 0
        self.turns_completed = 0
        self.simulation_running = True
        self.active_messages = []
        self.history = [{"Red": 0, "Blue": 0, "Neutral": self.num_nodes}]
        
        self.initialize_node_attributes()
        self.current_messages = {"Red": None, "Blue": None}
        self.initialize_metrics()

        print("### SIMULATION RESTARTED\n.\n.\n.")
    
        return {"graph": self.get_graph_data(), "stats": self.get_stats(), "status": "started"}


    def initialize_metrics(self):
        """
        Initialize the metrics for the simulation.
        """
        self.metrics = {
            "Red": {"believers_gained": 0, "believers_lost": 0},
            "Blue": {"believers_gained": 0, "believers_lost": 0},
        }
        self.history = [{"Red": 0, "Blue": 0, "Neutral": self.num_nodes}]
        self.frames = []  # Store graph data frame at each step


    def get_graph_data(self):
        """
        Serialize the graph data for the current state of the simulation
        to a JSON-serializable format. This data will be used to update
        the visualisation of the network on the client side.

        Returns
        -------
        dict
            Dictionary containing the graph data.
        """
        nodes = [
            {
                "id": node,
                "alignment": self.G.nodes[node]["alignment"],
                "susceptibility": self.G.nodes[node]["susceptibility"],
                "uncertainty": self.G.nodes[node]["uncertainty"],
                "alienated": self.G.nodes[node]["alienated"],
            }
            for node in self.G.nodes
        ]
        edges = [{"from": source, "to": target} for source, target in self.G.edges]
        return {"nodes": nodes, "edges": edges}


    def update_stats(self):
        """
        Update the metrics for the simulation, recording the number of believers
        gained and lost for each team. Prints the metrics to the console.
        """
        red_believers = sum(
            [1 for node in self.G.nodes if self.G.nodes[node]["alignment"] == "Red"]
        )
        blue_believers = sum(
            [1 for node in self.G.nodes if self.G.nodes[node]["alignment"] == "Blue"]
        )
        alienated = sum(
            [1 for node in self.G.nodes if self.G.nodes[node]["alienated"] == True]
        )
        neutral = self.num_nodes - red_believers - blue_believers

        last_entry = self.history[-1]
        change_red = red_believers - last_entry["Red"] if len(self.history) > 1 else 0
        change_blue = (
            blue_believers - last_entry["Blue"] if len(self.history) > 1 else 0
        )

        self.history.append(
            {"Red": red_believers, "Blue": blue_believers, "Neutral": neutral}
        )

        # print(f"\n# DEBUGGING Metrics History: {self.history}") if debugging else None
        (
            print(
                f"\nRED BELIEVERS: {red_believers} (CHANGE: {change_red}) \nBLUE BELIEVERS: {blue_believers} (CHANGE: {change_blue}) \nNEUTRAL: {neutral}, ALIENATED: {alienated}"
            )
            if debugging
            else None
        )

    def get_stats(self):
        """
        Get the current live stats for the simulation as dictionary.

        Returns
        -------
        dict
            Dictionary containing the current stats.
        """
        red_believers = sum(
            1 for node in self.G.nodes if self.G.nodes[node]["alignment"] == "Red"
        )
        blue_believers = sum(
            1 for node in self.G.nodes if self.G.nodes[node]["alignment"] == "Blue"
        )
        neutral = self.num_nodes - red_believers - blue_believers
        alienated = sum(
            [1 for node in self.G.nodes if self.G.nodes[node]["alienated"] == True]
        )

        red_percentage = (
            red_believers / self.num_nodes * 100 if self.num_nodes > 0 else 0
        )
        blue_percentage = (
            blue_believers / self.num_nodes * 100 if self.num_nodes > 0 else 0
        )
        neutral_percentage = neutral / self.num_nodes * 100 if self.num_nodes > 0 else 0
        alienated_percentage = alienated/self.num_nodes * 100 if self.num_nodes > 0 else 0

        if self.current_message:
            curr_message = self.current_message
            curr_content = curr_message.content
            curr_potency = curr_message.potency
            curr_team = curr_message.team
        else:
            curr_message = None
            curr_content = None
            curr_potency = None
            curr_team = None
        if curr_team == "Blue":
            self.blue_energy -= self.energy_lost(curr_potency)
        stats = {
            "CurrentTeam": curr_team,
            "CurrentMessageContent": curr_content,
            "CurrentPotency": curr_potency,
            "Red": red_believers,
            "RedPercentage": red_percentage,
            "Blue": blue_believers,
            "BluePercentage": blue_percentage,
            "Neutral": neutral,
            "NeutralPercentage": neutral_percentage,
            "Alienated": alienated,
            "AlienatedPercentage": alienated_percentage,
            "BlueEnergy": self.blue_energy
        }

        return stats

    def plot_stats(self):
        """
        Plot the metrics of the simulation. (Believers over time)
        """
        steps = range(1, self.num_turns + 1)
        self.history.pop(0)  # Remove initial entry for plotting
        red_believers = [
            entry["Red"] for entry in self.history
        ]  # ? Maybe use a traditional for loop instead of list comprehension for clarity
        blue_believers = [entry["Blue"] for entry in self.history]
        neutral = [entry["Neutral"] for entry in self.history]

        plt.figure(figsize=(15, 9))
        plt.plot(steps, red_believers, label="Red Believers", color="red")
        plt.plot(steps, blue_believers, label="Blue Believers", color="blue")
        plt.plot(steps, neutral, label="Neutral", color="grey")
        plt.xlabel("Step")
        plt.ylabel("Number of Believers")
        plt.title("Believers Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()


    def get_frame_data(self, turn):
        """
        Collect data for visualisation on website UI, and for animation frames
        for testing. Append the data to the frames list.

        Parameters
        ----------
        turn : int
            The turn number.

        Returns
        -------
        frame : dict
            Dictionary containing data for the current turn.
        """
        color_map = {"Red": "red", "Blue": "blue", "Neutral": "grey"}
        node_colors = [
            color_map[self.G.nodes[node]["alignment"]] for node in self.G.nodes
        ]
        frame = {"turn": turn, "node_colors": node_colors}
        self.frames.append(frame)

        return frame

    def animate_frames(self):
        """
        Animate the frames of the simulation.
        """
        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_title("Information Diffusion Simulation")
        ax.axis("off")

        # Keep the positions consistent
        pos = self.pos

        def update(frame_data):
            ax.clear()
            ax.set_title(
                f"Turn {frame_data['turn']//self.steps_per_turn}\nStep {frame_data['turn']}"
            )
            nx.draw(
                self.G, pos=self.pos, node_color=frame_data["node_colors"], node_size=40
            )
            return ax

        anim = FuncAnimation(
            fig,
            update,
            frames=self.frames,
            interval=1000 * self.autoplay_delay,
            repeat=True,
        )
        anim.save("diffusion_animation.gif") if save_animation else None
        plt.show()