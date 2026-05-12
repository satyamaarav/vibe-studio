import React from 'react';
import mockWeather from './mockWeather';
import './WeatherWidget.css';

export default function WeatherWidget() {
  const { temp, humidity, description, icon } = mockWeather;

  return (
    <div className="weather-widget">
      <img src={icon} alt={description} className="icon" />
      <div className="temp">{temp}°C</div>
      <div>{description}</div>
      <div>Humidity: {humidity}%</div>
    </div>
  );
}
