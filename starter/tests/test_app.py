import pytest

from app import CURRENT, app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_current_state():
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None
    yield
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None


def test_check_returns_400_for_malformed_board(client):
    response = client.post('/check', json={'board': [[1, 2, 3]]})

    assert response.status_code == 400
    assert response.is_json
    assert 'error' in response.get_json()


def test_hint_returns_solution_value_for_an_empty_cell(client):
    CURRENT['solution'] = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ]
    # Board is empty except one filled cell, so any hint must target an empty cell.
    board = [[0] * 9 for _ in range(9)]
    board[0][0] = 1

    response = client.post('/hint', json={'board': board})

    assert response.status_code == 200
    data = response.get_json()
    r, c, v = data['row'], data['column'], data['value']

    # The hint must target a cell that was empty in the submitted board.
    assert board[r][c] == 0, "Hint must fill a cell that was empty"
    # And its value must match the stored solution at that cell.
    assert v == CURRENT['solution'][r][c], "Hint value must match the solution"


def test_hint_returns_400_when_no_game_in_progress(client):
    # No solution stored (reset by the autouse fixture).
    board = [[0] * 9 for _ in range(9)]
    response = client.post('/hint', json={'board': board})

    assert response.status_code == 400
    assert 'error' in response.get_json()