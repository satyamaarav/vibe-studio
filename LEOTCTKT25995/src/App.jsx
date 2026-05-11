import React, { useState } from 'react';
import styles from './App.module.css';

const WINNING_COMBINATIONS = [
  [0, 1, 2], // rows
  [3, 4, 5],
  [6, 7, 8],
  [0, 3, 6], // columns
  [1, 4, 7],
  [2, 5, 8],
  [0, 4, 8], // diagonals
  [2, 4, 6],
];

function App() {
  const [board, setBoard] = useState(Array(9).fill(''));
  const [xIsNext, setXIsNext] = useState(true);
  const [winnerInfo, setWinnerInfo] = useState(null);

  // Place X/O, check win/draw, and handle turn
  const handleCellClick = (idx) => {
    if (board[idx] || winnerInfo) return;
    const newBoard = [...board];
    newBoard[idx] = xIsNext ? 'X' : 'O';
    setBoard(newBoard);

    const result = checkWinner(newBoard);
    if (result) {
      setWinnerInfo(result);
    } else if (newBoard.every((c) => c)) {
      setWinnerInfo({ winner: 'Draw', line: null });
    } else {
      setXIsNext(!xIsNext);
    }
  };

  // Reset whole game
  const resetGame = () => {
    setBoard(Array(9).fill(''));
    setXIsNext(true);
    setWinnerInfo(null);
  };

  // Win detection
  const checkWinner = (state) => {
    for (const combo of WINNING_COMBINATIONS) {
      const [a, b, c] = combo;
      if (state[a] && state[a] === state[b] && state[a] === state[c]) {
        return { winner: state[a], line: combo };
      }
    }
    return null;
  };

  // Highlight winning cells
  const getCellClass = (idx) => {
    return winnerInfo && winnerInfo.line?.includes(idx)
      ? `${styles.cell} ${styles.winningCell}`
      : styles.cell;
  };

  return (
    <div className={styles.game}>
      <h1>TicTakToe</h1>

      <div className={styles.turnIndicator}>
        {winnerInfo
          ? winnerInfo.winner === 'Draw'
            ? 'Draw'
            : `Winner: ${winnerInfo.winner}`
          : `Next Turn: ${xIsNext ? 'X' : 'O'}`}
      </div>

      <div className={styles.board}>
        {board.map((cell, idx) => (
          <button
            key={idx}
            className={getCellClass(idx)}
            onClick={() => handleCellClick(idx)}
          >
            {cell}
          </button>
        ))}
      </div>

      {winnerInfo && (
        <div className={styles.gameOver}>
          <p>
            {winnerInfo.winner === 'Draw'
              ? 'The game is a draw!'
              : `Player ${winnerInfo.winner} wins!`}
          </p>
          <button onClick={resetGame}>New Game</button>
        </div>
      )}
    </div>
  );
}

export default App;
