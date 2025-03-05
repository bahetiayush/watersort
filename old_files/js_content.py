JS_CONTENT = """
    function applySelectedMove() {
        var selectedMoveIndexElement = document.querySelector('input[name="selected_move"]:checked');
        
        if (selectedMoveIndexElement) {
            var selectedMoveIndex = selectedMoveIndexElement.value;
            fetch('/apply_move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ move_index: selectedMoveIndex }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateTubes(data.tubes, data.top_moves);
                } else {
                   console.error('Error applying move:', data.message);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        } else {
            console.error('No move selected.');
        }
    }

    function updateTubes(tubes, top_moves) {
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
        // Clear existing top moves
        var topMovesContainer = document.getElementById('top-moves-container');
        topMovesContainer.innerHTML = '<h2>Top 5 Possible Moves</h2><form id="move-form"></form>'; 
        if (top_moves) {
            var form = document.getElementById('move-form');
          for (let i = 0; i < top_moves.length; i++) {
            const moveData = top_moves[i];
            const move = moveData.movement;
            const score = moveData.score;
            const fromTubeName = move[0].name;
            const toTubeName = move[1].name;
            const checked = i === 0 ? "checked" : ""; // Check the first move by default
            const moveOptionDiv = document.createElement('div');
            moveOptionDiv.className = 'move-option';
            moveOptionDiv.innerHTML = `
                <input type="radio" id="move-\" name="selected_move" value="\" \>
                <label for="move-\">Move from \ to \ (Score: \)</label>
            `;
            form.appendChild(moveOptionDiv);
          }
        form.innerHTML += '<button type="button" onclick="applySelectedMove()">Run 1 Iteration</button>';
        } else {
            topMovesContainer.innerHTML += '<p>No moves possible.</p>'
        }
    }
"""
