import React from 'react';
import WeatherWidget from './WeatherWidget';
import './App.css';

export default function App() {
  return (
    <div className="App">
      <h1>Weather in Delhi</h1>
      <WeatherWidget />
    </div>
  );
}
