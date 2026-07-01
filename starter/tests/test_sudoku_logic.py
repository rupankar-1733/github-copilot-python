import random

import pytest

from sudoku_logic import SIZE, EMPTY, create_empty_board, fill_board, generate_by_difficulty, generate_puzzle, is_safe

def test_generated_puzzles_have_unique_solution():
    """Every generated puzzle must have exactly one solution."""
    from sudoku_logic import count_solutions
    for _ in range(5):
        puzzle, _ = generate_puzzle(clues=35)
        assert count_solutions(puzzle, limit=2) == 1, "Generated puzzle must be unique"

def board_is_valid(board):
    # Validate rows
    for row in board:
        assert set(row) == set(range(1, SIZE + 1)), "Each row must contain digits 1 through 9 exactly once"

    # Validate columns
    for col in range(SIZE):
        column = [board[row][col] for row in range(SIZE)]
        assert set(column) == set(range(1, SIZE + 1)), "Each column must contain digits 1 through 9 exactly once"

    # Validate 3x3 boxes
    for box_row in range(0, SIZE, 3):
        for box_col in range(0, SIZE, 3):
            box = [
                board[r][c]
                for r in range(box_row, box_row + 3)
                for c in range(box_col, box_col + 3)
            ]
            assert set(box) == set(range(1, SIZE + 1)), "Each 3x3 box must contain digits 1 through 9 exactly once"


def test_is_safe_returns_false_for_row_conflict():
    board = create_empty_board()
    board[0][0] = 5
    assert not is_safe(board, 0, 4, 5)


def test_is_safe_returns_false_for_column_conflict():
    board = create_empty_board()
    board[0][0] = 7
    assert not is_safe(board, 4, 0, 7)


def test_is_safe_returns_false_for_box_conflict():
    board = create_empty_board()
    board[1][1] = 9
    assert not is_safe(board, 2, 2, 9)


def test_is_safe_returns_true_when_safe():
    board = create_empty_board()
    board[0][0] = 1
    board[0][1] = 2
    board[1][0] = 3
    assert is_safe(board, 2, 2, 4)


def test_fill_board_produces_full_valid_board():
    random.seed(0)
    board = create_empty_board()
    assert fill_board(board), "fill_board should return True on an empty board"

    assert all(cell != EMPTY for row in board for cell in row), "Board must be fully filled"
    board_is_valid(board)


def test_generate_by_difficulty_uses_expected_clue_counts(monkeypatch):
    calls = []

    def fake_generate_puzzle(clues=35):
        calls.append(clues)
        return [[0]], [[1]]

    monkeypatch.setattr("sudoku_logic.generate_puzzle", fake_generate_puzzle)

    for difficulty, expected_clues in [("easy", 40), ("medium", 32), ("hard", 26), ("unknown", 32)]:
        calls.clear()
        generate_by_difficulty(difficulty)
        assert calls == [expected_clues], f"{difficulty} should map to {expected_clues} clues"


def test_generate_puzzle_returns_valid_puzzle_and_solution():
    random.seed(1)
    puzzle, solution = generate_puzzle(clues=35)

    assert puzzle != solution, "Puzzle and solution should not be identical once holes are removed"
    assert len(puzzle) == SIZE and len(solution) == SIZE

    board_is_valid(solution)

    for row in range(SIZE):
        for col in range(SIZE):
            if puzzle[row][col] != EMPTY:
                assert puzzle[row][col] == solution[row][col], (
                    "All non-zero puzzle cells must match the solution at the same location"
                )

    # Validate that puzzle does not introduce invalid filled cells relative to the solution
    for row in range(SIZE):
        for col in range(SIZE):
            if puzzle[row][col] != EMPTY:
                assert 1 <= puzzle[row][col] <= SIZE

    non_zero_cells = sum(1 for row in puzzle for cell in row if cell != EMPTY)
    assert non_zero_cells >= 35, "Puzzle should have exactly the requested number of clues"


def test_generate_by_difficulty_returns_valid_puzzles_with_minimum_clues():
    expected_clue_counts = {
        "easy": 40,
        "medium": 32,
        "hard": 26,
    }

    for difficulty, minimum_clues in expected_clue_counts.items():
        puzzle, solution = generate_by_difficulty(difficulty)

        assert len(puzzle) == SIZE and len(solution) == SIZE
        board_is_valid(solution)

        clue_count = sum(1 for row in puzzle for cell in row if cell != EMPTY)
        assert clue_count >= minimum_clues, (
            f"{difficulty} puzzle should have at least {minimum_clues} clues, got {clue_count}"
        )
