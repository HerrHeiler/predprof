import React, { useState, useEffect } from "react";
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const navigate = useNavigate();

    // Проверяем авторизацию при загрузке компонента (опционально)
    useEffect(() => {
        const token = localStorage.getItem('authToken');
        if (token) {
            navigate('/homeadmin'); // Если токен есть, сразу перенаправляем
        }
    }, [navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch("http://localhost:5000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                // Сохраняем токен и данные пользователя в localStorage
                localStorage.setItem('authToken', data.token); // Если бэкенд возвращает токен
                localStorage.setItem('userRole', data.role);
                localStorage.setItem('userEmail', data.email);   
                
                setMessage(data.message);
                if (data.role === 'user') {
                    navigate('/homeuser');
                } else {
                    navigate('/homeadmin');
                }
            } else {
                setMessage(data.message);
            }
        } catch (error) {
            console.error("Ошибка при авторизации:", error);
            setMessage("Произошла ошибка при подключении к серверу.");
        }
    };
    const handleRegRedirect = () => {
        navigate('/register');
    };

    return (
        <div
            style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                height: "100vh",
                fontFamily: "Arial, sans-serif",
            }}
        >
            <h1 style={{ marginBottom: "20px" }}>Авторизация</h1>
            <form
                onSubmit={handleSubmit}
                style={{
                    display: "flex",
                    flexDirection: "column",
                    width: "300px",
                    gap: "15px",
                }}
            >
                <div style={{ display: "flex", flexDirection: "column" }}>
                    <label htmlFor="email" style={{ marginBottom: "5px" }}>Электронная почта:</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        style={{
                            padding: "10px",
                            fontSize: "16px",
                            borderRadius: "5px",
                            border: "1px solid #ccc",
                        }}
                    />
                </div>
                <div style={{ display: "flex", flexDirection: "column" }}>
                    <label htmlFor="password" style={{ marginBottom: "5px" }}>Пароль:</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        style={{
                            padding: "10px",
                            fontSize: "16px",
                            borderRadius: "5px",
                            border: "1px solid #ccc",
                        }}
                    />
                </div>
                <button
                onClick={handleRegRedirect}
                style={{
                    padding: "10px",
                    fontSize: "16px",
                    borderRadius: "5px",
                    border: "1px solid #4CAF50",
                    backgroundColor: "transparent",
                    color: "#4CAF50",
                    cursor: "pointer",
                    marginTop: "15px",
                    width: "300px",
                    transition: "all 0.3s",
                    ':hover': {
                        backgroundColor: "#4CAF50",
                        color: "white"
                    }
                }}
            >
                Нет аккаунта? Создать
            </button>
                <button
                    type="submit"
                    style={{
                        padding: "10px",
                        fontSize: "16px",
                        borderRadius: "5px",
                        border: "none",
                        backgroundColor: "#4CAF50",
                        color: "white",
                        cursor: "pointer",
                    }}
                >
                    Войти
                </button>
            </form>
            {message && (
                <p
                    style={{
                        marginTop: "20px",
                        color: message.includes("успешна") ? "green" : "red",
                    }}
                >
                    {message}
                </p>
            )}
        </div>
    );
};

export default LoginPage;