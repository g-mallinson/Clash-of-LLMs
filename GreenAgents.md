### Draft on how green team changes their minds
Each turn, a blue or red message will be spread throughout the green team. Once the message has finished spreading, the green team will spread their opinions to those they have edges with. Each pair of nodes will only be able to spread their ideas to each other once. The order in which nodes spread their opinions will be done where the most certain nodes go first. Nodes will not necessarily spread their ideas to every node they are connected with, a slightly modified version of the function used to determine probability of a message being spread will be used.

## Process of Green Team Opinion Changing
People will change their minds about a topic when exposed to a strong, potent message which challenges their beliefs. For example, an anti-vaxxer may change sides when reading an article about how the anti-vax movement was championed by a fraud. However, people also change their beliefs based on who they are surrounded by rather than because of exposure to a certain message. If a Liberal party voter found themselves to fall in with a group of good freiends who are Labor party voters, they may over time change to a Labor party voter. Although there are many other means by which a person's opinions can be changed (i.e. bad experiences with someone of a certain viewpoint, upbringing, manipulation), the aforementioned reasons will be the ones modelled for how Green Team changes their stances.

To model how messages change people's minds, it must be known the variables to consider first. Each node has an uncertainty level, which side they are on, and if they have alienated themselves from red team messages, and all messages have a potency level. These are the only 3 variables that need to be considered when modelling green team stance changes. Therefore, when constructing the function which changes a green team node's opinion based on the message they received, the paramters required are:

```python
    node Node               # A node object which received the message.
    ├── int alignment       # node object attribute: Which position the node stands on. 0 = Blue, 1 = Red
    ├── bool alienated      # node objec attribute: Determines if a node receives red team messages.
    └── float uncertainty   # node object attribute: How certain a node. Ranges from 1.0 to (-1.0), where: 1.0 = certain of their stance, and (-1.0) = not sure about their stance.
    message Message
    ├── int side        # The team which the message belongs to. 0 = Blue, 1 = Red
    └── float potency   # How 'strong' the message the node received is.
```

### Code for Green Agent Responding to Messages
```python
def switch(self, node):
    if self.G.nodes[node]['alignment'] == 'Blue':
        return 'Red'
    return 'Blue'

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

# Determines if a message reaches a node
def message_reach(node, message):
    if (message.side != 'Red' and node.alienated != True):
        message(node, message)
```
Now it must be modeled how people have their minds changed by the people around them. However, certain rules must be established first to: establish an order, determine when influencing phase stops, and prevent unrealistic situations occurring. An example of an unrealistic situation is Node 1 influencing Node 2 even though Node 1 has a much higher uncertainty than Node 2. These will be the following rules of nodes influencing each other:
- A node of the same alignment as another node can only influence that other node if they are more certain. E.g. Node 1 has an uncertainty of -0.5 and Node 2 has an uncertainty of -0.3. Hence, Node 1 can influence Node 2, but Node 2 can't influence Node 1.
- A node can only influence their neighbouring nodes once.
- A node cannot make another node more certain than they are. E.g. Node 1 has uncertainty -0.5, Node 2 has uncertainty -0.45. Node 1 will influence Node 2, however, Node 2 can only be influenced to a maximum of -0.5 uncertainty.
- Nodes of the highest certainty will influence all of their nodes first.
With these rules established, we can now program how green agents will influence each other.

### Code for Green Agents Influencing Each Other

```python
def switch(self, node):
    if self.G.nodes[node]['alignment'] == 'Blue':
        return 'Red'
    return 'Blue'

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
        
def green_influence(self):
    for node in self.G.nodes:
        for neighbor in self.G.neighbors(node):
            if self.G.nodes[node]['uncertainty'] < self.G.nodes[neighbor]['uncertainty']:
                self.influence(node, neighbor)
```


