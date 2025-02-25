from flask import jsonify, render_template, request
from flask import json, render_template
from flask import Flask, render_template, Response, send_file, make_response
from Clash_Of_LLMs import app, plot
from Clash_Of_LLMs.graph.simulator import Simulator
from Clash_Of_LLMs.graph.message import Message
from flask import request, jsonify, render_template
import csv
import google.generativeai as genai
from openai import OpenAI
import os  # To get API keys from environment variables
from os.path import relpath
relpath('./CCLMs_Results.csv')
from dotenv import load_dotenv
load_dotenv()

global simulator
simulator = Simulator(num_nodes=10, edge_probability=0.5)

# Get API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key_1 = os.getenv("GEMINI_API_KEY_1")
gemini_api_key_2 = os.getenv("GEMINI_API_KEY_2")

# Ensure API keys are present
if not openai_api_key:
    raise ValueError("OpenAI API key not set in environment variables.")
if not gemini_api_key_1 or not gemini_api_key_2:
    raise ValueError("Google Gemini API keys not set in environment variables.")

# Initialize OpenAI client with the API key from environment variables
openai_client = OpenAI(api_key=openai_api_key)

# Initialise csv contents
stats_table = []
logged_in = False

@app.route('/login', methods=['POST'])
def login():
    global logged_in
    username = request.json.get('username')
    password = request.json.get('password')
    print("us", username, password)

    # Check if the credentials are valid
    if username == "guest" and password == "password":
        logged_in = True
        return {"message": "Logged in successfully"}, 200

    # Invalid credentials
    else:
        return {"message": "Invalid credentials"}, 401
        

@app.route('/game')
def game():
    if logged_in:
        # Pass the graph data to the template
        return render_template('game.html', title="Game")
    else:
        return render_template("login.html")
    

@app.route("/")
def index():
    return render_template("home.html")

# Set the generation configuration for Google models
generation_config = {
    "temperature": 2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 200,  # Control response length
    "response_mime_type": "text/plain",
}

# Function to start the chat session for a specific model and API key (Google Gemini)
def start_team_chat(model_name):
    if model_name == "gemini-1.0-pro":
        api_key = gemini_api_key_1
    elif model_name == "gemini-1.5-flash":
        api_key = gemini_api_key_2
    else:
        raise ValueError("Unsupported model name for Gemini")

    # Configure the API key for Google Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
    )
    return model.start_chat()

@app.route('/generate_message', methods=['POST'])
def generate_message():
    data = request.json
    model_name = data.get('model_name')
    prompt = data.get('prompt')
    team = data.get('team')
    app.logger.info(f"Received request with model: {model_name}, prompt: {prompt}, team: {team}")
    
    try:
        if "gpt" in model_name:  # OpenAI model
            response = openai_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are in a debate simulation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.9
            )
            message = response.choices[0].message.content
            
        elif "gemini" in model_name:  # Google Gemini models
            chat_session = start_team_chat(model_name)
            response = chat_session.send_message(prompt)
            message = response.text
        

        app.logger.info(f"Message: {message}")
        # Set the message in the simulator, this also updates the
        # active nodes and potency based on the message content
        if "Potency" in message:
        # Create a message object with default potency and active nodes
            message_obj = Message(
                team=team.capitalize(),
                content=message,
                potency = 0.0,
                active_nodes = [],
                steps_remaining = simulator.steps_per_turn            
                )
            app.logger.info(simulator.set_message(team=team, message=message_obj))
        
            

        return jsonify({'message': message, 'team': data.get('team')})

    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/submit_user_message', methods=['POST'])
def submit_user_message():
    data = request.json
    message = data.get('message')
    team = data.get('team')
    app.logger.info(f"Received request with message: {message}, team: {team}")
    
    try:
        # Set the message in the simulator, this also updates the
        # active nodes and potency based on the message content
        message_obj = Message(
            team=team.capitalize(),
            content=message,
            potency = 0.0,
            active_nodes = [],
            steps_remaining = simulator.steps_per_turn            
            )
        app.logger.info(simulator.set_message(team=team, message=message_obj))
        
        return jsonify({'message': message, 'team': team})

    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

# About Route
@app.route('/about')
def about():
    return render_template('about.html', title="About")

# Helper function for error message
def error_message(message):
    return "<div id='graph-message'>" + message + "</div>"

def validate_parameters(params):
    '''
    validates and parses parameters
    returns:
        False, errorMessage on error
        True, parsed_parameters on success
    '''
    # Check values aren't empty
    required = ['graph_type', 'uncertainty', 'n', 'er_probability', 'ba_connections', 'ws_neighbours', 'ws_rewire_probability']
    for param in required:
        if param not in params:
            return False, f"Missing parameter: {param}"
        
    # Parse values
    try:
        graph_type = params['graph_type']
        uncertainty = float(params['uncertainty'])
        n = int(params['n'])
        er_probability = float(params['er_probability'])
        ba_connections = int(params['ba_connections'])
        ws_neighbours = int(params['ws_neighbours'])
        ws_rewire_probability = float(params['ws_rewire_probability'])
    except ValueError:
        return False, "Invalid input"
    
    # Validate range
    if not (graph_type == 'erdos_renyi' or graph_type == 'barabasi_albert' or graph_type == 'watts_strogatz'):
        return False, "graph type not recognised"
    if not (0 <= uncertainty <= 1):
        return False, "Uncertainty out of bounds"
    if not (1 <= n <= 50):
        return False, "Number of nodes out of bounds"
    if not (0 <= er_probability <= 1):
        return False, "Erdos renyi connection probability out of bounds"
    if not (1 <= ba_connections <= 5): # BA graph requires a minimum of 1 not 0
        return False, "Barabási–Albert connection count out of bounds"
    if not (0 <= ws_neighbours <= 10):
        return False, "Watts–Strogatz neighbour connection count out of bounds"
    if not (0 <= ws_rewire_probability <= 1):
        return False, "Watts–Strogatz rewire probability out of bounds"
    
    # return values
    return True, {'graph_type': graph_type, 
        'uncertainty': uncertainty, 
        'n': n, 
        'er_probability': er_probability, 
        'ba_connections': ba_connections,
        'ws_neighbours': ws_neighbours,
        'ws_rewire_probability': ws_rewire_probability}

