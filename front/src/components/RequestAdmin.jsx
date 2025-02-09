import React, { useState, useEffect } from "react";
import { Table, Button, Select, message } from "antd";
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const { Option } = Select;

const RequestAdmin = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchRequests();
    checkAuth();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem('authToken');
    const role = localStorage.getItem('userRole');
    if (!token || role !== 'admin') navigate('/login');
  };

  const fetchRequests = async () => {
    try {
      const response = await axios.get('http://localhost:5000/allrequests', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
      });
      
      if (response.data.success) {
        setRequests(response.data.requests);
      }
    } catch (error) {
      handleError(error, 'Ошибка загрузки заявок');
    }
  };

  const handleStatusChange = async (requestId, newStatus) => {
    try {
      setLoading(true);
      const response = await axios.put(`http://localhost:5000/requests/${requestId}`, 
        { status: newStatus },
        {
          headers: { 
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        message.success('Статус обновлён!');
        fetchRequests();
      }
    } catch (error) {
      handleError(error, 'Ошибка обновления статуса');
    } finally {
      setLoading(false);
    }
  };

  const handleError = (error, defaultMsg) => {
    if (error.response) {
      message.error(error.response.data.message || defaultMsg);
    } else {
      message.error(defaultMsg);
    }
  };

  const columns = [
    { 
      title: 'Пользователь', 
      dataIndex: 'user_name', 
      key: 'user_name' 
    },
    { 
      title: 'Текст заявки', 
      dataIndex: 'text', 
      key: 'text' 
    },
    { 
      title: 'Предмет', 
      dataIndex: 'item_name', 
      key: 'item_name' 
    },
    { 
      title: 'Количество', 
      dataIndex: 'amount', 
      key: 'amount' 
    },
    { 
      title: 'Статус', 
      key: 'status',
      render: (_, record) => (
        <Select
          value={record.status}
          onChange={(value) => handleStatusChange(record.id, value)}
          style={{ width: 150 }}
        >
          <Option value="unread">Не просмотрено</Option>
          <Option value="approved">Принято</Option>
          <Option value="rejected">Отказано</Option>
        </Select>
      )
    }
  ];

  return (
    <div style={{ padding: 20 }}>
      <h2>Заявки пользователей</h2>
      <Button 
        type="primary" 
        onClick={() => navigate('/homeadmin')} 
        style={{ position: 'absolute', top: 20, right: 20 }}
      >
        На главную
      </Button>
      
      <Table 
        dataSource={requests} 
        columns={columns} 
        loading={loading}
        pagination={{ pageSize: 10 }}
        rowKey="id"
        style={{ marginTop: 20 }}
      />
    </div>
  );
};

export default RequestAdmin;