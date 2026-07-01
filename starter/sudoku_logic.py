import copy
import random
from typing import List

SIZE = 9
EMPTY = 0

DIFFICULTY_TO_CLUES = {
    "easy": 40,
    "medium": 32,
    "hard": 26,
}

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def count_solutions(board: List[List[int]], limit: int = 2) -> int:
    """Count the number of solutions for `board` up to `limit`.

    Uses backtracking and stops early once `limit` solutions are found.
    Returns the number of solutions found (<= limit).
    """
    # Work on a copy so we don't mutate the caller's board
    b = [row[:] for row in board]
    count = 0

    def backtrack() -> None:
        nonlocal count
        if count >= limit:
            return
        # Find first empty cell
        for i in range(SIZE):
            for j in range(SIZE):
                if b[i][j] == EMPTY:
                    row, col = i, j
                    break
            else:
                continue
            break
        else:
            # No empty cells: valid complete solution found
            count += 1
            return

        for num in range(1, SIZE + 1):
            if is_safe(b, row, col, num):
                b[row][col] = num
                backtrack()
                b[row][col] = EMPTY
                if count >= limit:
                    return

    backtrack()
    return count

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    """Remove cells from a full `board` down to `clues` while keeping a
    unique solution. Cells are tried in random order and a removal is kept
    only if the resulting puzzle still has exactly one solution.

    Stops early if no more cells can be removed without breaking uniqueness.
    """

    to_remove = SIZE * SIZE - clues
    # Collect coordinates of filled cells
    coords = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] != EMPTY]
    random.shuffle(coords)

    # Repeatedly try to remove cells until we've removed enough or no progress
    removed = 0
    progress = True
    while removed < to_remove and progress:
        progress = False
        for (row, col) in coords:
            if removed >= to_remove:
                break
            if board[row][col] == EMPTY:
                continue
            # Temporarily remove
            saved = board[row][col]
            board[row][col] = EMPTY
            # If puzzle still has a single solution, keep removal
            if count_solutions(board, limit=2) == 1:
                removed += 1
                progress = True
            else:
                # Restore if removal produced multiple solutions
                board[row][col] = saved
        # If we made progress, shuffle remaining coords to try new orders
        if progress:
            random.shuffle(coords)

    # Finished either because removed enough or no further removals are possible

def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution


def generate_by_difficulty(difficulty: str = "medium") -> tuple:
    """Generate a Sudoku puzzle for the requested difficulty level."""
    clue_count = DIFFICULTY_TO_CLUES.get(difficulty.lower(), DIFFICULTY_TO_CLUES["medium"])
    return generate_puzzle(clues=clue_count)
