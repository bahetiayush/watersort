const serverBase = 'http://localhost:8000';
import { ImageUploadModal } from './image-upload-modal.js';
export { sendImageAndAnalyze }

let imageUploadModal = null;
let gameState = null;
let isSolving = false;
let movesAfterSolvePuzzle = 0;
let current_gameState = { tubes: [] };
let isEditingColors = false;
let selectedSlots = [];
let originalGameState = null;
let tempGameState = null;
let solutionMoves = null;
let isExecutingSolution = false;
let solveFromCurrentState = false;

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
            // Store the original game state before making changes
            originalGameState = JSON.parse(JSON.stringify(current_gameState));
            
            // Update the temporary game state with the analyzed colors
            tempGameState = createGameState(data.tubes);
            
            // Update the UI with the analyzed colors
            updateTubes(tempGameState);
            
            // Enter color editing mode
            enterColorEditMode();
            
            console.log("Image analyzed successfully! You can now edit the colors.");
        } else {
            console.error('Error updating game state after analysis:', data.error);
            handleError(data.error);
        }
    } catch (error) {
        console.error('Error during image analysis:', error);
        handleError(error.message);
    }
}

function enterColorEditMode() {
    isEditingColors = true;
    selectedSlots = [];
    
    // Hide regular buttons
    const buttonsContainer = document.getElementById('buttons-container');
    buttonsContainer.innerHTML = '';
    
    // Create edit mode buttons
    const acceptButton = createButton('Accept new colours', acceptNewColors);
    const rejectButton = createButton('Reject completely', rejectChanges);
    rejectButton.style.backgroundColor = 'red';
    
    buttonsContainer.append(rejectButton, acceptButton);
    
    // Update the top moves heading
    const topMovesHeading = document.getElementById('top-moves-heading');
    if (topMovesHeading) {
        topMovesHeading.textContent = 'Swap the colours';
    }
    
    // Clear the moves list
    const movesList = document.getElementById('moves-list');
    if (movesList) {
        movesList.innerHTML = '';
    }
    
    // Add click event listeners to slots
    addSlotClickListeners();
}

function exitColorEditMode() {
    isEditingColors = false;
    selectedSlots = [];
    
    // Restore regular buttons
    renderButtons();
    
    // Update the top moves
    getTopMoves();
}

function addSlotClickListeners() {
    const tubes = document.querySelectorAll('.tube');
    tubes.forEach((tube, tubeIndex) => {
        const slots = tube.querySelectorAll('.slot');
        // Note: slots are in reverse order in the DOM (top to bottom)
        slots.forEach((slot, slotPosition) => {
            slot.style.cursor = 'pointer';
            // Store the tube index and position directly on the element
            slot.dataset.tubeIndex = tubeIndex;
            // Convert from visual position to data position (accounting for reversal)
            slot.dataset.position = 3 - slotPosition; // Assuming 4 slots per tube
            slot.addEventListener('click', () => handleSlotSelection(slot));
        });
    });
}

function handleSlotSelection(slot) {
    if (!isEditingColors) return;
    
    // Toggle selection class
    slot.classList.toggle('selected');
    
    // Add or remove from selected slots
    if (slot.classList.contains('selected')) {
        selectedSlots.push({
            element: slot,
            tubeIndex: parseInt(slot.dataset.tubeIndex),
            position: parseInt(slot.dataset.position)
        });
    } else {
        selectedSlots = selectedSlots.filter(s => s.element !== slot);
    }
    
    // If we have 2 selected slots, swap their colors
    if (selectedSlots.length === 2) {
        swapColors(selectedSlots[0], selectedSlots[1]);
        
        // Clear selections after swapping
        selectedSlots.forEach(s => s.element.classList.remove('selected'));
        selectedSlots = [];
    }
}

function swapColors(slot1, slot2) {
    // Get the tube and position information directly from the stored data
    const tube1Index = slot1.tubeIndex;
    const position1 = slot1.position;
    const tube2Index = slot2.tubeIndex;
    const position2 = slot2.position;
    
    console.log(`Swapping colors: Tube ${tube1Index} Position ${position1} with Tube ${tube2Index} Position ${position2}`);
    
    // Get the colors
    const color1 = tempGameState.tubes[tube1Index].colors[position1];
    const color2 = tempGameState.tubes[tube2Index].colors[position2];
    
    console.log(`Colors before swap: ${color1} and ${color2}`);
    
    // Swap the colors
    tempGameState.tubes[tube1Index].colors[position1] = color2;
    tempGameState.tubes[tube2Index].colors[position2] = color1;
    
    console.log(`Colors after swap: ${tempGameState.tubes[tube1Index].colors[position1]} and ${tempGameState.tubes[tube2Index].colors[position2]}`);
    
    // Update the UI
    updateTubes(tempGameState);
    
    // Re-add click listeners since we've updated the DOM
    addSlotClickListeners();
}

