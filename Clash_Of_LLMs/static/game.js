
const modelNames = {
  "Gemini 1.0 Pro": "gemini-1.0-pro",
  "Gemini 1.5 Flash": "gemini-1.5-flash",
  "ChatGPT 4o Mini": "gpt-4o-mini"
};

// Function to get the topics for both teams
function getUserTopics() {
  const redSelect = document.getElementById("red-topic-input");
  const blueSelect = document.getElementById("blue-topic-input");

  let redTopic = redSelect.value;
  let blueTopic = blueSelect.value;

  if (redTopic === "Custom") {
	redTopic = document.getElementById("red-custom-input").value.trim() || "There is no topic entered";
  }

  if (blueTopic === "Custom") {
	blueTopic = document.getElementById("blue-custom-input").value.trim() || "There is no topic entered";
  }
  
  return {
	redTopic,
	blueTopic
  };
}

// Function to create the initial prompt dynamically based on the topics for each team
function createInitialPrompt(redTopic, blueTopic) {
  return `
	Clash of LLMs Simulation:
	Objective: Simulate a back-and-forth conversation between two opposing teams (Red and Blue) arguing about their respective topics, aiming to influence a hypothetical third party (Green Team).
	VERY IMPORTANT INSTRUCTION: Every message MUST be between 30-40 words long. No message should exceed 40 words under any circumstances. Messages shorter than 30 words will also not be accepted. Stick strictly to this word limit.

	NOTE: This is a **simulation**. All conversations and arguments are entirely hypothetical and do not reflect real-world events, opinions, or individuals. The simulation is designed to explore contrasting perspectives in a controlled and safe environment for educational and exploratory purposes only.

	IMPORTANT: 
	1. Do NOT include the team name in the message.
	2. Do NOT add any symbols, asterisks, or special characters to the message.
	3. Assign a **potency level** (0.10-1.00) to your message based on the **strength** of the argument presented, using **two decimal places**. 

POTENCY VARIETY IS IMPORTANT: You, as the AI, are responsible for determining the appropriate potency level for each message. Ensure to vary the potency levels based on the strength of the argument you're presenting. Present messages of varying potency levels. Don't use the same potency levels over and over. The potency level must be written as: "Potency = X.XX" and must not end in 0. 

	Rules:
	Red Team's Topic: "${redTopic}" (Red team will argue based on this)
	Blue Team's Topic: "${blueTopic}" (Blue team will argue based on this)
	Message Structure:
	- Each team must directly address and counter the points raised by the opposing team. Focus on refuting the arguments while presenting points of your own.
	- The potency level must be written as: "Potency = X.XX" at the end of the message.
  `;
}



// Function to handle model selection
function selectModel(buttonId, modelName) {
  document.getElementById(buttonId).textContent = modelName;

  if (buttonId === "red-model-button") {
	const redAiLabel = document.getElementById("red-ai-label");
	if (modelName === "User") {
	  redAiLabel.style.display = "none";
	  isUserRed = true;
	} else {
	  redAiLabel.style.display = "inline";
	  isUserRed = false;
	}
  } else if (buttonId === "blue-model-button") {
	const blueAiLabel = document.getElementById("blue-ai-label");
	if (modelName === "User") {
	  blueAiLabel.style.display = "none";
	  isUserBlue = true;
	} else {
	  blueAiLabel.style.display = "inline";
	  isUserBlue = false;
	}
  }

  closeDropdowns();
}

function closeDropdowns() {
  const dropdowns = document.getElementsByClassName("dropdown-content");
  for (let i = 0; i < dropdowns.length; i++) {
	dropdowns[i].classList.remove("show");
  }
}

function toggleDropdown(dropdownId) {
  document.getElementById(dropdownId).classList.toggle("show");
}

