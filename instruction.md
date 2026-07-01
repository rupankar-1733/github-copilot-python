# Copilot Instructions — Sudoku Refactor

You are helping me refactor a legacy Flask + vanilla-JS Sudoku game into modern,
maintainable, well-tested code. Follow these standards in every suggestion.

## Stack
- Backend: Python 3 + Flask. Logic in `sudoku_logic.py`, routes in `app.py`.
- Frontend: vanilla JS + HTML + CSS, no frameworks.
- Tests: pytest. Tests must pass before and after every change.
- The puzzle generator MUST produce boards with exactly one unique solution.

## Style
- Python: PEP 8, type hints, docstrings, small single-purpose functions.
- JS: modern ES6+, no jQuery, event delegation for board input.
- Descriptive names. Explain non-obvious code briefly.

## Structure
- Keep game logic separate from routes and from DOM/rendering code.
- Prefer pure, testable functions and reusable helpers over copy-paste.

## Error handling
- Validate input at API boundaries; return JSON errors with proper status codes.
- Client fails gracefully with a user-facing message.

## How to help
- Give focused diffs, not sweeping rewrites, unless I ask.
- Flag anything that could break existing tests.
- I will accept or reject each suggestion.