function acceptNewColors() {
    // Send the updated colors to the backend
    fetch(serverBase + '/api/update_tubes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            tubes: tempGameState.tubes
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            // Update the current game state
            current_gameState = createGameState(data.tubes);
            updateTubes(current_gameState);
            
            // Exit edit mode
            exitColorEditMode();
            
            console.log("Colors updated successfully!");
        } else {
            console.error('Error updating colors:', data.message);
            handleError(data.message);
        }
    })
    .catch(handleError);
}

function rejectChanges() {
    // Revert to the original state
    updateTubes(originalGameState);
    
    // Exit edit mode
    exitColorEditMode();
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
    
    console.log("Toggle state:", { isSolving, isExecutingSolution });
    
    if (!isSolving && !isExecutingSolution) {
        // Initial state - start solving (just get solution, don't execute)
        console.log("Starting solve - getting solution only");
        solvePuzzleButton.textContent = 'Solving...';
        solvePuzzleButton.style.backgroundColor = 'grey';
        solvePuzzle();
    } else if (isSolving && !isExecutingSolution) {
        // Solution found but not executing - start executing
        console.log("Starting execution of solution");
        startExecutingSolution();
    } else if (isExecutingSolution) {
        // Currently executing solution - stop execution
        console.log("Stopping execution");
        stopExecutingSolution();
    }
}