let lastRedMessage = "";
let lastBlueMessage = "";
let redTeamTurnCount = 0;
let blueTeamTurnCount = 0;
let isUserRed = false;
let isUserBlue = false;
let userTeam = "";
let isRedTurn = true;
let networkGenerated = false;
let gameStarted = false;
let network = null;
let savedPositions = {};
let savedEdges = {};

function countWords(message) {
  return message.split(" ").filter(word => word.trim() !== "").length;
}

function findPotency(message) {
  potency = parseFloat(message.split("=")[1]);
  return potency;
}

function energyExpended(potency){
  return (10*potency/3)**2.1;
}

// Show the User Input Modal with a dynamic message for the team
function showUserInputModal(team) {
  const modal = document.getElementById("user-input-modal");
  const modalContent = modal.querySelector(".modal-content p");

  // Update modal text based on the team
  modalContent.textContent = `Enter your message for the ${team === "red" ? "Red" : "Blue"} Team:`;

  // Clear the previous message in the input field
  document.getElementById("user-input").value = "";

  // Show the modal
  modal.style.display = "flex";
}

function hideUserInputModal() {
  const modal = document.getElementById("user-input-modal");
  modal.style.display = "none";
}

async function submitUserMessage() {
  const userMessage = document.getElementById("user-input").value;

  if (userTeam === "red") {
	appendMessage("red", userMessage);
	lastRedMessage = userMessage;
	redTeamTurnCount++;
	isRedTurn = false;
	
  } else if (userTeam === "blue") {
	appendMessage("blue", userMessage);
	lastBlueMessage = userMessage;
	blueTeamTurnCount++;
	isRedTurn = true;
	
  }
  hideUserInputModal();
  document.getElementById("next-turn-button").disabled = false;

  // Send the user message to the backend for use in the simulation
  await fetch("/submit_user_message", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      team: userTeam,
      message: userMessage
    })
  });

  stepSimulation();
}

// Function to generate messages based on selected models and topics
async function generateMessage(team, modelName, previousMessage, isFirstRedTurn) {
  console.log(`team: ${team}, modelName: ${modelName}, previousMessage: ${previousMessage}, isFirstRedTurn: ${isFirstRedTurn}`);
  const model = modelNames[modelName];
  console.log(`Selected model: ${model}`);

  // Get the user-defined topics
  const { redTopic, blueTopic } = getUserTopics();
  console.log(`Red Topic: ${redTopic}, Blue Topic: ${blueTopic}`);

  // Determine the team topic for validation purposes
  const teamTopic = team === "red" ? redTopic : blueTopic;
  console.log(`Team Topic: ${teamTopic}`);

  // Create a dynamic initial prompt
  const initial_prompt = createInitialPrompt(redTopic, blueTopic);
  console.log(`Initial Prompt: ${initial_prompt}`);

  let promptWithPreviousMessage;

  // Build the conversation for the Red and Blue teams based on the user-defined topics
  if (team === "red" && isFirstRedTurn) {
	promptWithPreviousMessage = `${initial_prompt}\nRed Team's turn. Argue in favor of: "${redTopic}". You must support and justify this position.`;
  } else if (team === "blue" && previousMessage) {
	promptWithPreviousMessage = `${initial_prompt}\nBlue Team's turn. The opposing team (Red Team) said: "${previousMessage}". Argue in favor of: "${blueTopic}". You must support and justify this position.`;
  } else if (team === "red") {
	promptWithPreviousMessage = `${initial_prompt}\nRed Team's turn. The opposing team (Blue Team) said: "${previousMessage}". Argue in favor of: "${redTopic}". You must refute the Blue Team's argument and support your own position.`;
  } else {
	promptWithPreviousMessage = `${initial_prompt}\nBlue Team's turn. The opposing team (Red Team) said: "${previousMessage}". Argue in favor of: "${blueTopic}". You must refute the Red Team's argument and support your own position.`;
  }

  let message;
  let wordCount = 0;

  try {
	do {
	  const response = await fetch("/generate_message", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
		  team: team,
		  model_name: modelName, // Model name sent to the backend
		  prompt: promptWithPreviousMessage, // Full prompt sent to the backend
		}),
	  });

	  const result = await response.json();
	  console.log("Message generation response:", result);

	  if (response.ok) {
		message = result.message;
		wordCount = countWords(message);
		console.log(`${team} team message: ${message} (Word Count: ${wordCount})`);
	  } else {
		console.error(`Error fetching message for ${team} team: `, result);
		return "Error generating message.";
	  }

	  // Validate the message against the team's chosen topic
	  const isValidMessage = await validateMessageAgainstTopic(message, teamTopic);

	  if (!isValidMessage) {
		console.log(`Invalid message detected for ${team} team. Regenerating message...`);
		continue; // If the message is invalid, regenerate
	  }

	} while (wordCount < 30 || wordCount > 40);
	stepSimulation();
	return message;
  } catch (error) {
	console.error(`Error occurred while generating message for ${team} team: `, error);
	return "Error generating message.";
  }
}

