import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx as nx
import numpy as np
import random
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
    initial_activation_probability : float, optional
        Percentage of population initially receiving the message. The
        default is 0.1.
    base_influence_probability : float, optional
        Base probability of influence in the IC model. The default is
        0.1.
    backlash_threshold : float, optional
        Potency threshold for backlash to occur. The default is 0.8.
    backlash_factor : float, optional
        Factor for reduction of susceptibility during backlash. The
        default is 0.2.
    num_turns : int, optional
        Number of turns to simulate. The default is 10.
    message_propogation_duration : int, optional
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
    initialise_nodes()
        Initialise the nodes with random susceptibility and current
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
    update_metrics()
        Update the metrics for the simulation.
    visualise_network(turn)
        Visualise the network at a given turn.
        
               
    """    
    def __init__(
        self,
        num_nodes=50,  
        network_type="erdos_renyi",    
        edge_probability=0.05,     
        initial_activation_probability=0.01,
        base_influence_probability=0.2,
        backlash_threshold=0.8,
        backlash_factor=0.2,
        num_turns=10,
        message_propogation_duration=2,
        autoplay=True,
        autoplay_delay=1.0,
        random_seed=42,
        use_random_start_alignments=True,
        animate = True
    ):
        """
        Initialize the simulator with parameters.
        """
        self.num_nodes = num_nodes
        self.network_type = network_type
        self.edge_probability = edge_probability
        self.initial_activation_probability = initial_activation_probability
        self.base_influence_probability = base_influence_probability
        self.backlash_threshold = backlash_threshold
        self.backlash_factor = backlash_factor
        self.num_turns = num_turns
        self.message_propogation_duration = message_propogation_duration
        self.autoplay = autoplay
        self.autoplay_delay = autoplay_delay
        self.random_seed = random_seed
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)
        self.use_random_start_alignments = use_random_start_alignments
        self.animate = animate
    
        self.G = self.create_network()
        
        # Increase k value for larger networks
        k_value = 3/np.sqrt(self.num_nodes) 
        
        # Set fixed node positions for visualisation
        self.pos = nx.spring_layout(self.G,
                                    k=k_value,
                                    iterations=1000, 
                                    seed=self.random_seed)
        
        self.initialise_nodes()
        
        # Message pool for each team
        self.red_messages = self.create_messages(team='Red')
        self.blue_messages = self.create_messages(team='Blue')
        
        self.active_messages = [] # Messages actively being propogated
        
        # Initialise metrics
        self.metrics = {
            'Red': {'believers_gained': 0, 'believers_lost': 0},
            'Blue': {'believers_gained': 0, 'believers_lost': 0}
        }
        # History of metrics for plotting
        self.history = [{'Red': 0, 'Blue': 0, 'Neutral': num_nodes}]  # Initial history entry
        # Graph data frames at each turn
        self.frames = []
    
    def to_html():
        '''
        Converts the nx graph to a pyvis network and then renders it to html
        '''
        # TODO
        pass

    def recieve_message(potency, team):
        '''
        Receives a message of a certain potency from a team "RED" or "BLUE"
        '''
        # TODO
        pass

    def create_network(self):
        """
        Create a network with specified topology and parameters.
        """
        if self.network_type == "erdos_renyi":
            G = nx.erdos_renyi_graph(self.num_nodes, self.edge_probability, 
                                                        seed=self.random_seed)
        else:
            # TODO: Implement other network types here
            # ! For now, default to Erdos-Renyi (placeholder)
            # ...
            G = nx.erdos_renyi_graph(self.num_nodes, self.edge_probability, 
                                                        seed=self.random_seed)
        return G
    
    
    def initialise_nodes(self):
        """
        Initialise the nodes with random susceptibility and current
        alignment.
        """
        for node in self.G.nodes:
            self.G.nodes[node]['susceptibility'] = np.random.uniform(0.0, 1.0)
            self.G.nodes[node]['alienated'] = False
            if self.use_random_start_alignments:
                self.G.nodes[node]['alignment'] = np.random.choice(['Red', 'Blue'])
                self.G.nodes[node]['uncertainty'] = np.random.uniform(-1.0, 1.0)
            else:
                self.G.nodes[node]['alignment'] = 'Neutral'
                self.G.nodes[node]['uncertainty'] = 2.0
            
            # ? Do I need to initialise an 'activated' attribute here?
            
    
    def create_messages(self, team='Red'):
        """
        Create a list of messages for a given team. Each message has a
        random potency according to a uniform distribution. The content
        of the message is a placeholder string with the team name and
        potency.
        
        Parameters
        ----------
        team : str
            The team to create messages for ('Red' or 'Blue')
            (default='Red').
        """
        messages = []
        for i in range(self.num_turns // self.message_propogation_duration):
            potency = random.uniform(0.2, 1.0)
            message = Message(team=team, 
                              potency=potency, 
                              content=f"{team} message {i}, potency = {potency:.2f}", 
                              active_nodes=set(), 
                              steps_remaining=self.message_propogation_duration)
            messages.append(message)
            
        return messages
        
        
    def run_simulation(self):
        """
        Run the simulation for the desired number of steps. Alternate
        between Red and Blue team turns. Visualise the network and
        update metrics for plotting at each step.
        """
        total_turns = self.num_turns
        turn = 1
        step = 1
        current_team = 'Red' # Red team starts first # ? maybe add option to choose later
        
        while turn <= total_turns:
            print(f"\n--- {current_team} Team's Turn ---") if debugging else None
            # Send message as current team
            self.introduce_message(team=current_team)
            # Propogate message for `message_propogation_duration` steps
            for _ in range(self.message_propogation_duration):
                if turn > total_turns:
                    break
                print(f"\nStep {turn}") if debugging else None
                # Spread the active messages
                self.spread_active_messages()
                # Collect metrics and visualise network
                self.update_metrics()
                self.visualise_network(turn) if not self.autoplay else None
                # Collect data for animation frames
                self.collect_frame_data(turn)
                step += 1
            # Switch teams
            current_team = 'Blue' if current_team == 'Red' else 'Red'
            turn += 1
            
    def introduce_message(self, team='Red'):
        """
        Introduces message to the network for a given team.
        
        Parameters
        ----------
        team : str
            The team to propogate messages for ('Red' or 'Blue')
            (default='Red').
        """
        print("### SELECTING MESSAGE") if debugging else None
        print(f"{team.upper()} Team's Turn") if debugging else None
        
        # Select a message from respective team's message pool
        if team == 'Red':
            if not self.red_messages:
                print("\n\nERROR: Predefined messages exhausted (team: RED)")           
            message = random.choice(self.red_messages)
            self.red_messages.remove(message)
        else:
            if not self.blue_messages:
                print("\n\nERROR: Predefined messages exhausted (team: BLUE)")                
            message = random.choice(self.blue_messages)
            self.blue_messages.remove(message)
         
        # Set the current message to the selected message   
        self.current_message = message
        print(f"\n### SELECTED MESSAGE: \n{message.content}") if debugging else None
    
        # Activate source nodes and initialise message attributes
        source_nodes = self.activate_source_nodes(team, message)
        message.active_nodes = set(source_nodes)
        message.steps_remaining = self.message_propogation_duration
          
        # Add to active messages
        self.active_messages.append(message)
        
        
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
        num_initial = int(self.initial_activation_probability * self.num_nodes)
        
        # Select nodes to activate
        source_nodes = random.sample(list(self.G.nodes), num_initial)
        
        # Activate nodes
        for node in source_nodes:
            # ? Is an 'activated' attribute necessary? 
            self.G.nodes[node]['alignment'] = team
        print(f"Source nodes activated: {len(source_nodes)}") if debugging else None
        
        return source_nodes
    
                
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
                print(f"\nACTIVE MESSAGE: {content} \nTEAM: {team} \nACTIVE NODES: {current_active_nodes} \nSTEPS REMAINING: {active_message.steps_remaining}\n") if debugging else None   

                new_active_nodes = set()

                for current_node in current_active_nodes:
                    for neighbor in self.G.neighbors(current_node):
                        if (self.G.nodes[neighbor]['alienated'] == True 
                            and team == 'Red'):
                            continue
                        if (neighbor in current_active_nodes 
                            or neighbor in new_active_nodes):
                            continue

                        susceptibility = self.G.nodes[neighbor]['susceptibility']
                        influence_probability = (self.base_influence_probability
                                                 * active_message.potency 
                                                 * susceptibility)
                        
                        if self.G.nodes[neighbor]['alignment'] != team:
                            influence_probability *= 0.8 # Reduce influence probability for nodes with opposite alignment  
                            
                        if random.random() < influence_probability:
                            old = self.G.nodes[neighbor]['alignment']
                            self.message_influence(neighbor, active_message)
                            ''' message_influence handles whether a
                            green agent swaps alignments given exposure
                            to the message '''
                            #self.G.nodes[neighbor]['alignment'] = team 
                            new_active_nodes.add(neighbor)
                            if(self.G.nodes[neighbor]['alignment'] != old):
                                print(f"Node {neighbor} influenced by node {current_node}, and changes to {self.G.nodes[neighbor]['alignment']} alignment from {old}.") if debugging else None

                self.green_influence()
                # Update active nodes for the message   
                active_message.active_nodes = new_active_nodes
                active_message.steps_remaining -= 1
                new_active_messages.append(active_message)
                print(f"### UPDATING ACTIVE NODES FOR MESSAGE \nNEW ACTIVE NODES: {new_active_nodes}\n") if debugging else None
        # Update active messages
        self.active_messages = new_active_messages
        

    def message_influence(self, node, message):
        U = self.G.nodes[node]['uncertainty']
        Q = message.potency
        A = self.G.nodes[node]['alignment']
        T = message.team
        #print(f"NODE {node} BEFORE message_influence A: {A} U: {U} T: {T} Q: {Q} Alienated?: {self.G.nodes[node]['alienated']}")
        if A != message.team:
            if A == 'Neutral':
                self.G.nodes[node]['uncertainty'] = 0.5
                self.G.nodes[node]['alignment'] = message.team
            elif(U >= 0 ):
                if(Q >= 0.5):
                    self.G.nodes[node]['alignment'] = self.switch(node)
                    self.G.nodes[node]['uncertainty'] = (9 - Q*10 - (U * 2)) / 10    # -0.3 < U < 0.4 range for nodes 
                else:
                    if( (U + Q) > 1.0):
                        self.G.nodes[node]['alignment'] = self.switch(node)
                        self.G.nodes[node]['uncertainty'] = 2.0 - (U + Q)  # 0.5 < U < 1.0 range for nodes
            elif (-0.5 < U):
                self.G.nodes[node]['uncertainty'] += Q/2        # -0.5 < U < 0.5 range for nodes
            else:
                if (message.team == 'Red'):
                    alienation_threshold = -8    # 0.8 < Q < 1 have the power to alienate nodes. Q = 0.8 can only alienate U = -1.0; Q = 1 can alienate U < -8.0
                    if (U*Q*10 <= alienation_threshold):
                        self.G.nodes[node]['alienated'] = True
                    else:
                        # nodes closer to U = -1.0 will resist potent messages more
                        self.G.nodes[node]['uncertainty'] += (10*Q)/(100 * -(U))  # -1.0 < U < -0.3 range for nodes
                else:
                    # nodes closer to U = -1.0 will resist potent messages more
                    self.G.nodes[node]['uncertainty'] += (10*Q)/(100 * -(U))  # -1.0 < U < -0.3 range for nodes
        else:
            if(U >= 0 ):
                if(Q >= 0.5):
                    self.G.nodes[node]['uncertainty'] = (5 - (Q*10) + (U*5)) / 10   # -0.5 < U < 0.5 range for nodes 
                else:
                    self.G.nodes[node]['uncertainty'] = U - (2*Q/5)     # -0.2 < U < 0.8 range for nodes
            elif (-0.5 < U):
                self.G.nodes[node]['uncertainty'] = U - (Q/3)         # -0.8 < U < -0.5 range for nodes
            else:
                # nodes closer to U = -1.0 will be harder to make them more certain than they already are.
                self.G.nodes[node]['uncertainty'] = U - max((10*Q)/(30*(-U)) - 0.34, 0)  # -1.0 < U < -0.5 range for nodes
        #print(f"NODE {node} AFTER message_influence A: {self.G.nodes[node]['alignment']} U: {self.G.nodes[node]['uncertainty']} Alienated?: {self.G.nodes[node]['alienated']} ")
    
    def switch(self, node):
        if self.G.nodes[node]['alignment'] == 'Blue':
            return 'Red'
        return 'Blue'
        
    def green_influence(self):
        for node in self.G.nodes:
            for neighbor in self.G.neighbors(node):
                if self.G.nodes[node]['uncertainty'] < self.G.nodes[neighbor]['uncertainty']:
                    self.influence(node, neighbor)

    def influence(self, sup_node, inf_node):
        A1 = self.G.nodes[sup_node]['alignment']
        U1 = self.G.nodes[sup_node]['uncertainty']
        A2 = self.G.nodes[inf_node]['alignment']
        U2 = self.G.nodes[inf_node]['uncertainty']
        c = 1000
        #print(f"BEFORE: NODE {sup_node} A = {A1} U = {U1} influences NODE {inf_node} A = {A2} U = {U2}")
        if (A1 == A2):
            if (U2 >= 0):
                if (U1 >= 0):
                    self.G.nodes[inf_node]['uncertainty'] = U2 - (U2 - U1)/(c/5)     # Change of unceratinty is 20% of the difference in uncertainty
                elif (U1 > -0.5):
                    self.G.nodes[inf_node]['uncertainty'] = U2 - (U2 - U1)/(c/4)     # Change of unceratinty is 25% of the difference in uncertainty
                else:
                    self.G.nodes[inf_node]['uncertainty'] = U2 - (U2 - U1)/(c/3)     # Change of unceratinty is 33.33% of the difference in uncertainty
            elif (U2 > -0.5):
                if (U1 > -0.5):
                    self.G.nodes[inf_node]['uncertainty'] = U2 - (U2 - U1)/(c/10)    # Change of unceratinty is 10% of the difference in uncertainty
                else:
                    self.G.nodes[inf_node]['uncertainty'] = U2 - (U2 - U1)/(c/5)     # Change of unceratinty is 20% of the difference in uncertainty
            else:
                self.G.nodes[inf_node]['uncertainty'] = U2 - (U2 - U1)/(c/10)        # Change of unceratinty is 10% of the difference in uncertainty
        elif A2 == 'Neutral':
            self.G.nodes[inf_node]['uncertainty'] = 0.5
            self.G.nodes[inf_node]['alignment'] = A1
        else:
            if (U2 >= 0):
                if (U1 >= 0):
                    if (U2 + (U2 - U1)/(c/5) > 1):
                        self.G.nodes[inf_node]['alignment'] = self.switch(inf_node)
                        self.G.nodes[inf_node]['uncertainty'] = 2 - (U2 + (U2 - U1)/(c/5))
                    else:
                        self.G.nodes[inf_node]['uncertainty'] = U2 + (U2 - U1)/(c/5)     # Change of unceratinty is 20% of the difference in uncertainty
                elif (U1 > -0.5):
                    if (U2 + (U2 - U1)/(c/4) > 1):
                        self.G.nodes[inf_node]['alignment'] = self.switch(inf_node)
                        self.G.nodes[inf_node]['uncertainty'] = 2 - (U2 + (U2 - U1)/(c/4))
                    else:
                        self.G.nodes[inf_node]['uncertainty'] = U2 + (U2 - U1)/(c/4)     # Change of unceratinty is 25% of the difference in uncertainty
                else:
                    if (U2 + (U2 - U1)/(c/3) > 1):
                        self.G.nodes[inf_node]['alignment'] = self.switch(inf_node)
                        self.G.nodes[inf_node]['uncertainty'] = 2 - (U2 + (U2 - U1)/(c/3))
                    else:
                        self.G.nodes[inf_node]['uncertainty'] = U2 + (U2 - U1)/(c/3)     # Change of unceratinty is 33.33% of the difference in uncertainty
            elif (U2 > -0.5):
                if (U1 > -0.5):
                    self.G.nodes[inf_node]['uncertainty'] = U2 + (U2 - U1)/(c/10)    # Change of unceratinty is 10% of the difference in uncertainty
                else:
                    self.G.nodes[inf_node]['uncertainty'] = U2 + (U2 - U1)/(c/5)     # Change of unceratinty is 20% of the difference in uncertainty
            else:
                self.G.nodes[inf_node]['uncertainty'] = U2 + (U2 - U1)/(c/10)        # Change of unceratinty is 10% of the difference in uncertainty
        #print(f"AFTER: NODE {sup_node} A = {A1} U = {U1} influences NODE {inf_node} A = {A2} U = {U2}")


    def update_metrics(self):
        """
        Update the metrics for the simulation, recording the number of believers
        gained and lost for each team. Prints the metrics to the console.
        """
        red_believers = sum([1 for node in self.G.nodes 
                                if self.G.nodes[node]['alignment'] == 'Red'])
        blue_believers = sum([1 for node in self.G.nodes 
                                if self.G.nodes[node]['alignment'] == 'Blue'])
        alienated = sum([1 for node in self.G.nodes 
                            if self.G.nodes[node]['alienated'] == True])
        neutral = self.num_nodes - red_believers - blue_believers
        
        last_entry = self.history[-1]
        change_red = red_believers - last_entry['Red'] if len(self.history) > 1 else 0
        change_blue = blue_believers - last_entry['Blue'] if len(self.history) > 1 else 0
        
        self.history.append({'Red': red_believers, 'Blue': blue_believers, 'Neutral': neutral})
        
        #print(f"\n# DEBUGGING Metrics History: {self.history}") if debugging else None
        print(f"\nRED BELIEVERS: {red_believers} (CHANGE: {change_red}) \nBLUE BELIEVERS: {blue_believers} (CHANGE: {change_blue}) \nNEUTRAL: {neutral}, ALIENATED: {alienated}") if debugging else None
        
        
    def plot_metrics(self):
        """
        Plot the metrics of the simulation. (Believers over time)
        """
        steps = range(1, self.num_turns + 1)
        self.history.pop(0) # Remove initial entry for plotting
        red_believers = [entry['Red'] for entry in self.history]            # ? Maybe use a traditional for loop instead of list comprehension for clarity
        blue_believers = [entry['Blue'] for entry in self.history]
        neutral = [entry['Neutral'] for entry in self.history]
        
        plt.figure(figsize=(15, 9))
        plt.plot(steps, red_believers, label='Red Believers', color='red')
        plt.plot(steps, blue_believers, label='Blue Believers', color='blue')
        plt.plot(steps, neutral, label='Neutral', color='grey')
        plt.xlabel('Step')
        plt.ylabel('Number of Believers')
        plt.title('Believers Over Time')
        plt.legend()
        plt.grid(True)
        plt.show()
        
    
    def visualise_network(self, turn):
        """
        Visualise the network at a given turn. Results in a plot of the network
        with node colours corresponding to alignment.
        
        Parameters
        ----------
        turn : int
            The turn number.
        """
        colour_map = {'Red': 'red', 'Blue': 'blue', 'Neutral': 'grey'}
        node_colours = [colour_map[self.G.nodes[node]['alignment']] for node in self.G.nodes]
        plt.figure(figsize=(15, 15))
        nx.draw_networkx_nodes(self.G, pos=self.pos, node_color=node_colours, node_size=40)
        nx.draw_networkx_edges(self.G, pos=self.pos, edge_color='gray', width=0.5, alpha=0.3)
        plt.title(f"Turn {turn // self.message_propogation_duration}\n(Step {turn})")
        plt.show() 
        
        # TODO: Integrate with plot.py once satisfied with the implementation of the Simulator
        
    
    def collect_frame_data(self, turn):
        """
        Collect data for visualisation on website UI, and for animation frames
        for testing. 
        
        Parameters
        ----------
        turn : int
            The turn number.
        """
        color_map = {'Red': 'red', 'Blue': 'blue', 'Neutral': 'grey'}
        node_colors = [color_map[self.G.nodes[node]['alignment']] for node in self.G.nodes]
        self.frames.append({'turn': turn, 'node_colors': node_colors})
        
        
    def animate_frames(self):
        """
        Animate the frames of the simulation.
        """
        fig, ax = plt.subplots(figsize=(15, 15))
        ax.set_title("Information Diffusion Simulation")
        ax.axis('off')
        
        # Keep the positions consistent
        pos = self.pos
        
        def update(frame_data):
            ax.clear()
            ax.set_title(f"Turn {frame_data['turn']//self.message_propogation_duration}\nStep {frame_data['turn']}")
            nx.draw(self.G, pos=self.pos, node_color=frame_data['node_colors'], node_size=40)
            return ax
        
        anim = FuncAnimation(fig, update, frames=self.frames, interval=1000 * self.autoplay_delay, repeat=True)
        anim.save('diffusion_animation.gif') if save_animation else None
        plt.show()
        
        
        
        
# Run the simulation
if __name__ == "__main__":
    simulator = Simulator(num_nodes=100, 
                          num_turns=500, 
                          autoplay_delay=0.2, 
                          edge_probability=0.05, 
                          initial_activation_probability=0.01,
                          base_influence_probability=1.0,
                          message_propogation_duration=10, 
                          animate=True, 
                          autoplay=True)
    
    
    
    simulator.run_simulation()
    simulator.plot_metrics()
    simulator.animate_frames() if simulator.animate else None
