import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
const HomePageUser = () => {
    const navigate = useNavigate();
    const handleLogout = () => {
        // Очищаем данные авторизации
        localStorage.removeItem('authToken');
        localStorage.removeItem('userRole');
        // Перенаправляем на страницу входа
        navigate('/login');
    };
    useEffect(() => {
        const token = localStorage.getItem('authToken');
        if (!token) {
            navigate('/login');
        }
    }, [navigate]);
    return (
        <div>
            <button 
                onClick={handleLogout}
                style={{
                    padding: "10px",
                    backgroundColor: "#f44336",
                    color: "white",
                    border: "none",
                    borderRadius: "5px",
                    cursor: "pointer",
                    position: "absolute",
                    top: "20px",
                    right: "20px"
                }}
            >
                Выйти
            </button>
        </div>
    );
};
export default HomePageUser;
