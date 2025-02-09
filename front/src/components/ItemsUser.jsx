import React, { useState, useEffect } from "react";
import { Table, Button, Modal, Form, Input, message, Select } from "antd";
import { PlusOutlined, DeleteOutlined, ExclamationCircleFilled } from '@ant-design/icons';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const { TextArea } = Input;
const { Option } = Select;
const { confirm } = Modal;

const ItemsUser = () => {
  const [requests, setRequests] = useState([]);
  const [items, setItems] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchRequests();
    fetchItems();
    checkAuth();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem('authToken');
    const role = localStorage.getItem('userRole');
    const userEmail = localStorage.getItem('userEmail')
    if (!token || role !== 'user') navigate('/login');
  };

  const fetchRequests = async () => {
    try {
      const userEmail = localStorage.getItem('userEmail');
      const email = userEmail
      console.log('Fetching requests for email:', email); // Добавить лог
      
      const response = await axios.get('http://localhost:5000/requests', {
        params: { email },
        headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
      });
      
      console.log('Response data:', response.data); // Лог ответа
      if (response.data.success) {
        setRequests(response.data.requests);
      }
    } catch (error) {
      console.error('Error details:', error.response); // Лог ошибки
      handleError(error, 'Ошибка загрузки заявок');
    }
  };

  const fetchItems = async () => {
    try {
      const response = await axios.get('http://localhost:5000/setuseritems', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
      });
      
      if (response.data.success) {
        setItems(response.data.items.map(item => ({
          id: item.id,
          name: `${item.name} (Доступно: ${item.new})`
        })));
      }
    } catch (error) {
      handleError(error, 'Ошибка загрузки предметов');
    }
  };

  const handleDeleteRequest = (requestId) => {
    confirm({
      title: 'Удалить эту заявку?',
      icon: <ExclamationCircleFilled />,
      content: 'Заявка будет удалена безвозвратно!',
      okText: 'Удалить',
      okType: 'danger',
      cancelText: 'Отмена',
      async onOk() {
        try {
          await axios.delete(`http://localhost:5000/requests/${requestId}`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
          });
          message.success('Заявка удалена!');
          fetchRequests();
        } catch (error) {
          handleError(error, 'Ошибка удаления заявки');
        }
      }
    });
  };

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const userEmail = localStorage.getItem('userEmail');
      const response = await axios.post('http://localhost:5000/requests', {
        text: values.text,
        amount: values.amount,
        item_id: values.item_id,
        email: localStorage.getItem('userEmail')  // Добавлено явное получение email
      }, {
        headers: { 
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
          'Content-Type': 'application/json'
        }
      });
  
      if (response.data.success) {
        message.success('Заявка создана!');
        fetchRequests();
        setIsModalOpen(false);
        form.resetFields();
      }
    } catch (error) {
      handleError(error, 'Ошибка создания заявки');
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
    { title: 'Текст заявки', dataIndex: 'text', key: 'text' },
    { title: 'Количество', dataIndex: 'amount', key: 'amount' },
    { 
      title: 'Статус', 
      dataIndex: 'status', 
      key: 'status',
      render: (status) => {
        const statusMap = {
          'unread': 'Не просмотрено',
          'approved': 'Принято',
          'rejected': 'Отказано'
        };
        return statusMap[status] || status;
      }
    },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Button
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleDeleteRequest(record.id)}
          disabled={record.status !== 'unread'}
        />
      ),
    }
  ];

  return (
    <div style={{ padding: 20 }}>
      <h2>Мои заявки</h2>
      <Button 
        type="primary" 
        onClick={() => navigate('/homeuser')} 
        style={{ position: 'absolute', top: 20, right: 20 }}
      >
        На главную
      </Button>
      
      <Table 
        dataSource={requests} 
        columns={columns} 
        pagination={{ pageSize: 5 }}
        style={{ marginTop: 20 }}
        rowKey="id"
      />

      <Button
        type="primary"
        shape="circle"
        icon={<PlusOutlined />}
        onClick={() => setIsModalOpen(true)}
        style={{ position: 'fixed', bottom: 40, right: 40, width: 50, height: 50 }}
      />

      <Modal
        title="Новая заявка"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
        confirmLoading={loading}
        okText="Создать"
        cancelText="Отмена"
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="text"
            label="Описание"
            rules={[{ required: true, message: 'Введите описание заявки' }]}
          >
            <TextArea rows={3} />
          </Form.Item>

          <Form.Item
            name="item_id"
            label="Предмет"
            rules={[{ required: true, message: 'Выберите предмет' }]}
          >
            <Select
              showSearch
              placeholder="Выберите предмет"
              optionFilterProp="children"
              filterOption={(input, option) =>
                option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
              }
            >
              {items.map(item => (
                <Option key={item.id} value={item.id}>
                  {item.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="amount"
            label="Количество"
            rules={[{ 
              required: true,
              type: 'number',
              min: 1,
              transform: value => Number(value),
              message: 'Введите положительное число'
            }]}
          >
            <Input type="number" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ItemsUser;