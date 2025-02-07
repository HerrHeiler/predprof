import React, { useState, useEffect } from "react";
import { Table, Button, Modal, Form, Input, message } from "antd";
import { PlusOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const { TextArea } = Input;

const PlansBuy = () => {
  const [plans, setPlans] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();
  // Получение планов при загрузке компонента
  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
        const response = await axios.get('http://localhost:5000/plan');
        const plansData = response.data; // Получаем данные

        // Проверяем, что данные являются массивом
        if (Array.isArray(plansData)) {
            setPlans(plansData.map((plan, index) => ({
                key: index,
                text: plan[1], // Используем индекс для доступа к тексту
                items: Object.keys(JSON.parse(plan[2])).join(', '), // Используем индекс для доступа к item_amount_price
                amounts: Object.values(JSON.parse(plan[2])).map(i => i[0]).join(', '),
                prices: Object.values(JSON.parse(plan[2])).map(i => i[1]).join(', '),
                deadline: new Date(plan[4] * 1000).toLocaleDateString() // Используем индекс для доступа к deadline
            })));
        } else {
            message.error('Полученные данные не являются массивом');
        }
    } catch (error) {
        if (error.response) {
            message.error(`Ошибка сервера: ${error.response.data.message}`);
        } else if (error.request) {
            message.error('Нет ответа от сервера');
        } else {
            message.error('Ошибка настройки запроса');
        }
    }
};

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const role = localStorage.getItem('userRole');
    
    if (!token || role !== 'admin') {
      navigate('/login');
    }
  }, [navigate]);

  const handleSubmit = async (values) => {
    try {
      const userEmail = localStorage.getItem('userEmail');
      if (!userEmail) {
        message.error('Ошибка авторизации ');
        navigate('/login');
        return;
      }

      const deadlineDate = new Date(values.deadline);
      if (isNaN(deadlineDate.getTime())) {
        message.error('Неверный формат даты');
        return;
      }
      const deadlineTimestamp = Math.floor(deadlineDate.getTime() / 1000);

      const requestData = {
        text: values.text,
        items: values.items.split(',').map(i => i.trim()).filter(i => i),
        amounts: values.amounts.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n)),
        prices: values.prices.split(',').map(n => parseFloat(n.trim())).filter(n => !isNaN(n)),
        deadline: deadlineTimestamp,
        email: userEmail
      };

      if (
        !requestData.text || 
        requestData.items.length === 0 ||
        requestData.amounts.length === 0 ||
        requestData.prices.length === 0
      ) {
        message.error('Заполните все обязательные поля');
        return;
      }

      if (requestData.items.length !== requestData.amounts.length || 
          requestData.items.length !== requestData.prices.length) {
        message.error('Количество элементов в полях должно совпадать');
        return;
      }

      const response = await axios.post('http://localhost:5000/plan', requestData, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.data.success) {
        message.success('План успешно создан!');
        fetchPlans();
        setIsModalOpen(false);
        form.resetFields();
      } else {
        message.error('Ошибка при создании плана: ' + response.data.message);
      }
    } catch (error) {
      console.error('Ошибка:', error);
      message.error(`Ошибка создания плана: ${error.response?.data?.message || error.message}`);
    }
  };

  const columns = [
    { title: 'Описание', dataIndex: 'text', key: 'text' },
    { title: 'Предметы', dataIndex: 'items', key: 'items' },
    { title: 'Количество', dataIndex: 'amounts', key: 'amounts' },
    { title: 'Цены', dataIndex: 'prices', key: 'prices' },
    { title: 'Срок', dataIndex: 'deadline', key: 'deadline' }
  ];

  return (
    <div style={{ padding: 20 }}>
      <h2>Планы закупок</h2>
      <Button 
        type="primary" 
        onClick={() => navigate('/homeadmin')} 
        style={{ position: 'absolute', top: 20, right: 20 }}
      >
        Перейти на главную
      </Button>
      <Table 
        dataSource={plans} 
        columns={columns} 
        pagination={{ pageSize: 5 }}
        style={{ marginTop: 20 }}
      />

      <Button
        type="primary"
        shape="circle"
        icon={<PlusOutlined />}
        onClick={() => setIsModalOpen(true)}
        style={{ position: 'fixed', bottom: 40, right: 40, width: 50, height: 50 }}
      />

      <Modal
        title="Новый план закупок"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
        okText="Создать"
        cancelText="Отмена"
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="text"
            label="Описание"
            rules={[{ required: true, message: 'Введите описание плана' }]}
          >
            <TextArea rows={3} />
          </Form.Item>

          <Form.Item
            name="items"
            label="Предметы (через запятую)"
            rules={[{ 
              required: true,
              validator: (_, value) => 
                value && value.split(',').some(v => v.trim() !== '') ? 
                Promise.resolve() : 
                Promise.reject('Введите хотя бы одно значение')
            }]}
          >
            <Input placeholder="Например: Мячи, Сетка, Форма" />
          </Form.Item>

          <Form.Item
            name="amounts"
            label="Количество (через запятую)"
            rules={[{ 
              required: true,
              validator: (_, value) => 
                value && value.split(',').every(n => !isNaN(n.trim())) ? 
                Promise.resolve() : 
                Promise.reject('Введите числа через запятую')
            }]}
          >
            <Input placeholder="Например: 10, 5, 20" />
          </Form.Item>

          <Form.Item
            name="prices"
            label="Цены (через запятую)"
            rules={[{ 
              required: true,
              validator: (_, value) => 
                value && value.split(',').every(n => !isNaN(n.trim())) ? 
                Promise.resolve() : 
                Promise.reject('Введите числа через запятую')
            }]}
          >
            <Input placeholder="Например: 1500, 3000, 2000" />
          </Form.Item>

          <Form.Item
            name="deadline"
            label="Срок выполнения"
            rules={[{ required: true, message: 'Выберите дату' }]}
          >
            <Input type="date" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PlansBuy;