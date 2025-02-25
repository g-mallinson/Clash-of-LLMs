# ClashOfLLMs
CITS3200 (Professional Computing) project.

Clash of LLMs is a turn-based game that simulates the spread of information in a social network, using Large Language Models (LLMs) to represent two teams with competing narratives. It models how information can propagate through social networks and influence the people within them.

### Teams:
- **Red Team:** The red team represents the opponent, e.g. disinformation spreaders. Their goal is to create posts that convince the green team of their viewpoint, using any means necessary to achieve this.
- **Blue Team:** The blue team represents the ally, e.g. content moderators. Their goal is to create posts that refute the red team's claims while also convincing the green team of their viewpoint.
- **Green Team:** The green team represents the bystanders, e.g. users. Each member of this group reacts to the posts from the red and blue teams, forming their own opinions based on the persuasiveness of the arguments presented. Some members of the green team are also connected, meaning they can influence the opinions of their peers.

### How It Works:
- Initially, all members of the green team are either aligned with the blue team, red team, or undecided.
- The red team starts by posting their points, followed by the blue team arguing against the post and presenting their own points. The teams continue to refute each other's posts and provide new points on the topic.
- The blue team loses energy every time they post and will automatically lose if all their energy is depleted. This means the blue team must choose their points carefully and refute the red team effectively, or they will run out of energy.
- The red team gains influence if their claims are valid or acceptable, but loses influence if their claims are wrong or outlandish. Their influence determines how easily they can change the opinions of green team members.
- The game ends when the majority of green team opinions align with one team, or when the blue team runs out of energy.

## User Guide:
1. On the home page, selecting **START** will take you to the game page.
2. Select the red and blue team's LLM, or choose to represent them yourself.
3. Select a topic for the red and blue team to use, or add a custom topic. This topic must be a statement.
3. Set the green team graph type and parameters, then select **Generate Network** (or upload your own graph):
    - **Number of nodes:** The number of members in the green team (Whole number, 1-50).
    - **Probability of Connection:** The likelihood that two nodes will have a connection (Decimal, 0.00-1.00).
    - **Uncertainty Spread:** How difficult it is to change a green team member's opinion (Decimal, 0.00-1.00).
6. Select **RUN** to start the game.
7. Select **Play** to play the game automatically, or select **Next Turn** to step through each turn individually.

## Install Guide and Getting Started

1. **Download or Clone**  
   - Download the latest release or clone the repository and open a terminal in the project’s root directory.

2. **(Recommended) Create a Virtual Environment**  
   Use a virtual environment to manage dependencies:  
   [Python venv documentation](https://docs.python.org/3/library/venv.html).  
   - **Windows**  
        ```
        python -m venv venv
        venv\Scripts\activate
        ```
   
   - **MacOS/Linux**  
        ```
        python -m venv venv
        source venv/bin/activate
        ```

3. **Install Dependencies**  
        ```
        python -m pip install -r requirements.txt
        ```

4. **Set LLM API Keys**  
   Provide the necessary API keys (`GEMINI_API_KEY_1` for Gemini 1.0 Pro and `GEMINI_API_KEY_2` for Gemini 1.5 Flash):
   - **(Recommended) Set API keys permanently**
        
        Open `.flaskenv` with a text editor and add the API keys:
        ```
        OPENAI_API_KEY=<your-key>
        GEMINI_API_KEY_1=<your-key>
        GEMINI_API_KEY_2=<your-key>
        ```
   - **Windows**  
     - **PowerShell**  
        ```
        $Env:OPENAI_API_KEY="<your-key>"
        $Env:GEMINI_API_KEY_1="<your-key>"
        $Env:GEMINI_API_KEY_2="<your-key>"
        ```  
     - **Command Prompt (CMD)**  
        ```
        set OPENAI_API_KEY=<your-key>
        set GEMINI_API_KEY_1=<your-key>
        set GEMINI_API_KEY_2=<your-key>
        ```

   - **MacOS/Linux**  
     ```
     export OPENAI_API_KEY="<your-key>"
     export GEMINI_API_KEY_1="<your-key>"
     export GEMINI_API_KEY_2="<your-key>"
     ```

5. **Run the Flask Project**  
        ```
        flask run
        ```

6. **Access the Website**  
   Open your browser and visit:  
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

## File Structure
```
ClashOfLLMs/
|   .flaskenv
│   GreenAgents.md
│   LICENSE
│   README.md
│   requirements.txt
│   run.py
└───Clash_Of_LLMs/
    │   plot.py
    │   routes.py
    │   __init__.py
    ├───graph/
    │       config.py
    │       message.py
    │       Research.md
    │       simulator.py
    │       test.py
    │       testSimulator.py
    │       test_diffusion.py
    │       test_network.py
    │       __init__.py
    ├───static/
    │       base.css
    │       game.css
    │       game.js
    │       home.css
    │       pause-fill.svg
    │       play-fill.svg
    │       screenshot.png
    │       skip-end-fill.svg
    └───templates/
			about.html
            base.html
            game.html
            graph.html
            home.html
```

## Additional Documentation

- Flask - [Flask Documentation](http://flask.pocoo.org/)
- Bootstrap CSS - [Bootstrap Documentation](https://getbootstrap.com/)