from dataclasses import dataclass

@dataclass
class Message:
    """
    A message that can be sent to a node in the network. Used to influence the
    alignment of nodes.
    
    Attributes
    ----------
    team : str
        The team that the message is associated with ('Red' or 'Blue').
    potency : float
        The potency of the message (between 0 and 1).
    content : str
        The body of the message
    """
    team: str
    potency: float  
    content: str
    active_nodes: list
    steps_remaining: int