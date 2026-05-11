import React, { useState } from 'react';
import './App.css';

function App() {
  const [expenses, setExpenses] = useState([]);
  const [name, setName] = useState('');
  const [date, setDate] = useState('');
  const [amount, setAmount] = useState('');

  const addExpense = (e) => {
    e.preventDefault();
    if (!name || !date || !amount) return;
    const newExpense = { name, date, amount: parseFloat(amount) };
    setExpenses([...expenses, newExpense]);
    setName('');
    setDate('');
    setAmount('');
  };

  const total = expenses.reduce((sum, exp) => sum + exp.amount, 0);

  return (
    <div className="App">
      <h1>Expense Tracker</h1>
      <form onSubmit={addExpense}>
        <input
          type="text"
          placeholder="Expense name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
        <input
          type="number"
          step="0.01"
          placeholder="Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <button type="submit">Add Expense</button>
      </form>
      <h2>Total: ${total.toFixed(2)}</h2>
      <ul>
        {expenses.map((exp, idx) => (
          <li key={idx}>
            {exp.date} - {exp.name}: ${exp.amount.toFixed(2)}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