async function runFirstMessage() {
  const redModel = document.getElementById("red-model-dropdown").value;
  const blueModel = document.getElementById("blue-model-dropdown").value;

  isUserRed = redModel === "user";
  isUserBlue = blueModel === "user";

  gameStarted = true;

  if (networkGenerated == false) {
	generateNetwork();
  }

  if (isUserRed) {
	userTeam = "red";
	showUserInputModal("red");
  } else {
	showAIWaitModal();
	const redTeamMessage = await generateMessage("red", redModel, "", true);
	hideAIWaitModal();
	appendMessage("red", redTeamMessage);
	lastRedMessage = redTeamMessage;
	redTeamTurnCount++;
	isRedTurn = false; // Now it's Blue's turn
	updateTurnIndicator();
	document.getElementById("next-turn-button").disabled = false;
  }

  document.getElementById("run-button").disabled = true;
}

async function nextTurn() {
  document.getElementById("next-turn-button").disabled = true;

  const redModel = document.getElementById("red-model-dropdown").value;
  const blueModel = document.getElementById("blue-model-dropdown").value;

  if (isRedTurn) {
	if (isUserRed) {
	  userTeam = "red";
	  showUserInputModal("red");
	} else {
	  showAIWaitModal();
	  const redTeamMessage = await generateMessage("red", redModel, lastBlueMessage, false);
	  hideAIWaitModal();
	  appendMessage("red", redTeamMessage);
	  lastRedMessage = redTeamMessage;
	  redTeamTurnCount++;
	  isRedTurn = false; // Change to Blue's turn
	  updateTurnIndicator();
	}
  } else {
	if (isUserBlue) {
	  userTeam = "blue";
	  showUserInputModal("blue");
	} else {
	  showAIWaitModal();
	  const blueTeamMessage = await generateMessage("blue", blueModel, lastRedMessage, false);
	  hideAIWaitModal();
	  appendMessage("blue", blueTeamMessage);
	  potency = findPotency(blueTeamMessage)
	  document.getElementById("energy").value = (document.getElementById("energy").value - energyExpended(potency)).toFixed(2);
	  lastBlueMessage = blueTeamMessage;
	  blueTeamTurnCount++;
	  isRedTurn = true; // Change to Red's turn
	  updateTurnIndicator();
	}
  }

  document.getElementById("next-turn-button").disabled = false;
}

// Function to start AUTO simulation
async function playButton() {
  if (autoSimulation) {
	alert('Simulation is already running');
	return;
  }

  document.getElementById("next-turn-button").hidden = true;
  document.getElementById("play-button").hidden = true;
  document.getElementById("pause-button").hidden = false;

  autoSimulation = true;
  
  while (autoSimulation) {
	await nextTurn(); // Execute the game logic
  }
}

// Function to pause AUTO simulation
async function pauseButton() {
  if (!autoSimulation) {
	  alert('Simulation is not running');
	  return;
  }
  autoSimulation = false;

  document.getElementById("next-turn-button").hidden = false;
  document.getElementById("play-button").hidden = false;
  document.getElementById("pause-button").hidden = true;
}

