import React, { useState, useEffect } from "react";
import { Table, Button, Modal, Form, Input, message } from "antd";
import { PlusOutlined, DeleteOutlined, ExclamationCircleFilled } from '@ant-design/icons';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const { TextArea } = Input;
const { confirm } = Modal;

const PlansBuy = () => {
  const [plans, setPlans] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPlans();
    checkAuth();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem('authToken');
    const role = localStorage.getItem('userRole');
    if (!token || role !== 'admin') navigate('/login');
  };

  const fetchPlans = async () => {
    try {
      const response = await axios.get('http://localhost:5000/plan', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });

      const formattedPlans = response.data.map((plan, index) => ({
        key: plan[0],
        id: plan[0],
        text: plan[1],
        items: Object.keys(JSON.parse(plan[2])).join(', '),
        amounts: Object.values(JSON.parse(plan[2])).map(i => i[0]).join(', '),
        prices: Object.values(JSON.parse(plan[2])).map(i => i[1]).join(', '),
        deadline: new Date(plan[4] * 1000).toLocaleDateString()
      }));
      
      setPlans(formattedPlans);
    } catch (error) {
      handleError(error, 'Ошибка загрузки планов');
    }
  };

  const handleDeletePlan = (planId) => {
    confirm({
      title: 'Удалить этот план закупок?',
      icon: <ExclamationCircleFilled />,
      content: 'Все данные будут удалены безвозвратно!',
      okText: 'Удалить',
      okType: 'danger',
      cancelText: 'Отмена',
      async onOk() {
        try {
          await axios.delete(`http://localhost:5000/plan/${planId}`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
          });
          message.success('План удален!');
          fetchPlans();
        } catch (error) {
          handleError(error, 'Ошибка удаления плана');
        }
      }
    });
  };

  const handleSubmit = async (values) => {
    try {
      const deadlineDate = new Date(values.deadline);
      const deadlineTimestamp = Math.floor(deadlineDate.getTime() / 1000);

      const requestData = {
        text: values.text,
        items: values.items.split(',').map(i => i.trim()).filter(i => i),
        amounts: values.amounts.split(',').map(n => parseInt(n.trim())).filter(n => !isNaN(n)),
        prices: values.prices.split(',').map(n => parseFloat(n.trim())).filter(n => !isNaN(n)),
        deadline: deadlineTimestamp,
        email: localStorage.getItem('userEmail')
      };

      // Валидация
      if (requestData.items.length !== requestData.amounts.length || 
          requestData.items.length !== requestData.prices.length) {
        return message.error('Количество элементов должно совпадать');
      }

      const response = await axios.post('http://localhost:5000/plan', requestData, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.data.success) {
        message.success('План создан!');
        fetchPlans();
        setIsModalOpen(false);
        form.resetFields();
      }
    } catch (error) {
      handleError(error, 'Ошибка создания плана');
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
    { title: 'Описание', dataIndex: 'text', key: 'text' },
    { title: 'Предметы', dataIndex: 'items', key: 'items' },
    { title: 'Количество', dataIndex: 'amounts', key: 'amounts' },
    { title: 'Цены', dataIndex: 'prices', key: 'prices' },
    { title: 'Срок', dataIndex: 'deadline', key: 'deadline' },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Button
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleDeletePlan(record.id)}
        />
      ),
    }
  ];

  return (
    <div style={{ padding: 20 }}>
      <h2>Планы закупок</h2>
      <Button 
        type="primary" 
        onClick={() => navigate('/homeadmin')} 
        style={{ position: 'absolute', top: 20, right: 20 }}
      >
        На главную
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
                value?.split(',').some(v => v.trim()) ? 
                Promise.resolve() : 
                Promise.reject('Введите хотя бы один предмет')
            }]}
          >
            <Input placeholder="Мячи, Сетка, Форма" />
          </Form.Item>

          <Form.Item
            name="amounts"
            label="Количество (через запятую)"
            rules={[{ 
              required: true,
              validator: (_, value) => 
                value?.split(',').every(n => !isNaN(n.trim())) ? 
                Promise.resolve() : 
                Promise.reject('Только числа через запятую')
            }]}
          >
            <Input placeholder="10, 5, 20" />
          </Form.Item>

          <Form.Item
            name="prices"
            label="Цены (через запятую)"
            rules={[{ 
              required: true,
              validator: (_, value) => 
                value?.split(',').every(n => !isNaN(n.trim())) ? 
                Promise.resolve() : 
                Promise.reject('Только числа через запятую')
            }]}
          >
            <Input placeholder="1500, 3000, 2000" />
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