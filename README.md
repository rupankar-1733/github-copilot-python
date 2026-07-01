# Sudoku Game (Python + Flask)

A Sudoku web game refactored from legacy code into a modern, tested Flask
application, built with the help of GitHub Copilot. The generator guarantees a
unique solution, and the game supports difficulty levels, a timer, hints,
real-time input checking, and a persistent Top 10 leaderboard.

## Features

- **Unique-solution generator** — every puzzle is verified to have exactly one solution.
- **Difficulty levels** — Easy, Medium, and Hard change how many cells are prefilled.
- **Hint button** — fills one correct empty cell and locks it.
- **Check button** — highlights incorrect entries against the solution.
- **Live conflict feedback** — duplicate numbers in a row, column, or box are flagged as you type.
- **Timer** — tracks how long the puzzle takes to solve.
- **Completion message** — shows time taken and hints used, and prompts for a name.
- **Top 10 leaderboard** — saves name, time, difficulty, and hints in `localStorage` so scores persist across refreshes.
- **Dark mode toggle.**

## Getting Started

### Dependencies

- Python 3
- A modern web browser (Chrome, Firefox, Edge, etc.)

### Installation

1. Clone this repository to your local machine.
2. Open a terminal and navigate to the `starter` directory.
3. Create and activate a virtual environment (recommended):

   ```bash
   # macOS / Linux
   python3 -m venv .venv
   source .venv/bin/activate

   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

5. Run the Flask app:

   ```bash
   python app.py
   ```

6. Open http://127.0.0.1:5000 in your browser.

## Running Tests

Tests are written with **pytest**. From the `starter` directory, run:

```bash
pytest -v
```

The suite covers the core Sudoku logic (safety checks, board filling,
unique-solution generation, difficulty mapping) and the Flask routes
(`/check` and `/hint`, including error handling).

## Project Structure

```
starter/
├── app.py              # Flask routes: /new, /check, /hint
├── sudoku_logic.py     # Puzzle generation, solving, and validation
├── requirements.txt
├── static/
│   ├── main.js         # Client-side game logic and rendering
│   └── styles.css
├── templates/
│   └── index.html
└── tests/              # pytest test suite
```

## Working with Copilot

An `instruction.md` file at the project root defines the coding standards and
project context provided to GitHub Copilot. Screenshots of key Copilot
interactions (test setup, unique-solution generation, leaderboard/localStorage,
and evaluating suggestions) are in the `Screenshots/` folder.