function solvePuzzle() {
    console.log("solvePuzzle called, state before:", { isSolving, isExecutingSolution, solveFromCurrentState });
    
    const solvePuzzleButton = document.getElementById('solve-puzzle-button');
    
    // Set state flags - we're solving but not executing
    isSolving = true;
    isExecutingSolution = false;
    solvePuzzleButton.disabled = true;

    // Prepare payload based on whether we're solving from current state
    const payload = solveFromCurrentState ? 
        { current_state: current_gameState.tubes } : {};
    
    console.log("Solving with payload:", payload);
    
    // Reset the flag after use
    solveFromCurrentState = false;

    fetch(serverBase + '/api/solve_puzzle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(data => {
            solvePuzzleButton.disabled = false;
            
            if (data.status === "success") {
                // Store the solution moves
                solutionMoves = data.solution;
                console.log("Solution received:", solutionMoves);
                
                // Display the solution on screen (but don't execute)
                displaySolution(solutionMoves);
                
                // If there are no moves needed (already solved)
                if (solutionMoves.length === 0) {
                    console.log("Puzzle already solved (0 moves)");
                    // Reset the button to normal state
                    resetSolveButton();
                } else {
                    // Change button to "Complete the moves"
                    solvePuzzleButton.textContent = 'Complete the moves';
                    solvePuzzleButton.style.backgroundColor = '#4CAF50'; // Green
                    console.log("Solution displayed, button changed to 'Complete the moves'");
                }
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

function displaySolution(moves) {
    const topMovesContainer = document.getElementById('top-moves-container');
    topMovesContainer.innerHTML = '';

    const topMovesHeading = document.createElement('h3');
    topMovesHeading.id = 'top-moves-heading';
    topMovesContainer.appendChild(topMovesHeading);

    const movesContainer = document.createElement('div');
    movesContainer.id = 'moves-list';
    topMovesContainer.appendChild(movesContainer);

    if (moves && moves.length > 0) {
        topMovesHeading.textContent = 'Solution';
        const moveListHtml = moves.map((move, index) => 
            `<div>${index + 1}. ${move.from} to ${move.to}</div>`
        ).join('');
        movesContainer.innerHTML = moveListHtml;
    } else if (moves && moves.length === 0) {
        // Handle already solved case
        topMovesHeading.textContent = 'Puzzle Already Solved';
        movesContainer.innerHTML = '<div style="font-weight: bold; margin-top: 10px;">0 moves needed - puzzle is already solved</div>';
    } else {
        topMovesHeading.textContent = 'Solution';
        movesContainer.innerHTML = '<div>No solution available</div>';
    }
}

function startExecutingSolution() {
    console.log("startExecutingSolution called, state before:", { isSolving, isExecutingSolution });
    
    if (!solutionMoves || !Array.isArray(solutionMoves)) {
        console.error("No valid solution to execute.");
        return;
    }
    
    // Update state flags - we're now executing the solution
    isExecutingSolution = true;
    
    // Change button to "Stop moves"
    const solvePuzzleButton = document.getElementById('solve-puzzle-button');
    solvePuzzleButton.textContent = 'Stop moves';
    solvePuzzleButton.style.backgroundColor = 'red';
    
    console.log("Starting execution of solution moves");
    
    // Start executing the moves
    executeSolutionMoves();
}

function stopExecutingSolution() {
    console.log("stopExecutingSolution called, state before:", { isSolving, isExecutingSolution });
    
    // Update state flags
    isExecutingSolution = false;
    
    // Get top moves for current state
    getTopMoves();
    
    // Set flag to solve from current state on next solve
    solveFromCurrentState = true;
    
    // Reset the button
    const solvePuzzleButton = document.getElementById('solve-puzzle-button');
    solvePuzzleButton.textContent = 'Solve Puzzle';
    solvePuzzleButton.style.backgroundColor = '';
    
    console.log("Execution stopped, state after:", { isSolving, isExecutingSolution, solveFromCurrentState });
}

function stopSolve() {
    isSolving = false;
    isExecutingSolution = false;
    resetSolveButton();
    getTopMoves();
}

function resetSolveButton() {
    console.log("resetSolveButton called, state before:", { isSolving, isExecutingSolution, solveFromCurrentState });
    
    // Reset all state flags
    isSolving = false;
    isExecutingSolution = false;
    solutionMoves = null;
    
    // Reset the button appearance
    const solvePuzzleButton = document.getElementById('solve-puzzle-button');
    solvePuzzleButton.textContent = 'Solve Puzzle';
    solvePuzzleButton.style.backgroundColor = '';
    solvePuzzleButton.disabled = false;
    
    console.log("Button reset, state after:", { isSolving, isExecutingSolution });
}

function executeSolutionMoves() {
    console.log("executeSolutionMoves called, state:", { isSolving, isExecutingSolution });
    
    if (!solutionMoves || !Array.isArray(solutionMoves)) {
        console.error("No valid solution moves to execute");
        return;
    }
    
    if (!isExecutingSolution) {
        console.error("Not in execution mode");
        return;
    }
    
    console.log(`Starting execution of ${solutionMoves.length} solution moves`);
    
    let index = 0;
    let movesMade = 0;
    
    function executeNextMove() {
        // Check if we should stop execution
        if (!isExecutingSolution) {
            console.log("Execution stopped mid-way");
            return;
        }
        
        if (index < solutionMoves.length) {
            const move = solutionMoves[index];
            console.log(`Executing move ${index + 1}/${solutionMoves.length}: ${move.from} to ${move.to}`);
            
            // Highlight the current move in the solution list
            const movesList = document.getElementById('moves-list');
            const moveElements = movesList.children;
            if (index > 0 && moveElements[index-1]) {
                moveElements[index-1].style.fontWeight = 'normal';
            }
            if (moveElements[index]) {
                moveElements[index].style.fontWeight = 'bold';
            }
            
            applyMoveBackend(move.from, move.to, () => {
                movesMade++;
                movesAfterSolvePuzzle = movesMade;
                setTimeout(executeNextMove, 500);
            });
            index++;
        } else {
            // All moves completed
            console.log("All solution moves completed");
            isExecutingSolution = false;
            isSolving = false; // Reset solving flag too
            
            const solvePuzzleButton = document.getElementById('solve-puzzle-button');
            solvePuzzleButton.textContent = 'Solve Puzzle';
            solvePuzzleButton.style.backgroundColor = '';
        }
    }
    
    // Start the execution
    executeNextMove();
}

// This function is no longer used - we use executeSolutionMoves instead
// Keeping it commented out for reference
/*
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
*/

function applyMoveBackend(fromTube, toTube, callback) {
    console.log(`applyMoveBackend: ${fromTube} to ${toTube}, state:`, { isSolving, isExecutingSolution });
    
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
            // Update game state with the new tubes
            current_gameState = createGameState(data.tubes);
            updateTubes(current_gameState);
            
            if (data.game_completed) {
                console.log("Game completed!");
                showGameCompletedMessage(data.final_move_list);
                
                // Reset state flags
                isSolving = false;
                isExecutingSolution = false;
            }
            else if (data.status === 'success') {
                // Only get top moves if we're not in the middle of executing a solution
                if (!isExecutingSolution && !isSolving) {
                    console.log("Getting top moves after move");
                    getTopMoves();
                }
            }
            
            if (data.status === 'error') {
                console.error('Error applying move:', data.message);
                handleError(data.message);
            }
            
            // Call the callback if provided
            if (callback) {
                callback();
            }
        })
        .catch(handleError);
}

getInitialState()
