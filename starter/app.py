import random

from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}


def _validate_board(board):
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return False

    for row in board:
        if not isinstance(row, list) or len(row) != sudoku_logic.SIZE:
            return False
        for value in row:
            if not isinstance(value, int) or isinstance(value, bool):
                return False

    return True


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium')
    puzzle, solution = sudoku_logic.generate_by_difficulty(difficulty)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Board is required'}), 400

    board = data.get('board')
    if not _validate_board(board):
        return jsonify({'error': 'Board must be a 9x9 array'}), 400

    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})


@app.route('/hint', methods=['POST'])
def get_hint():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Board is required'}), 400

    board = data.get('board')
    if not _validate_board(board):
        return jsonify({'error': 'Board must be a 9x9 array'}), 400

    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    empty_cells = [
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if board[row][col] == sudoku_logic.EMPTY
    ]
    if not empty_cells:
        return jsonify({'error': 'No empty cells left'}), 400

    row, col = random.choice(empty_cells)
    return jsonify({'row': row, 'column': col, 'value': solution[row][col]})

if __name__ == '__main__':
    app.run(debug=True)