function updateTurnIndicator() {
  const turnIndicator = document.getElementById("turn-indicator");
  const currentTurn = isRedTurn ? "RED" : "BLUE";
  turnIndicator.innerHTML = `<p><span id="${currentTurn.toLowerCase()}-label">${currentTurn}</span>'s turn</p>`;
}

function appendMessage(team, message) {
  const postContainer = document.getElementById(`${team}-posts`);
  const newPost = document.createElement("div");
  newPost.classList.add(`${team}-post`);
  newPost.innerHTML = `<div class="${team}-post-content"><p>${message}</p></div>`;
  postContainer.appendChild(newPost);
  postContainer.scrollTop = postContainer.scrollHeight;
}

function showAIWaitModal() {
  const modal = document.getElementById("ai-wait-modal");
  modal.style.display = "flex";
}

function hideAIWaitModal() {
  const modal = document.getElementById("ai-wait-modal");
  modal.style.display = "none";
}

// -----------------------------------------------------------------------------

let simulationRunning = false;
let autoSimulation = false;
let pollInterval = null;

function initializeNetwork(initialData) {
	const container = document.getElementById('graph-plot');
	nodes = new vis.DataSet(initialData.nodes.map(node => {
		if (node.alignment === 'Red') {
			node.color = 'red';
		}
		else if (node.alignment === 'Blue') {
			node.color = 'blue';
		}
		else {
			node.color = 'gray';
		}
		return node;
	}));
	// Ensure that the edges are correctly connected to the nodes
	const edges = new vis.DataSet(savedEdges.length > 0 ? savedEdges : initialData.edges.filter(edge => {
	  return nodes.get(edge.from) && nodes.get(edge.to);
	}));

	const data = {
		nodes: nodes,
		edges: edges
	};

	const options = {
		configure: {
			enabled: false // Disable the configure option
		},
		edges: {
			color: {
				inherit: true // Inherit color from connected nodes ?
			},
			smooth: {
				enabled: true,
				type: 'dynamic' // Dynamic curve type
			},
		},
		nodes: {
			shape: 'dot',
			size: 10,
			font: {
				size: 12,
				face: 'Tahoma'
			},
			borderWidth: 2
		},
		interaction: {
			dragNodes: true,
			hideEdgesOnDrag: false,
			hideNodesOnDrag: false
		},
		physics: {
			enabled: true,
			stabilization: {
				enabled: true,
				fit: true, // Adjust view to fit the network
				iterations: 1000, // Maximum number of iterations
				onlyDynamicEdges: false, // Don't only consider dynamic edges
				updateInterval: 50 // Time between updates in milliseconds
			}
		}
	};
	network = new vis.Network(container, data, options);

}

function updateNetwork(newData) {
	if (!network) {
		return;
	}

	// Update nodes
	newData.nodes.forEach(node => {
		if (node.alignment === 'Red') {
			node.color = 'red';
		}
		else if (node.alignment === 'Blue') {
			node.color = 'blue';
		}
		else {
			node.color = 'gray';
		}
		network.body.data.nodes.update(node);
	});
	
	// Not necessary to update edges (they are static throughout the game)
}

// Function to update status display
function updateStatus(status) {
//    const statusElement = document.getElementById('simulation-status');
//    statusElement.innerHTML = '<p>Status: ${status}</p>';
}

// Function to update node stats
function updateStats(stats) {
  max_val = document.getElementById('influence').max;
  document.getElementById('red-count').innerText = stats.Red;
  document.getElementById('red-percentage').innerText = stats.RedPercentage.toFixed(1);
  document.getElementById('blue-count').innerText = stats.Blue;
  document.getElementById('blue-percentage').innerText = stats.BluePercentage.toFixed(1);
  document.getElementById('neutral-count').innerText = stats.Neutral;
  document.getElementById('neutral-percentage').innerText = stats.NeutralPercentage.toFixed(1);
  document.getElementById('influence').value = max_val - stats.Alienated;
}