@app.route('/initial_graph', methods=['GET'])
def initial_graph():
    '''
    (GET) Returns the initial graph.
    
    Returns:
    --------
        JSON response with the initial graph.
    '''
    graph_data = simulator.get_graph_data()
    stats = simulator.get_stats() # ! Need to implement this method in simulator.py
    return jsonify({'graph': graph_data, 'stats': stats})



@app.route('/start_simulation', methods=['POST'])
def start_simulation():
    '''
    (POST) Initializes the simulation with the current graph.
    
    Returns:
    --------
        JSON response with status: 'started'
    '''
    # Clear stats table
    for entry in stats_table:
        stats_table.remove(entry)
    return jsonify({'status': 'started'})
    
@app.route('/restart_simulation', methods=['GET'])
def restart_simulation():
    '''
    (POST) Restarts the simulation with the current graph.
    
    Returns:
    --------
        JSON response with status: 'started'
    '''
    graph_data, stats, status = simulator.restart_simulation()
    for entry in stats_table:
        stats_table.remove(entry)
    
    return jsonify({'graph': simulator.get_graph_data(), 'stats': stats})

@app.route('/get_update', methods=['GET'])
def get_update():
    '''
    (GET) Returns the next update in the simulation.
    
    Returns:
    --------
        JSON response with the next update in the simulation.
    '''
    update = simulator.step_simulation()
    try:
        print(f"Update: {update}")
        
        if update['status'] == 'running':
            stats = simulator.get_stats()
            stats_table.append(stats)
            if stats["BlueEnergy"] <= 0 or stats["AlienatedPercentage"] >= 100:
                return jsonify({'status': 'finished', 'data': update.get('data', None), 'current_step': update.get('current_step', None)})
            return jsonify({'status': 'running', 'data': update['data'], 'current_step': update['current_step'], 'stats': stats})
        else:
            return jsonify({'status': 'finished', 'data': update.get('data', None), 'current_step': update.get('current_step', None)})
    except StopIteration:
        return jsonify({'status': 'finished', 'data': None, 'current_step': None})

@app.route('/generate_network', methods=['POST'])
def generate_network():
    '''
    (POST) Generates a new network with the given parameters.
    
    Returns:
    --------
        JSON response with the new network.
    '''
    params = request.json
    if not params:
        return jsonify({'status': 'error', 'message': 'No parameters provided'}), 400
    
    success, data = validate_parameters(params)
    if not success:
        return jsonify({'status': 'error', 'message': data}), 400
    
    graph_type = data['graph_type']
    uncertainty = round(float(data['uncertainty']), 2)
    n = int(data['n'])
    er_probability = round(float(data['er_probability']), 2)
    ba_connections = data['ba_connections']
    ws_neighbours = data['ws_neighbours']
    ws_rewire_probability = data['ws_rewire_probability']
    
    global simulator
    
    simulator = Simulator(num_nodes=n, edge_probability=er_probability)
    simulator.create_network_custom(network_type=graph_type, 
                                    uncertainty=uncertainty, 
                                    n=n, 
                                    er_probability=er_probability,
                                    ba_connections=ba_connections,
                                    ws_neighbours=ws_neighbours,
                                    ws_rewire_probability=ws_rewire_probability)
    simulator.initialize_simulation()
    
    graph_data = simulator.get_graph_data()
    stats = simulator.get_stats()
    print(f"Stats: {stats}")
    
    return jsonify({'status': 'success', 'graph': graph_data, 'stats': stats})

def generate_csv():
    csv_content = "sep=|\nTurn|Team|Message|Potency|Red Alignment|Blue Alignment|Neutral Alignment|Red Influence|Blue Energy\n"
    turn_counter = 2
    total_pop = stats_table[0]["Red"] + stats_table[0]["Blue"] + stats_table[0]["Neutral"]
    for entry in stats_table:
        csv_content += f"{turn_counter//2}|{entry['CurrentTeam']}|{entry['CurrentMessageContent']}|{entry['CurrentPotency']}|{entry['Red']}/{total_pop} ({entry['RedPercentage']}%)|{entry['Blue']}/{total_pop} ({entry['BluePercentage']}%)|{entry['Neutral']}/{total_pop} ({entry['NeutralPercentage']}%)|{total_pop - entry['Alienated']}/{total_pop} ({100 - entry['AlienatedPercentage']}%)|{entry['BlueEnergy']}\n"        
        turn_counter += 1
    return csv_content

@app.route("/download_csv")
def download_csv():
    if len(stats_table) == 0:
        return "Nothing to download"
    csv_data = generate_csv() 
    response = make_response(csv_data)
    cd = 'attachment; filename=CLLMs_results.csv'
    response.headers['Content-Disposition'] = cd 
    response.mimetype='text/csv'

    return response


if __name__ == "__main__":
    app.run(debug=True)