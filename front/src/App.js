import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HomePageUser from './components/Homepage_user';
import RegisterPage from './components/registerpage';
import LoginPage from './components/autorisation';
import HomePageAdmin from './components/Homepageadmin';
import Reports from './components/Reports';
import PlansBuy from './components/PlansBuy';
import ItemsAdmin from './components/ItemsAdmin';
const App = () => {
  return (
    <Router>
      <Routes>
        {/* Автоматическое перенаправление с корневого пути */}
        <Route 
          path="/" 
          element={
            localStorage.getItem('authToken') 
              ? (localStorage.getItem('userRole') === 'admin' 
                  ? <Navigate to="/homeadmin" replace /> 
                  : <Navigate to="/homeuser" replace />)
              : <Navigate to="/register" replace />
          } 
        />
        {/* Маршрут для главной страницы */}
        <Route path="/homeuser" element={<HomePageUser />} />
        {/* Маршрут для страницы регистрации */}
        <Route path="/register" element={<RegisterPage />} />
        {/* Маршрут для страницы авторизации */}
        <Route path="/login" element={<LoginPage />} />
        {/* Маршрут для главной страницы админа */}
        <Route path="/homeadmin" element={<HomePageAdmin />} />
        {/* Маршрут для репортов для админа*/}
        <Route path="/reports" element={<Reports />} />
        {/* Маршрут для планов покупки для админа */}
        <Route path="/plans" element={<PlansBuy />} />
        {/* Маршрут для управления инвентарём админа*/}
        <Route path="/itemsadmin" element={<ItemsAdmin />} />
        {/* Резервный маршрут для несуществующих страниц */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export default App;