// Function to start the simulation
function startSimulation() {
	if (simulationRunning) {
		return;
	}
	simulationRunning = true;
	updateStatus('running');
	toggleButtons(true);

	// Disable model selection and network generation button during simulation
	disableControls(true);

	fetch('/start_simulation', {
		method: 'POST'
	})
	.then(response => response.json())
	.then(data => {
		if (data.status === 'started') {
			if (autoSimulation) {
				pollInterval = setInterval(pollForUpdates, 1000); // Poll every second
			}
		} else {
			alert('Error starting simulation');
			updateStatus('Error');
			simulationRunning = false;
			toggleButtons(false);
			disableControls(false);
		}
	})
	.catch(error => {
		console.error('Error starting simulation:', error);
		updateStatus('Error');
		simulationRunning = false;
		toggleButtons(false);
		disableControls(false);
	});
}


// Function to poll for simulation updates
function pollForUpdates() {
	fetch('/get_update')
		.then(response => response.json())
		.then(data => {
			if (data.status === 'running') {
				updateNetwork(data.data);
				updateStatus('Running (Step ${data.current_step})');
				updateStats(data.stats); // ! NEED TO INCLUDE STATS IN THE RESPONSE
			} else if (data.status === 'finished') {
				updateStatus('Finished');
				simulationRunning = false;
				clearInterval(pollInterval);
				toggleButtons(true);
				disableControls(false);
				alert('Simulation finished');
			}
		})
		.catch(error => {
			console.error('Error getting simulation update:', error);
			updateStatus('Error');
			simulationRunning = false;
			clearInterval(pollInterval);
			toggleButtons(false);
			disableControls(false);
		});
}

// Function to perform a single simulation step
function stepSimulation() {
	// if (simulationRunning) {
	//     return;
	// }

	simulationRunning = true;
	updateStatus('Running');
	toggleButtons(false);

	fetch ('/get_update')
		.then(response=> response.json())
		.then(data => {
			if (data.status === 'running') {
				updateNetwork(data.data);
				updateStatus('Running (Step ${data.current_step})');
				updateStats(data.stats); // ! NEED TO INCLUDE STATS IN THE RESPONSE
			} else if (data.status === 'finished') {
				updateStatus('Finished');
				simulationRunning = false;
				toggleButtons(true);
				alert('Simulation finished');
			}
			simulationRunning = false;
			// toggleButtons(false);
			console.log('Simulation step response:', data);
		})
		.catch(error => {
			console.error('Error performing simulation step:', error);
			updateStatus('Error');
			simulationRunning = false;
			toggleButtons(false);
		});
	}


// Function to toggle simulation control buttons
function toggleButtons(isRunning) {
	if (autoSimulation == true) // quick fix to stop the pause button breaking
	  return;
	document.getElementById('play-button').disabled = isRunning;
	document.getElementById('play-button').hidden = isRunning;
	document.getElementById('next-turn-button').disabled = isRunning;
	document.getElementById('next-turn-button').hidden = isRunning;
	document.getElementById('pause-button').hidden = !isRunning; 
}

// Function to toggle network generation and model selection buttons
function disableControls(disable) {
	document.getElementById('red-model-button').disabled = disable;
	document.getElementById('blue-model-button').disabled = disable;
	document.getElementById('generate-network-button').disabled = disable;
	document.getElementById('upload-network-button').disabled = disable;
}

