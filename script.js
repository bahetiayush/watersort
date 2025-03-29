const serverBase = 'http://localhost:8000';
import { ImageUploadModal } from './image-upload-modal.js';
export { sendImageAndAnalyze }

let imageUploadModal = null;
let gameState = null;
let isSolving = false;
let movesAfterSolvePuzzle = 0;
let current_gameState = { tubes: [] };

function getInitialState() {
    fetch(serverBase + '/api/initial_state')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            current_gameState = createGameState(data.tubes);
            updateTubes(current_gameState);
            renderButtons();
            getTopMoves();
        })
        .catch(handleError);
}

async function sendImage() {
    if (!imageUploadModal) {
        imageUploadModal = new ImageUploadModal();
    }
    imageUploadModal.show();
}

async function sendImageAndAnalyze(file) {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('image_type', file.type);

    try {
        const response = await fetch(serverBase + '/api/analyze_tubes', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.error || response.statusText}`);
        }

        const data = await response.json();
        if (data.status === "success") {
            current_gameState = createGameState(data.tubes);
            updateTubes(current_gameState);
            getTopMoves();
            console.log("Game state updated successfully after image analysis!");
        } else {
            console.error('Error updating game state after analysis:', data.error);
            handleError(data.error);
        }
    } catch (error) {
        console.error('Error during image analysis:', error);
        handleError(error.message);
}
}

function createGameState(tubes) {
    return { tubes: tubes };
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
        const match = selectedMoveLabel.textContent.match(/(\w+) to (\w+)/);

        if (match) {
            const fromTube = match[1];
            const toTube = match[2];

            // Now, use the API to apply the move
            applyMoveBackend(fromTube, toTube);
        }
    } else {
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
            current_gameState = createGameState(data.tubes);
            updateTubes(current_gameState);
            getTopMoves();
        }).catch(handleError);
}

function updateTubes(current_gamestate) {
    const tubesContainer = document.getElementById('tubes-container');
    tubesContainer.innerHTML = '';

    current_gamestate.tubes.forEach(tubeData => {
        const tubeWrapper = document.createElement('div');
        tubeWrapper.className = 'tube-wrapper';
        const tubeDiv = document.createElement('div');
        tubeDiv.className = 'tube';
        tubeWrapper.appendChild(tubeDiv);

        tubeData.colors.forEach(color => {
            const slotDiv = document.createElement('div');
            slotDiv.className = `slot ${color || 'NONE'}`;
            tubeDiv.prepend(slotDiv);
        })

        const tubeNameDiv = document.createElement('div');
        tubeNameDiv.className = 'tube-name';
        tubeNameDiv.textContent = tubeData.name;
        tubeWrapper.appendChild(tubeNameDiv);
        ;

        tubesContainer.appendChild(tubeWrapper);
    })

    gameState = current_gamestate;
}

function renderButtons() {
    const buttonsContainer = document.getElementById('buttons-container');
    buttonsContainer.innerHTML = ''; // Clear existing buttons

    const sendImageButton = createButton('Send Image', sendImage);
    const undoButton = createButton('Undo', sendUndoRequest);
    const runIterationButton = createButton('Run 1 Iteration', applySelectedMove);
    const solvePuzzleButton = createButton('Solve Puzzle', toggleSolvePuzzle);
    solvePuzzleButton.id = 'solve-puzzle-button';

    buttonsContainer.append(sendImageButton, undoButton, runIterationButton, solvePuzzleButton);
}

function updateMoves(top_moves) {
    const topMovesContainer = document.getElementById('top-moves-container');
    topMovesContainer.innerHTML = '';

    const topMovesHeading = document.createElement('h3');
    topMovesHeading.id = 'top-moves-heading';
    topMovesContainer.appendChild(topMovesHeading);

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
            label.textContent = `${fromTubeName} to ${toTubeName} (Score: ${score})`;

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

function showGameCompletedMessage(finalMoveList) {
    const topMovesHeading = document.getElementById('top-moves-heading');
    const movesList = document.getElementById('moves-list');
    const totalMovesNeeded = document.createElement('div');
    totalMovesNeeded.id = 'total-moves-needed';

    topMovesHeading.textContent = `Game Completed!`;

    movesList.innerHTML = '';
    const moveListHtml = finalMoveList.map(move => `<li>${move.from} to ${move.to}</li>`).join('');
    movesList.innerHTML = `<ul>${moveListHtml}</ul>`;

    totalMovesNeeded.textContent = `Total moves: ${finalMoveList.length}${movesAfterSolvePuzzle > 0 ? `\nMoves after "Solve puzzle": ${movesAfterSolvePuzzle}` : ''}`;
    const buttonsContainer = document.getElementById('buttons-container');
    buttonsContainer.insertAdjacentElement('afterend', totalMovesNeeded);
    renderButtons();
}

function handleError(error) {
    console.error('Error:', error);
}

function createButton(text, onClick) {
    const button = document.createElement('button');
    button.textContent = text;
    button.addEventListener('click', onClick);
    return button;
}

function toggleSolvePuzzle() {
    const solvePuzzleButton = document.getElementById('solve-puzzle-button');
    if (!isSolving) {
        solvePuzzleButton.textContent = 'Solving...';
        solvePuzzleButton.style.backgroundColor = 'grey';
        solvePuzzle();
    } else {
        stopSolve();
    }
}

function solvePuzzle() {
    const solvePuzzleButton = document.getElementById('solve-puzzle-button');
    isSolving = true;
    solvePuzzleButton.disabled = true;


    fetch('/api/solve_puzzle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
    })
        .then(response => response.json())
        .then(data => {
            solvePuzzleButton.disabled = false;
            if (data.status === "success") {
                const solutionMoves = data.solution;
                console.log("Solution moves:", solutionMoves);
                solvePuzzleButton.textContent = 'Stop Solving';
                solvePuzzleButton.style.backgroundColor = 'red';
                applyManyMoves(solutionMoves);
            } else if (data.status === "failure") {
                console.log("No solution found.");
                resetSolveButton();
            } else {
                console.error("Error:", data.message);
                resetSolveButton();
            }
        })
        .catch(error => {
            console.error("Error during API call:", error);
            resetSolveButton();
        });
}

function stopSolve() {
    isSolving = false;
    resetSolveButton();
    getTopMoves();
}

function resetSolveButton() {
    isSolving = false;
    const solvePuzzleButton = document.getElementById('solve-puzzle-button');
    solvePuzzleButton.textContent = 'Solve Puzzle';
    solvePuzzleButton.style.backgroundColor = '';
    solvePuzzleButton.disabled = false;
}

function applyManyMoves(solutionMoves) {
    if (!solutionMoves || !Array.isArray(solutionMoves)) {
        console.error("Invalid solution data received.");
        return;
    }
    let index = 0;
    let movesMade = 0; // counter for number of moves made

    function applyNextMove() {
        if (!isSolving) return;

        if (index < solutionMoves.length) {
            const move = solutionMoves[index];
            applyMoveBackend(move.from, move.to, () => {
                movesMade++;
                setTimeout(applyNextMove, 500);
            });
            index++;
        }
    }
    applyNextMove();
}

function applyMoveBackend(fromTube, toTube, callback) {
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
            current_gameState = createGameState(data.tubes);
            updateTubes(current_gameState);
            if (data.game_completed) {
                showGameCompletedMessage(data.final_move_list);
            }
            else if (data.status === 'success' && !isSolving) {
                getTopMoves();
            }
            
            if (data.status === 'error') {
                console.error('Error applying move:', data.message);
                handleError(data.message);
            }
            if(callback){
                callback();
              }
        })
        .catch(handleError);
}

getInitialState()
