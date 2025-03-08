const serverBase = 'http://localhost:8000';

function getInitialState() {
    fetch(serverBase + '/api/initial_state')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateTubes(data.tubes);
            getTopMoves();
        })
        .catch(handleError);
}

function getTopMoves() {
    fetch(serverBase + '/api/top_moves')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateMoves(data.top_moves);
            if (!data.top_moves || data.top_moves.length === 0) {
                setTimeout(sendUndoRequest, 500);
            }
        })
        .catch(handleError);
}

function applySelectedMove() {
    const selectedMoveIndexElement = document.querySelector('input[name="selected_move"]:checked');

    if (selectedMoveIndexElement) {
        const selectedMoveIndex = selectedMoveIndexElement.value;
        const selectedMoveLabel = selectedMoveIndexElement.nextElementSibling; // Get the label element

        // Extract from_tube and to_tube from the label text using a regular expression
        const match = selectedMoveLabel.textContent.match(/Move from (\w+) to (\w+)/); 

        if (match) {
            const fromTube = match[1];
            const toTube = match[2];

            fetch(serverBase + '/api/apply_move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    from_tube: fromTube, 
                    to_tube: toTube 
                }),
            })
            .then(response => response.json())
            .then(data => {
                updateTubes(data.tubes);
                if (data.game_completed) {
                    showGameCompletedMessage(data.final_move_list);
                    return;
                }
                if (data.status === 'success') {
                    getTopMoves();
                } else if (data.status === 'error') {
                    console.error('Error applying move:', data.message);
                    showErrorMessage(data.message);
                    getTopMoves();
                }
            })
            .catch(handleError);
    }} else {
        console.error('No move selected.');
    }
}

function sendUndoRequest() {
    fetch(serverBase + '/api/undo_move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateTubes(data.tubes);
            getTopMoves();}
        ).catch(handleError);
}

function updateTubes(tubes) {
    const tubesContainer = document.getElementById('tubes-container');
    tubesContainer.innerHTML = '';

    tubes.forEach(tubeData => {
        const tubeWrapper = document.createElement('div');
        tubeWrapper.className = 'tube-wrapper';
        const tubeDiv = document.createElement('div');
        tubeDiv.className = 'tube';
        tubeWrapper.appendChild(tubeDiv);

        tubeData.colors.forEach(color => {
            const slotDiv = document.createElement('div');
            slotDiv.className = `slot ${color || 'NONE'}`;
            tubeDiv.appendChild(slotDiv);
        })
        
        const tubeNameDiv = document.createElement('div');
        tubeNameDiv.className = 'tube-name';
        tubeNameDiv.textContent = tubeData.name;
        tubeWrapper.appendChild(tubeNameDiv);
        ;
        
        tubesContainer.appendChild(tubeWrapper);
    });
}

function updateMoves(top_moves) {
    const topMovesContainer = document.getElementById('top-moves-container');
    topMovesContainer.innerHTML = '';

    const topMovesHeading = document.createElement('h3');
    topMovesHeading.id = 'top-moves-heading';
    topMovesContainer.appendChild(topMovesHeading);

    const buttonsContainer = document.createElement('div');
    buttonsContainer.id = 'top-moves-buttons-container';

    const undoButton = createButton('Undo', sendUndoRequest);
    const runIterationButton = createButton('Run 1 Iteration', applySelectedMove);
    const solvePuzzleButton = createButton('Solve Puzzle', () => { });
    solvePuzzleButton.disabled = true;

    buttonsContainer.append(undoButton, runIterationButton, solvePuzzleButton);
    topMovesContainer.appendChild(buttonsContainer);

    const movesContainer = document.createElement('div');
    movesContainer.id = 'moves-list';
    topMovesContainer.appendChild(movesContainer);

    if (top_moves && top_moves.length > 0) {
        topMovesHeading.textContent = `Top ${top_moves.length} possible moves`;
        top_moves.forEach((moveData, index) => {
            const move = moveData.movement;
            const score = moveData.score;

            const fromTubeName = move[0].name;
            const toTubeName = move[1].name;

            const radioInput = document.createElement('input');
            radioInput.type = 'radio';
            radioInput.id = `move-${index}`;
            radioInput.name = 'selected_move';
            radioInput.value = index;
            radioInput.checked = index === 0;

            const label = document.createElement('label');
            label.htmlFor = `move-${index}`;
            label.textContent = `Move from ${fromTubeName} to ${toTubeName} (Score: ${score})`;

            const moveItem = document.createElement('div');
            moveItem.style.marginBottom = "5px";
            moveItem.appendChild(radioInput);
            moveItem.appendChild(label);
            movesContainer.appendChild(moveItem);

        });
    } else {
        topMovesHeading.textContent = 'Dead end reached';
    }
}

function showGameCompletedMessage(moveList) {
    const topMovesHeading = document.getElementById('top-moves-heading');
    const movesList = document.getElementById('moves-list');

    topMovesHeading.textContent = `Game Completed!`;

    movesList.innerHTML = ''; 
    const moveListHtml = moveList.map(move => `<li>${move.from} -> ${move.to}</li>`).join('');
    movesList.innerHTML = `<ul>${moveListHtml}</ul>`;

    const totalMovesNeeded = document.createElement('div');
    totalMovesNeeded.id = 'total-moves-needed';
    totalMovesNeeded.textContent = `Total moves needed: ${moveList.length} moves`;
    //Add after button container
    const buttonsContainer = document.getElementById('top-moves-buttons-container');
    buttonsContainer.insertAdjacentElement('afterend', totalMovesNeeded);
}

function showErrorMessage(message) {
    console.error('Error:', message);
}

function handleError(error) {
    console.error('Error:', error);
}

function createButton(text, onClick) {
    const button = document.createElement('button');
    button.textContent = text;
    button.addEventListener('click', onClick);
    return button;x
}

function sendDeadEndState(tubes) {
    fetch(serverBase + '/api/add_dead_end', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: tubes }),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => { })
        .catch(handleError);
}

getInitialState();
