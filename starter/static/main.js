// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_STORAGE_KEY = 'sudokuTop10';
let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let hintsUsed = 0;
let gameCompleted = false;
let scoreboardEntries = [];

function updateTimerDisplay() {
  const minutes = Math.floor(elapsedSeconds / 60);
  const seconds = elapsedSeconds % 60;
  document.getElementById('timer').innerText = `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function startTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
  }
  elapsedSeconds = 0;
  updateTimerDisplay();
  timerInterval = window.setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function loadLeaderboard() {
  try {
    const storedEntries = window.localStorage.getItem(LEADERBOARD_STORAGE_KEY);
    if (!storedEntries) {
      return [];
    }

    const parsedEntries = JSON.parse(storedEntries);
    if (!Array.isArray(parsedEntries)) {
      return [];
    }

    return parsedEntries
      .filter((entry) => entry && typeof entry.name === 'string' && Number.isFinite(Number(entry.time)))
      .map((entry) => ({
        name: entry.name,
        time: Number(entry.time),
        difficulty: entry.difficulty || 'medium',
        hints: Number(entry.hints || 0)
      }))
      .sort((firstEntry, secondEntry) => firstEntry.time - secondEntry.time)
      .slice(0, 10);
  } catch (error) {
    console.error('Failed to load leaderboard:', error);
    return [];
  }
}

function saveLeaderboard(entries) {
  try {
    window.localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(entries));
  } catch (error) {
    console.error('Failed to save leaderboard:', error);
  }
}

function renderLeaderboard() {
  const leaderboardBody = document.getElementById('leaderboard-body');
  if (!leaderboardBody) {
    return;
  }

  leaderboardBody.innerHTML = '';

  if (scoreboardEntries.length === 0) {
    const emptyRow = document.createElement('tr');
    const emptyCell = document.createElement('td');
    emptyCell.colSpan = 5;
    emptyCell.innerText = 'No scores yet';
    emptyRow.appendChild(emptyCell);
    leaderboardBody.appendChild(emptyRow);
    return;
  }

  scoreboardEntries.forEach((entry, index) => {
    const row = document.createElement('tr');
    const rankCell = document.createElement('td');
    const nameCell = document.createElement('td');
    const timeCell = document.createElement('td');
    const difficultyCell = document.createElement('td');
    const hintsCell = document.createElement('td');

    rankCell.innerText = `${index + 1}`;
    nameCell.innerText = entry.name;
    timeCell.innerText = formatTime(entry.time);
    difficultyCell.innerText = entry.difficulty;
    hintsCell.innerText = entry.hints;

    row.append(rankCell, nameCell, timeCell, difficultyCell, hintsCell);
    leaderboardBody.appendChild(row);
  });
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function updateConflictClasses() {
  const boardDiv = document.getElementById('sudoku-board');
  if (!boardDiv) {
    return;
  }

  const inputs = Array.from(boardDiv.getElementsByTagName('input'));
  const values = inputs.map((input) => {
    const value = input.value.trim();
    return value ? parseInt(value, 10) : null;
  });
  const conflictingIndices = new Set();

  for (let index = 0; index < values.length; index += 1) {
    const value = values[index];
    if (value === null) {
      continue;
    }

    const row = Math.floor(index / SIZE);
    const col = index % SIZE;
    const boxRow = Math.floor(row / 3) * 3;
    const boxCol = Math.floor(col / 3) * 3;

    for (let offset = 0; offset < SIZE; offset += 1) {
      const rowIndex = row * SIZE + offset;
      if (rowIndex !== index && values[rowIndex] === value) {
        conflictingIndices.add(index);
        conflictingIndices.add(rowIndex);
      }

      const colIndex = offset * SIZE + col;
      if (colIndex !== index && values[colIndex] === value) {
        conflictingIndices.add(index);
        conflictingIndices.add(colIndex);
      }
    }

    for (let boxRowOffset = 0; boxRowOffset < 3; boxRowOffset += 1) {
      for (let boxColOffset = 0; boxColOffset < 3; boxColOffset += 1) {
        const boxIndex = (boxRow + boxRowOffset) * SIZE + (boxCol + boxColOffset);
        if (boxIndex !== index && values[boxIndex] === value) {
          conflictingIndices.add(index);
          conflictingIndices.add(boxIndex);
        }
      }
    }
  }

  inputs.forEach((input, index) => {
    input.classList.toggle('conflict', conflictingIndices.has(index));
  });
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.classList.remove('prefilled');
      }
    }
  }
  updateConflictClasses();
}

async function newGame() {
  const difficulty = document.getElementById('difficulty-select').value;
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  hintsUsed = 0;
  gameCompleted = false;
  startTimer();
}

function storeScoreEntry(name, finalTime, difficulty, hintsUsedCount) {
  const entry = {
    name,
    time: finalTime,
    difficulty,
    hints: hintsUsedCount
  };

  scoreboardEntries = [...scoreboardEntries, entry]
    .sort((firstEntry, secondEntry) => firstEntry.time - secondEntry.time)
    .slice(0, 10);

  saveLeaderboard(scoreboardEntries);
  renderLeaderboard();
  window.scoreboardEntries = scoreboardEntries;
}

async function checkBoardCompletion() {
  if (gameCompleted) {
    return;
  }

  const boardDiv = document.getElementById('sudoku-board');
  const inputs = Array.from(boardDiv.getElementsByTagName('input'));
  const isBoardFull = inputs.every((input) => input.disabled || input.value.trim() !== '');
  if (!isBoardFull) {
    return;
  }

  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }

  try {
    const res = await fetch('/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    const data = await res.json();
    if (data.error || data.incorrect.length > 0) {
      return;
    }

    gameCompleted = true;
    stopTimer();

    const msg = document.getElementById('message');
    const difficulty = document.getElementById('difficulty-select').value;
    const finalTime = formatTime(elapsedSeconds);
    msg.style.color = '#388e3c';
    msg.innerText = `Congratulations! You solved it in ${finalTime} with ${hintsUsed} hint(s).`;

    const name = window.prompt('Enter your name for the scoreboard:');
    if (name !== null) {
      const trimmedName = name.trim() || 'Anonymous';
      storeScoreEntry(trimmedName, elapsedSeconds, difficulty, hintsUsed);
    }
  } catch (error) {
    console.error('Failed to check board completion:', error);
  }
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    // Only mark as incorrect if not empty and in incorrect set
    if (incorrect.has(idx) && inp.value !== '') {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

async function getHint() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  // Fill the hint cell
  const row = data.row;
  const col = data.column;
  const value = data.value;
  const idx = row * SIZE + col;
  const inp = inputs[idx];
  inp.value = value;
  inp.disabled = true;
  inp.className = 'sudoku-cell prefilled hint-cell';
  hintsUsed += 1;
  msg.style.color = '#1976d2';
  msg.innerText = '';

  await checkBoardCompletion();
}

// Wire buttons
window.addEventListener('load', () => {
  scoreboardEntries = loadLeaderboard();
  renderLeaderboard();

  // Add delegated event listener for input validation on board container
  document.getElementById('sudoku-board').addEventListener('input', (e) => {
    if (e.target.classList.contains('sudoku-cell')) {
      const val = e.target.value.replace(/[^1-9]/g, '');
      e.target.value = val;
      updateConflictClasses();
      checkBoardCompletion();
    }
  });

  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-button').addEventListener('click', getHint);
  // initialize
  newGame();
});