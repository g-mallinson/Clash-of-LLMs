import unittest
import networkx as nx
import random
import numpy as np
from simulator import Simulator

class TestSimulator(unittest.TestCase):
    def setUp(self):
        """
        Instantiate a Simulator for testing.
        """
        self.simulator = Simulator(
            num_nodes=100,               
            network_type='erdos_renyi',
            edge_probability=0.05,
            initial_activation_probability=0.05,
            base_influence_probability=0.1,
            backlash_threshold=0.8,
            backlash_factor=0.2,
            num_steps=1,
            autoplay_delay=0.0,
            random_seed=42
        )
        
        
    def test_create_network(self):
        """
        Test network creation.
        """
        G = self.simulator.G
        self.assertIsInstance(G, nx.Graph, "G is not a NetworkX graph.")
        self.assertEqual(len(G.nodes()), self.simulator.num_nodes, 
                         "Number of nodes does not match.")
        
        
    def test_initialise_nodes(self):
        """
        Test that nodes are initialised properly.
        """
        self.simulator.initialise_nodes()
        
        for node in self.simulator.G.nodes(data=True):
            self.assertIn(node[1]['alignment'], ['Red', 'Blue', 'Neutral'], 
                          "Node alignment should be 'Red', 'Blue', or 'Neutral'.")
            self.assertIn('susceptibility', node[1], "Node should have susceptibility attribute.")
            self.assertTrue(0.0 <= node[1]['susceptibility'] <= 1.0, "Susceptibility should be between 0 and 1.")
            
            
    def test_activate_source_nodes(self):
        """
        Test initial activation of source nodes.
        """
        team = 'Red'
        message = random.choice(self.simulator.red_messages)
        initial_nodes = self.simulator.activate_source_nodes(team, message)

        expected_num_initial = int(self.simulator.initial_activation_probability * self.simulator.num_nodes)
        self.assertEqual(len(initial_nodes), expected_num_initial, "Number of initial nodes activated should match the expected value.")

        for node in initial_nodes:
            alignment = self.simulator.G.nodes[node]['alignment']
            self.assertEqual(alignment, team, f"Node {node} should have alignment '{team}'.")
            
            
    def test_propogate_message_red(self):
        """
        Test spreading of messages sent by the Red team.
        """
        initial_alignments = {node: data['alignment'] for node, data in self.simulator.G.nodes(data=True)}
        self.simulator.propogate_message(team='Red')
        
        # Check that message was selected from correct team
        self.assertEqual(self.simulator.current_message.team, 'Red', "Message team should be 'Red'.")
        
        # Check that nodes were activated correctly
        num_initial = int(self.simulator.initial_activation_probability * self.simulator.num_nodes)
        activated_nodes = [node for node, data in self.simulator.G.nodes(data=True) if data['alignment'] == 'Red']
        self.assertGreaterEqual(len(activated_nodes), num_initial, "Number of activated nodes should be at least the initial number.")
        
        # Check that message spread to correct nodes
        # As there is randomness in the process, we can't check exact values
        # We can check for expected behaviour (i.e. number of red nodes increases)
        num_red_believers = len(activated_nodes)
        self.assertGreater(num_red_believers, num_initial, "Number of red believers should increase.")
        
    
    def test_propogate_message_blue(self):
        """
        Test spreading of messages sent by the Blue team.
        """
        initial_alignments = {node: data['alignment'] for node, data in self.simulator.G.nodes(data=True)}
        self.simulator.propogate_message(team='Blue')
        
        # Check that message was selected from correct team
        self.assertEqual(self.simulator.current_message.team, 'Blue', "Message team should be 'Blue'.")
        
        # Check that nodes were activated correctly
        num_initial = int(self.simulator.initial_activation_probability * self.simulator.num_nodes)
        activated_nodes = [node for node, data in self.simulator.G.nodes(data=True) if data['alignment'] == 'Blue']
        self.assertGreaterEqual(len(activated_nodes), num_initial, "Number of activated nodes should be at least the initial number.")
        
        # Check that message spread to correct nodes
        num_blue_believers = len(activated_nodes)
        self.assertGreater(num_blue_believers, num_initial, "Number of blue believers should increase.")
        
        
    def test_update_metrics(self):
        """
        Test that metrics are updated correctly.
        """
        self.simulator.propogate_message(team='Red')
        self.simulator.update_metrics()
        
        # Check that metrics are updated correctly
        self.assertEqual(len(self.simulator.history), 1, "History should have 1 entry.")
        
        metrics = self.simulator.history[0]
        total_nodes = metrics['Red'] + metrics['Blue'] + metrics['Neutral']
        self.assertEqual(total_nodes, self.simulator.num_nodes, "Total number of nodes should match.")
            
        # Verify that number of Red believers matches the actual count from the graph
        num_red_believers = len([node for node, data in self.simulator.G.nodes(data=True) if data['alignment'] == 'Red'])
        self.assertEqual(metrics['Red'], num_red_believers, "Number of Red believers should match.")
            
    if __name__ == '__main__':
        unittest.main()