const serverBase = 'http://localhost:8000'; // Correct server path

function applySelectedMove() {
    var selectedMoveIndexElement = document.querySelector('input[name="selected_move"]:checked');

    if (selectedMoveIndexElement) {
        var selectedMoveIndex = selectedMoveIndexElement.value;
        return fetch(serverBase + '/api/apply_move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ move_index: selectedMoveIndex }),
        })
        .then(response => {
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }
          return response.json();
        })
        .then(data => {
            updateTubes(data.tubes); // Update the tubes in every response.
            if (data.game_completed) {
                showGameCompletedMessage();
                return;
            }
            if (data.status === 'success') {
                getTopMoves();
            } else if (data.status === 'dead_end') {
                showDeadEndMessage(); // show the message
                sendDeadEndState(data.tubes); //send the state to be added to dead_ends.
                setTimeout(() => { // Wait 1.5 seconds
                    sendUndoRequest(); // call the undo request
                    getTopMoves();
                }, 1500);
            } else if (data.status === "error"){
                console.error('Error applying move:', data.message);
                showErrorMessage(data.message);
                getTopMoves();
            }else if (data.status === "game_completed"){
                showGameCompletedMessage(); // show the game completed message.
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    } else {
        console.error('No move selected.');
    }
}

function updateTubes(tubes) {
    var tubesContainer = document.getElementById('tubes-container');
    tubesContainer.innerHTML = ''; // Clear existing tubes

    for (const tubeData of tubes) {
        var tubeWrapper = document.createElement('div');
        tubeWrapper.className = 'tube-wrapper';
        var tubeDiv = document.createElement('div');
        tubeDiv.className = 'tube';
        for (const color of tubeData.colors.slice().reverse()) { // Reverse to add bottom-up
            var slotDiv = document.createElement('div');
            slotDiv.className = 'slot ' + (color ? color : 'NONE');
            tubeDiv.appendChild(slotDiv);
        }
        tubeWrapper.appendChild(tubeDiv);
        var tubeNameDiv = document.createElement('div');
        tubeNameDiv.className = 'tube-name';
        tubeNameDiv.textContent = tubeData.name;
        tubeWrapper.appendChild(tubeNameDiv);
        tubesContainer.appendChild(tubeWrapper);
    }
}

function updateMoves(top_moves) {
    var topMovesContainer = document.getElementById('top-moves-container');
    topMovesContainer.innerHTML = '<h2>Top 5 Possible Moves</h2><form id="move-form"></form>';
    var form = document.getElementById('move-form');
    if (top_moves) {
        for (let i = 0; i < top_moves.length; i++) {
            const moveData = top_moves[i];
            const move = moveData.movement;
            const score = moveData.score;
            let fromTubeName, toTubeName;
            
            if (move.length === 0) { // Handle the no-move case
                continue
            } else {
                fromTubeName = move[0].name;
                toTubeName = move[1].name;
            }
            const checked = (i === 0 && top_moves.length > 0)? "checked" : ""; // Check the first move by default
            const moveOptionDiv = document.createElement('div');
            moveOptionDiv.className = 'move-option';
            moveOptionDiv.innerHTML = `
                <input type="radio" id="move-${i}" name="selected_move" value="${i}" ${checked}>
                <label for="move-${i}">Move from ${fromTubeName} to ${toTubeName} (Score: ${score})</label>
            `;
            form.appendChild(moveOptionDiv);
        }
        form.innerHTML += '<button type="button" onclick="applySelectedMove()">Run 1 Iteration</button>';
        if(form.innerHTML == '<button type="button" onclick="applySelectedMove()">Run 1 Iteration</button>')
          topMovesContainer.innerHTML += '<p>No moves possible.</p>'
    } else {
        topMovesContainer.innerHTML += '<p>No moves possible.</p>'
    }
}

function getTopMoves(){
    fetch(serverBase + '/api/top_moves', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
      })
    .then(data => {
        updateMoves(data.top_moves);
        updateTubes(data.state);
        if (!data.top_moves || data.top_moves.length == 0){
            showDeadEndMessage();
            sendDeadEndState(data.state); // data state is the complete list of tubes.
            setTimeout(() => {
                sendUndoRequest();
                getTopMoves();
            }, 1500);
        }

    })
    .catch((error) => {
        console.error('Error:', error);
    });

}

function getInitialState(){
    fetch(serverBase + '/api/initial_state', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
      })
    .then(data => {
        updateTubes(data.tubes);
        getTopMoves(); // Make sure to load the top moves
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function sendDeadEndState(tubes) {
    fetch(serverBase + '/api/add_dead_end', {
        method: 'POST',
        body: JSON.stringify({ state: tubes}), //send the complete tubes, not just the colors.
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        // Handle success (optional)
    })
    .catch(error => {
        console.error("Error sending dead end state:", error);
    });
}

function sendUndoRequest() {
    fetch(serverBase + '/api/undo_move')
    .then(response => response.json())
    .then(data => {
        // Update the UI with the new state
        updateTubes(data.tubes);
        updateMoves(data.top_moves); // correct function call
    })
    .catch(error => {
        console.error("Error during undo:", error);
    });
}

// Function to show error message
function showErrorMessage(message){
    // add code to display the error message
    console.log("Showing error message")
    console.log(message)
}
  
function showDeadEndMessage() {
    var deadEndMessageContainer = document.getElementById('dead-end-message-container');
    deadEndMessageContainer.innerHTML = '<p>Dead End Reached, going back...</p>';
    // Optionally clear the message after a delay
    setTimeout(() => {
        deadEndMessageContainer.innerHTML = ''; // remove the message after 1.5 seconds.
    }, 1500);
}

function showGameCompletedMessage() {
    var gameCompletedMessageContainer = document.getElementById('top-moves-container');
    gameCompletedMessageContainer.innerHTML = '<h2>Game Completed!</h2>';
}
getInitialState()

// undo button code below

document.getElementById('undo-button').addEventListener('click', sendUndoRequest); // call directly to the function.
