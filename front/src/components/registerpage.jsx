// RegisterPage.jsx
import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';
const RegisterPage = () => {
    const [FIO, setFIO] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const navigate = useNavigate(); 
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch("http://localhost:5000/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ FIO, email, password }),
            });

            const data = await response.json();
            
            if (response.ok) {
                setMessage(data.message);
                navigate('/login'); // Добавлено перенаправление
            } else {
                setMessage(data.message);
            }
        
        } catch(error) {
            console.error("Ошибка при отправке", error)
            setMessage("Произошла ошибка")
        }
        
        
    };
    const handleLoginRedirect = () => {
        navigate('/login');
    };
    

    return (
        <div style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            height: "100vh",
            fontFamily: "Arial, sans-serif",
        }}>
            <h1 style={{ marginBottom: "20px" }}>Регистрация</h1>
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
                    <label htmlFor="FIO" style={{ marginBottom: "5px" }}>ФИО:</label>
                    <input
                        type="text"
                        id="FIO"
                        value={FIO}
                        onChange={(e) => setFIO(e.target.value)}
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
                onClick={handleLoginRedirect}
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
                Уже есть аккаунт? Войти
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
                    Зарегистрироваться
                </button>
            </form>
            {message && (
                <p style={{
                    marginTop: "20px",
                    color: message.includes("успешно") ? "green" : "red",
                }}>
                    {message}
                </p>
            )}
        </div>
    );
};

export default RegisterPage;