// Function to reset the simulation
function restartButton() {
	if (simulationRunning) {
		alert('Please wait until the simulation finishes, or pause it before resetting');
	}

	if (network) {
		// Save the current positions of the nodes
		savedPositions = network.getPositions();
		savedEdges = network.body.data.edges.get();
		network.destroy();
		network = null;
	}

	// Reset stats
	updateStats({
		Red: 0,
		RedPercentage: 0,
		Blue: 0,
		BluePercentage: 0,
		Neutral: 0,
		NeutralPercentage: 0,
		Alienated: 0,
	});

	// Reset status
	updateStatus('Started');

	fetch('/restart_simulation')
	.then(response => response.json())
	.then(data => {
		if (data && data.graph) {
		  console.log('Reset network:', data.graph);
			initializeNetwork(data.graph);
			document.getElementById('influence').max = nodes.length;
			document.getElementById('influence').value = nodes.length;
			document.getElementById('energy').max = 70;
			document.getElementById('energy').value = 70;
		} else {
			console.error('Invalid data received:', data);
			alert('Error resetting network: Invalid data received');
		}
	})
	.catch(error => {
		console.error('Error resetting network:', error);
		alert('Error resetting network');
	});

	console.log('Simulation reset');
	console.log('Saved positions:', savedPositions, 'Alignments:', nodes.get({ fields: ['id', 'alignment'] }));
}

// Function to handle the selection of a new graph type. Shows and hides the specific graph type options.
function handleUpdatedGraphType() {
  const graphType = document.getElementById('graph-type').value;

  const er_probabilityDiv = document.getElementById('probability').parentElement;
  const ba_connectionDiv = document.getElementById('initial-connections').parentElement;
  const ws_neighbourDiv = document.getElementById('neighbour-connections').parentElement;
  const ws_rewireDiv = document.getElementById('rewire-probability').parentElement;
  
  if (graphType === "erdos_renyi") {
	er_probabilityDiv.style.display = "block";
	ba_connectionDiv.style.display = "none";
	ws_neighbourDiv.style.display = "none";
	ws_rewireDiv.style.display = "none";
  } else if (graphType === "barabasi_albert") {
	er_probabilityDiv.style.display = "none";
	ba_connectionDiv.style.display = "block";
	ws_neighbourDiv.style.display = "none";
	ws_rewireDiv.style.display = "none";
  } else if (graphType === "watts_strogatz") {
	er_probabilityDiv.style.display = "none";
	ba_connectionDiv.style.display = "none";
	ws_neighbourDiv.style.display = "block";
	ws_rewireDiv.style.display = "block";
  } else {
	  console.log("invalid graph type?");
  }
}

// Function to generate network
function generateNetwork() {
	network = null;
	const graph_type = document.getElementById("graph-type").value;
	const n = document.getElementById('number-of-nodes').value;
	const uncertainty = document.getElementById('uncertainty-spread').value;
	const er_probability = document.getElementById('probability').value;
	const ba_connections = document.getElementById('initial-connections').value;
	const ws_neighbours = document.getElementById('neighbour-connections').value;
	const ws_rewire_probability = document.getElementById('rewire-probability').value;
	
	document.getElementById('influence').max = n;
	document.getElementById('influence').value = n;
	document.getElementById('energy').max = 70;
	document.getElementById('energy').value = 70;

	//console.log(`Generating network type ${graph_type} with n=${n}, uncertainty=${uncertainty}, er_probability=${er_probability}`);
	toggleButtons(false);

	fetch('/generate_network', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			graph_type: graph_type,
			uncertainty: uncertainty,
			n: n,
			er_probability: er_probability,
			ba_connections: ba_connections,
			ws_neighbours: ws_neighbours,
			ws_rewire_probability: ws_rewire_probability
		})
	})
	.then(response => {
	  return response.text().then(text => {
		  console.log('Raw response:', text); // Log the raw response
		  try {
			  const data = JSON.parse(text);
			  return data;
		  } catch (error) {
			  console.error('Error parsing JSON:', error);
			  throw new Error('Invalid JSON response from server');
		  }
	  });
  })
	.then(data => {
		console.log('Network generation response:', data);
		if (data.status === 'success') {
			if (network) {
				network.destroy();
			}
			initializeNetwork(data.graph);
			updateStats(data.stats);
			updateStatus('Idle');
		} else {
			alert('Error generating network');
		}
	})
	.catch(error => {
		console.log('Error generating network:', error);
		alert('Error generating network');
	});
	
	networkGenerated = true;
}

