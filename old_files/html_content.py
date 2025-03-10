HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Water Sort Visualization</title>
    <style>
    {{CSS_PLACEHOLDER}}
    </style>
</head>
<body>
    <h1>Water Sort Visualization</h1>
    <div id="tubes-container" class="tubes-container">
        {{TUBES_PLACEHOLDER}}
    </div>
    <div id="top-moves-container">
        <h2>Top 5 Possible Moves</h2>
        <form id="move-form">
            {{MOVES_PLACEHOLDER}}
        </form>
    </div>
    <script src={{JS_PLACEHOLDER}}></script>
    <script>
        // Add an event listener to the form to prevent it from submitting normally
        document.getElementById('move-form').addEventListener('submit', function(event) {
            event.preventDefault();
        });
    </script>
</body>
</html>
"""

CSS_STYLE = """
body {
    font-family: sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.tubes-container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    width: 80%;
}
.tube-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 10px;
}
.tube {
    width: 80px;
    height: 200px;
    border: 2px solid black;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
}
.slot {
    width: 100%;
    height: 25%;
    border-top: 1px solid black;
}
.BROWN { background-color: brown; }
.LIGHT_GREEN { background-color: lightgreen; }
.BLUE { background-color: blue; }
.GREY { background-color: grey; }
.GREEN { background-color: green; }
.RED { background-color: red; }
.PINK { background-color: pink; }
.MEHENDI { background-color: #8A2BE2; } /* Violet-like */
.LIGHT_BLUE { background-color: lightblue; }
.ORANGE { background-color: orange; }
.PURPLE { background-color: purple; }
.YELLOW { background-color: yellow; }
.NONE { background-color: transparent;}
.tube-name {
    text-align: center;
    margin-top: 5px;
    font-weight: bold;
}
#top-moves-container {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.move-option {
    margin-bottom: 10px;
}
"""
