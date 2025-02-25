# Information Diffusion Simulations: Research and Proposed Methodology

*Version 1.0.2*

*DRAFT*

*Date: 17 September 2024*

## Contents
- [Information Diffusion Simulations: Research and Proposed Methodology](#information-diffusion-simulations-research-and-proposed-methodology)
  - [Contents](#contents)
  - [1. Introduction](#1-introduction)
  - [2. Literature Review](#2-literature-review)
    - [2.1. Information Diffusion Models](#21-information-diffusion-models)
    - [2.2. Network Structures in Social Networks](#22-network-structures-in-social-networks)
    - [2.3. Susceptibility and Influence in Networks](#23-susceptibility-and-influence-in-networks)
    - [2.4. Message Potency and Backlash Effects](#24-message-potency-and-backlash-effects)
  - [3. Methodology](#3-methodology)
    - [3.1. Simulation Framework](#31-simulation-framework)
    - [3.2. The Population Model](#32-the-population-model)
    - [3.3. Messages](#33-messages)
    - [3.4. Propagation Mechanism](#34-propagation-mechanism)
    - [3.5. Metrics and Evaluation](#35-metrics-and-evaluation)
    - [3.6. Visualisation](#36-visualisation)
  - [4. Design Considerations](#4-design-considerations)
    - [4.1. Scalability and Performance](#41-scalability-and-performance)
    - [4.2. Flexibility and Extensibility](#42-flexibility-and-extensibility)
    - [4.3. Reproducibility:](#43-reproducibility)
    - [5. Future Work](#5-future-work)

## 1. Introduction

The simulation will be designed to model the spread of harmful and debunking information within a population network. This tool assists in understanding how different types of messages propagate, influence individuals, and impact overall belief alignments. The foundational logic behind the simulation aims to achieve a realistic representation of information dynamics based on established research.

## 2. Literature Review

### 2.1. Information Diffusion Models

An Information Diffusion Model is a mathematical framework used to describe the propogation of information through a network. We will look at two of these models, which are commonly used in this field:

- **Independent Cascade (IC) Model:**
  Each active node in a network has a single chance to activate its inactive neighbours with a certain probability. Formed by Kempe, Kleinberg, and Tardos (2003)[^1], this model is widely used due to its simplicity and applicability to various scenarios related to information diffusion.

- **Susceptible-Infected-Recovered (SIR) Model:**
  Categorises individuals into susceptible, infected, and recovered states. Primarily used for contagion simulations for epidemiological studies, it has been adapted for information diffusion by using an "infected" person as an analogue for an individual who has adopted a message, thus, information spread can be thought of as a "*social* contagion."

This simulation will adopt a hybrid approach, making additions to the IC model to incorporate individual susceptibility and message "potency," aiming to produce a more realistic simulation of information spread through a population.

### 2.2. Network Structures in Social Networks

The network topology used in modelling a population's social structure significantly influences how the information diffusion simulation will play out. Commonly used topologies include:

- **Erdos-Renyi (ER) Networks:**
  Assigns randomly distributed edges, suitable for modeling scenarios with uniform connectivity. 

- **Scale-Free Networks:**
  Features a power-law degree distribution, these networks can be representative of many real-world social networks, as they contain highly connected "hubs," (Barabasi & Albert, 1999)[^2].

- **Small-World Networks:**
  Combines high clustering with short average path lengths, these networks capture the "six degrees of separation" phenomenon (Wikipedia contributors, 2024)[^3] observed in large social structures, can be generated using a Watts-Strogatz model (Watts & Strogatz, 1998)[^4].

Our initial implementation utilises the ER model for simplicity's sake, with provisions to switch to other topologies to better emulate specific networks as needed.

### 2.3. Susceptibility and Influence in Networks

Individual susceptibility is the likelihood of an individual adopting and spreading a message upon exposure. Factors influencing susceptibility include:

- **Personal Beliefs and Biases:**  
  Pre-existing alignments (e.g., political affiliations) affect receptiveness to certain messages.

- **Network Position:**  
  Highly connected individuals (hubs) can exert significant influence on information spread.

Incorporating susceptibility into diffusion models enhances their predictive power, allowing us to account for individual differences within the population.

### 2.4. Message Potency and Backlash Effects
*(backlash mechanism still in research phase, not guaranteed in final product)*
Message potency quantifies the strength and believability of a message. High-potency messages are more likely to be adopted but may also trigger backlash if perceived as too extreme or unbelievable. Backlash effects can lead to:

- **Decreased Susceptibility:**  
  Overexposure to high-potency messages may make individuals less receptive to subsequent messages. If messages become too outlandish, it may put them off the group ideology as they realise they may have been involved in irrational *groupthink* or *group-shift*.

- **Alignment Shifts:**  
  Extreme messages can cause shifts in individuals' beliefs, either reinforcing or opposing their initial stance.

Understanding the relationship between potency and possible backlash is useful for accurately modeling information spread and its impact on population beliefs.

## 3. Methodology

### 3.1. Simulation Framework

**Python** was selected for its collection of readily available libraries. We intend to use:

**NetworkX:**
To handle creation and manipulation of networks, and modelling the simulated population.

**Matplotlib:**
*(For testing purposes, and may be implemented in finished product)*
To implement visualisation features and record the [measurements obtained](#35-metrics-and-evaluation) during the simulation.

**NumPy & Random:**
For numerical operations and randomness required for spawning populations representing a realistic sample set of individuals to make up our social network.

### 3.2. The Population Model

The population is represented as a network graph where the nodes are the individuals, and the edges symbolise social connections. Each node will be assigned a:

- **Susceptibility Score:**  
  A continuous value between 0 and 1 indicating the individual's openness to adopting messages. Think of it as a measure of how easy a person is to convince or manipulate into changing their mind.

- **Current Alignment:**  
  Categorised as **Red**, **Blue**, or **Neutral**, reflecting the individual's current belief state.

For the first iteration of this tool, initial alignments will be set to **Neutral**, with susceptibility scores randomly distributed within a specified range to simulate diversity in receptiveness.

### 3.3. Messages

Two types of messages will be introduced to the network:

- **Harmful Messages (Red Team):**  
  Aim to spread misinformation, characterised by negative alignment shifts.

- **Debunking Messages (Blue Team):**  
  Intended to counteract harmful messages and promote truthful information. Representative of perhaps a government organisation attempting to prevent the spread of potentially dangerous beliefs.

Each message is defined by:

- **Team:**  
  Indicates whether it's a Red or Blue message.

- **Potency Score:**  
  Describes the message's assigned influence strength.

- **Content:**  
  The actual information being disseminated.

Predefined message pools will be used in the testing phase for each team to maintain a standard testbed whilst the diffusion model is developed. Later, we will use an LLM such as Google's Gemini to formulate messages for each team, so we can test the capabilities of these tools with regard to generating misinformation or debunking it, and understand the possible use cases for both sides as they become more advanced.

### 3.4. Propagation Mechanism
*The propogation mechanism is a work in progress, however the current model is as follows*
Building upon the Independent Cascade model, the propagation mechanism incorporates:

- **Influence Probability Calculation:**  
  ```math
  p = \text{Base Probability} \times \text{Potency Score} \times \text{Susceptibility}

  ```

  This formula determines the likelihood of a message spreading from one individual to another.

- **Turn-Based Propagation:**  
  Red and Blue teams alternate turns, each sending out a message to initiate propagation.

- **Backlash Handling:**  
  Messages exceeding a potency threshold trigger a backlash effect, reducing the susceptibility of affected individuals:
  ```math
  \text{Susceptibility} \leftarrow \text{Susceptibility} \times (1 - \alpha)
  ```
  where $\alpha$ is the backlash factor.

- **Message Spread Simulation:**  
  Messages propagate through the network based on calculated probabilities, updating individuals' alignments accordingly.

This approach tries to find a balance between realistic diffusion dynamics and computational efficiency.

### 3.5. Metrics and Evaluation

To assess the simulation's outcomes, the following metrics are tracked:

- **Believers Gained/Lost per Team:**  
  Measures the number of individuals adopting (or abandoning) each team's message.

- **Overall Simulation Totals:**  
  Calculates the total believers gained and lost across all steps.

- **Step-wise Reporting:**  
  Provides insights at each time step, for analysis of diffusion trends over time.

These metrics may be expanded later, but for now, they allow for a reasonable evaluation of information spread dynamics and the relative effectiveness of Red and Blue messages.

### 3.6. Visualisation

Visual representation will help us understand the diffusion process. Strategies used include:

- **Network Graphs:**  
  Nodes are colour-coded based on alignment (Red, Blue, Neutral), providing a clear view of belief distributions.

- **Consistent Layouts:**  
  Utilising a fixed layout (e.g., spring layout with a fixed seed) ensures stability across visual updates.

- **Dynamic Updates:**  
  Real-time visualisation updates reflect changes in the network state after each step.

This will facilitate both real-time monitoring and post-simulation analysis of information diffusion.

## 4. Design Considerations

### 4.1. Scalability and Performance
We aim to have a simulation that can run on consumer-grade hardware, through use of:

- **Optimised Algorithms:**
  NetworkX provides well optimised functions which should handle high node counts without unreasonable performance degradation.

- **Efficient Data Structures:**
  Appropriate data structures will be used to  minimise overhead during the propogation simulation.

- **(Potential Future Scope Expansion) Parallel Processing:**
  Maybe use parallel computing techniques to boost performance for larger networks should it be necessary.

### 4.2. Flexibility and Extensibility

To allow for future expansion, we should implement the following:

- **Modular Code Structure:**  
  Separating functionalities into distinct modules (e.g., network setup, propagation, visualisation) to facilitate easy modifications and feature additions.

- **Parameter Configurations:**  
  Allowing parameters (e.g., network type, susceptibility range, number of nodes) to be adjustable without touching the source code.

- **Support for Multiple Network Topologies:**  
  Enabling easy switching between different network structures to model various social scenarios. Also means we can fine-tune the logic behind the simulation to suit more generalised input.

### 4.3. Reproducibility:

Important for validation and testing:

- **Random Seed Control:**
  Allowing the use of random seeds, but reporting the seed at some point during the execution for later re-use, ensuring consisten network generation across multiple runs.

- **Documentation:**
  Could provide guidelines on parameter settings and seed configurations for users to replicate our results.

### 5. Future Work

This is just a "casual" section for brainstorming potential expansions of scope:

- **Advanced Message Interactions:**  
  Implementing mechanisms where messages can influence each other's potency, such as debunking messages reducing the effectiveness of related harmful ones.

- **Temporal Decay:**  
  Introducing decay factors where message influence diminishes over time unless reinforced by additional propagation. So messages can "fade out" of the public eye, much like real life where seemingly significant news loses relevancy within a population once people stop talking about it.

- **Scalability Enhancements:**  
  Optimising the simulation to handle larger networks (e.g., thousands of nodes) through parallel processing or more efficient algorithms.



[^1]: Kempe, D., Kleinberg, J., & Tardos, É. (2003, August). Maximizing the spread of influence through a social network. In Proceedings of the ninth ACM SIGKDD international conference on Knowledge discovery and data mining (pp. 137-146).

[^2]: Barabási, A. L., & Albert, R. (1999). Emergence of scaling in random networks. science, 286(5439), 509-512.

[^3]: Wikipedia contributors. (2024, September 14). Six degrees of separation. In Wikipedia, The Free Encyclopedia. Retrieved 16:13, September 16, 2024, from https://en.wikipedia.org/w/index.php?title=Six_degrees_of_separation&oldid=1245690519

[^4]: Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440–442. https://doi.org/10.1038/30918