// Function to upload network
function uploadNetwork() {
// TODO
}

// Initialize the network with initial data on page load
document.addEventListener('DOMContentLoaded', function() {
	// fetch('/initial_graph')
	//     .then(response => response.json())
	//     .then(data => {
	//         initializeNetwork(data.graph);
	//         updateStats(data.stats);
	//     })
	//     .catch(error => {
	//         console.error('Error fetching initial network:', error);
	//         updateStatus('Error');
	//     });
	document.getElementById('play-button').disabled = true;
	document.getElementById('next-turn-button').disabled = true;
});




// -----------------------------------------------------------------------------


// ? IS THIS FUNCTION STILL NEEDED ?
// function generateNetwork(){
//     // Get values from forms
//     let n = $("#number-of-nodes").val()
//     let p = $("#probability").val()

//     // Send AJAX request to generate the network
//     $.ajax({
//         url: "graph",
//         data: {'n': n, 
//                 'p': p},
//         success: function(result){
//             $("#graph-plot").html(result);
//         }
//     })
// }

function uploadNetwork() {
  // Create a file input element
  var inputElement = document.createElement('input');
  inputElement.type = 'file';
  inputElement.accept = '.txt, .csv'; // Only allow .txt and .csv files
  inputElement.onchange = function(event) {
	// Placeholder: handle the file upload here
	var file = event.target.files[0];
	if (file) {
	  alert('Selected file: ' + file.name);
	}
  };
  
  // Trigger the file input dialog
  inputElement.click();
}

// Function to validate custom topic word limit
function validateCustomTopic(team) {
  const inputField = document.getElementById(`${team}-custom-input`);
  const warningMessage = document.getElementById(`${team}-custom-warning`);
  const runButton = document.getElementById('run-button');

  // Get the number of words in the custom topic
  const wordCount = inputField.value.trim().split(/\s+/).filter(word => word.length > 0).length;

  // Check if the word count exceeds 12
  if (wordCount > 12) {
	warningMessage.style.display = 'block'; // Show the warning message
	runButton.disabled = true; // Disable the Run button
  } else {
	warningMessage.style.display = 'none'; // Hide the warning message
	runButton.disabled = false; // Enable the Run button if valid
  }
}

// Function to handle the selection of custom topics and show/hide custom input
function handleCustomTopic(team) {
  const topicSelect = document.getElementById(`${team}-topic-input`);
  const customInputDiv = document.getElementById(`${team}-custom-topic`);
  if (topicSelect.value === "Custom") {
	customInputDiv.style.display = "block"; // Show the custom input field
	document.getElementById('run-button').disabled = true; // Disable Run button until valid
  } else {
	customInputDiv.style.display = "none"; // Hide the custom input field
	document.getElementById('run-button').disabled = false; // Enable Run button
  }
}

async function validateMessageAgainstTopic(message, teamTopic) {
  const validationPrompt = `
	Validate the following message to see if it aligns with the given topic:
	
	Topic: "${teamTopic}"
	Message: "${message}"
	
	Respond with "True" if the message supports or aligns with the topic, and "False" if it contradicts or does not support the topic.
  `;

  try {
	const response = await fetch("/generate_message", {
	  method: "POST",
	  headers: { "Content-Type": "application/json" },
	  body: JSON.stringify({
		model_name: "gemini-1.0-pro", // Use a default model for validation
		prompt: validationPrompt,
	  }),
	});
	console.log("Validation response:", response);
	console.log("Request:", validationPrompt);
	const result = await response.json();
	const validationResult = result.message.trim().toLowerCase();

	return validationResult === "true"; // AI response should be "True" or "False"
  } catch (error) {
	console.error(`Error occurred while validating message: ${error}`);
	return false; // Return false in case of an error
  }
}
