import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './components/Homepage';
import RegisterPage from './components/registerpage';
import LoginPage from './components/autorisation';
const App = () => {
  return (
    <Router>
      <Routes>
        {/* Маршрут для главной страницы */}
        <Route path="/home" element={<HomePage />} />
        {/* Маршрут для страницы регистрации */}
        <Route path="/" element={<RegisterPage />} />
        {/* Маршрут для страницы авторизации */}
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </Router>
  );
};

export default App;