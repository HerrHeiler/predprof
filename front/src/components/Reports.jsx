import React, { useState, useEffect } from "react";
import { Table, Button, Modal, Form, Input, message } from "antd";
import { PlusOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import moment from 'moment';
import { DeleteOutlined } from '@ant-design/icons';
const { TextArea } = Input;

const Reports = () => {
  const [reports, setReports] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  useEffect(() => {
    fetchReports();
    checkAuth();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem('authToken');
    const role = localStorage.getItem('userRole');
    if (!token || role !== 'admin') navigate('/login');
  };

  const fetchReports = async () => {
    try {
      const response = await axios.get('http://localhost:5000/reports', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });
      
      if (response.data.success) {
        const formattedData = response.data.reports.map(report => ({
          key: report.id,
          id: report.id,
          text: report.text,
          date: moment.unix(report.date).format('DD.MM.YYYY HH:mm')
        }));
        setReports(formattedData);
      }
    } catch (error) {
      handleError(error, 'Ошибка загрузки отчетов');
    }
  };

  const handleSubmit = async (values) => {
    try {
      const response = await axios.post('http://localhost:5000/reports', 
        { text: values.text },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.data.success) {
        message.success('Отчет добавлен!');
        fetchReports();
        setIsModalOpen(false);
        form.resetFields();
      }
    } catch (error) {
      handleError(error, 'Ошибка создания отчета');
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
      title: 'Текст отчета', 
      dataIndex: 'text', 
      key: 'text',
      width: '70%'
    },
    { 
      title: 'Дата создания', 
      dataIndex: 'date', 
      key: 'date',
      width: '20%'
    },
    {
      title: 'Действия',
      key: 'actions',
      width: '10%',
      render: (_, record) => (
        <Button
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleDelete(record.id)}
        />
      ),
    },
  ];
  
  // Добавить функцию удаления
  const handleDelete = async (reportId) => {
    try {
      const response = await axios.delete(`http://localhost:5000/reports/${reportId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });
  
      if (response.data.success) {
        message.success('Отчет удален!');
        fetchReports();
      }
    } catch (error) {
      handleError(error, 'Ошибка удаления отчета');
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Управление отчетами</h2>
      
      <Button 
        type="primary" 
        onClick={() => navigate('/homeadmin')}
        style={{ position: 'absolute', top: 20, right: 20 }}
      >
        На главную
      </Button>

      <Table
        dataSource={reports}
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
        title="Новый отчет"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
        okText="Создать"
        cancelText="Отмена"
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit}>
          <Form.Item
            name="text"
            label="Текст отчета"
            rules={[{ required: true, message: 'Введите текст отчета' }]}
          >
            <TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Reports;