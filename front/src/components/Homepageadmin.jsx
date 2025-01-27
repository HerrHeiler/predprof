import React from 'react';
import { useNavigate } from 'react-router-dom';

const HomePageAdmin = () => {
    const navigate = useNavigate();

    const handleNavigation = (path) => {
        navigate(path);
    };

    return (
        <div
            style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100vh',
                fontFamily: 'Arial, sans-serif',
                background: '#f4f4f4',
                padding: '20px',
            }}
        >
            <h1 style={{ marginBottom: '30px', fontSize: '28px', fontWeight: 'bold', color: '#333' }}>
                Административная Панель
            </h1>
            <div
                style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '20px',
                    maxWidth: '400px',
                    width: '100%',
                }}
            >
                <button
                    onClick={() => handleNavigation('/itemsadmin')}
                    style={{
                        padding: '15px',
                        fontSize: '16px',
                        borderRadius: '10px',
                        border: 'none',
                        background: '#007BFF',
                        color: 'white',
                        cursor: 'pointer',
                        transition: 'background 0.3s',
                    }}
                    onMouseOver={(e) => (e.target.style.background = '#0056b3')}
                    onMouseOut={(e) => (e.target.style.background = '#007BFF')}
                >
                    Управление Инвентарём
                </button>
                <button
                    onClick={() => handleNavigation('/plans')}
                    style={{
                        padding: '15px',
                        fontSize: '16px',
                        borderRadius: '10px',
                        border: 'none',
                        background: '#28A745',
                        color: 'white',
                        cursor: 'pointer',
                        transition: 'background 0.3s',
                    }}
                    onMouseOver={(e) => (e.target.style.background = '#1e7e34')}
                    onMouseOut={(e) => (e.target.style.background = '#28A745')}
                >
                    Планирование Закупок
                </button>
                <button
                    onClick={() => handleNavigation('/reports')}
                    style={{
                        padding: '15px',
                        fontSize: '16px',
                        borderRadius: '10px',
                        border: 'none',
                        background: '#FFC107',
                        color: '#212529',
                        cursor: 'pointer',
                        transition: 'background 0.3s',
                    }}
                    onMouseOver={(e) => (e.target.style.background = '#e0a800')}
                    onMouseOut={(e) => (e.target.style.background = '#FFC107')}
                >
                    Отчёты по Инвентарю
                </button>
            </div>
        </div>
    );
};

export default HomePageAdmin;