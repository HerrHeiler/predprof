import React, { useState, useEffect } from "react";
import { Table, Button, Modal, Form, Input, message, Select, Space } from "antd";
import { PlusOutlined, EditOutlined, DeleteOutlined, UserAddOutlined, CloseOutlined, ExclamationCircleFilled } from '@ant-design/icons';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const { Option } = Select;
const { confirm } = Modal;

const ItemsAdmin = () => {
  const [items, setItems] = useState([]);
  const [users, setUsers] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [form] = Form.useForm();
  const [editForm] = Form.useForm();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchItems();
    fetchUsers();
  }, []);

  const fetchItems = async () => {
    try {
      const authToken = localStorage.getItem('authToken');
      const response = await axios.get('http://localhost:5000/setitems', {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      if (response.data.success) {
        const formattedItems = response.data.items.map(item => {
          let used = [];
          try {
            used = item.used ? JSON.parse(item.used) : [];
          } catch (e) {
            console.error('Ошибка парсинга used:', e);
            used = [];
          }

          return {
            ...item,
            key: item.id,
            used,
            total: item.new + used.reduce((sum, u) => sum + (u.amount || 0), 0) + item.broken
          };
        });
        setItems(formattedItems);
      }
    } catch (error) {
      handleApiError(error, 'Ошибка при загрузке предметов');
    }
  };

  const fetchUsers = async () => {
    try {
      const authToken = localStorage.getItem('authToken');
      const response = await axios.get('http://localhost:5000/users', {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      
      if (response.data.success) {
        setUsers(response.data.users);
      }
    } catch (error) {
      console.error('Ошибка при загрузке пользователей:', error);
    }
  };

  const handleAddItem = async (values) => {
    setLoading(true);
    try {
      const authToken = localStorage.getItem('authToken');
      const userEmail = localStorage.getItem('userEmail');
      
      if (!authToken || !userEmail) {
        navigate('/login');
        return;
      }

      const response = await axios.post('http://localhost:5000/setitems', {
        name: values.name,
        amount: parseInt(values.amount, 10),
        email: userEmail
      }, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.data.success) {
        await fetchItems();
        message.success('Предмет успешно добавлен!');
        setIsModalOpen(false);
        form.resetFields();
      }
    } catch (error) {
      handleApiError(error, 'Ошибка при добавлении предмета');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateItem = async (values) => {
    setLoading(true);
    try {
      const authToken = localStorage.getItem('authToken');
      
      const processedUsed = (values.used || []).map(u => ({
        email: u.email,
        amount: Number(u.amount) || 0
      }));

      const parsedValues = {
        ...values,
        new: Number(values.new) || 0,
        broken: Number(values.broken) || 0,
        used: processedUsed
      };

      const response = await axios.put('http://localhost:5000/updateitem', parsedValues, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.data.success) {
        await fetchItems();
        message.success('Изменения сохранены!');
        setIsEditModalOpen(false);
      }
    } catch (error) {
      handleApiError(error, 'Ошибка при обновлении предмета');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteItem = (itemId) => {
    confirm({
      title: 'Вы уверены, что хотите удалить этот предмет?',
      icon: <ExclamationCircleFilled />,
      content: 'Все связанные данные будут удалены безвозвратно!',
      okText: 'Удалить',
      okType: 'danger',
      cancelText: 'Отмена',
      async onOk() {
        try {
          const authToken = localStorage.getItem('authToken');
          const response = await axios.delete(`http://localhost:5000/items/${itemId}`, {
            headers: {
              'Authorization': `Bearer ${authToken}`
            }
          });

          if (response.data.success) {
            message.success('Предмет удален!');
            await fetchItems();
          }
        } catch (error) {
          handleApiError(error, 'Ошибка удаления предмета');
        }
      }
    });
  };

  const handleApiError = (error, defaultMessage) => {
    console.error('API Error:', error);
    if (error.response) {
      if (error.response.status === 403) {
        message.error('Доступ запрещен');
        navigate('/login');
      } else {
        message.error(error.response.data.message || defaultMessage);
      }
    } else {
      message.error('Сервер недоступен');
    }
  };

  const columns = [
    { title: 'ID', dataIndex: 'id', key: 'id' },
    { title: 'Название', dataIndex: 'name', key: 'name' },
    { title: 'Новые', dataIndex: 'new', key: 'new' },
    { 
      title: 'Используемые', 
      dataIndex: 'used', 
      key: 'used',
      render: (used) => (
        <div>
          {used?.map((u, i) => (
            <div key={i}>{u.email}: {u.amount}</div>
          )) || 'Нет данных'}
        </div>
      )
    },
    { title: 'Сломанные', dataIndex: 'broken', key: 'broken' },
    {
      title: 'Действия',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            icon={<EditOutlined />}
            onClick={() => {
              const itemData = {
                ...record,
                used: record.used || []
              };
              editForm.setFieldsValue(itemData);
              setIsEditModalOpen(true);
            }}
          />
          <Button
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDeleteItem(record.id)}
          />
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: 20, maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 20 }}>
        <h2>Управление инвентарём</h2>
        <Button 
          type="primary" 
          onClick={() => navigate('/homeadmin')}
          style={{ marginLeft: 20 }}
        >
          На главную
        </Button>
      </div>

      <Table
        dataSource={items}
        columns={columns}
        pagination={{ pageSize: 10 }}
        bordered
        rowKey="id"
        locale={{ emptyText: 'Нет данных' }}
      />

      <Button
        type="primary"
        shape="circle"
        icon={<PlusOutlined />}
        onClick={() => setIsModalOpen(true)}
        style={{
          position: 'fixed',
          bottom: 50,
          right: 50,
          width: 56,
          height: 56,
          fontSize: 20
        }}
      />

      <Modal
        title="Добавить новый предмет"
        open={isModalOpen}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        confirmLoading={loading}
        okText="Добавить"
        cancelText="Отмена"
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleAddItem}>
          <Form.Item
            name="name"
            label="Название предмета"
            rules={[
              { required: true, whitespace: true, message: 'Введите название' },
              { max: 100, message: 'Максимум 100 символов' }
            ]}
          >
            <Input placeholder="Например: Футбольный мяч" />
          </Form.Item>

          <Form.Item
            name="amount"
            label="Количество новых единиц"
            rules={[
              { required: true, message: 'Введите количество' },
            ]}
          >
            <Input type="number" placeholder="Например: 5" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="Редактировать предмет"
        open={isEditModalOpen}
        width={600}
        onCancel={() => {
          setIsEditModalOpen(false);
          editForm.resetFields();
        }}
        onOk={() => editForm.submit()}
        confirmLoading={loading}
        okText="Сохранить"
        cancelText="Отмена"
        destroyOnClose
      >
        <Form form={editForm} layout="vertical" onFinish={handleUpdateItem}>
          <Form.Item name="id" hidden><Input /></Form.Item>
          
          <Form.Item
            name="name"
            label="Название"
            rules={[{ required: true, message: 'Введите название' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item
            name="new"
            label="Новые"
            rules={[{ required: true, message: 'Введите количество' }]}
          >
            <Input type="number" min={0} />
          </Form.Item>

          <Form.Item
            name="broken"
            label="Сломанные"
            rules={[{ required: true, message: 'Введите количество' }]}
          >
            <Input type="number" min={0} />
          </Form.Item>

          <Form.List name="used">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <Space key={key} style={{ display: 'flex', marginBottom: 8 }}>
                    <Form.Item
                      {...restField}
                      name={[name, 'email']}
                      rules={[{ required: true, message: 'Выберите пользователя' }]}
                    >
                      <Select placeholder="Пользователь" style={{ width: 200 }}>
                        {users.map(user => (
                          <Option key={user.email} value={user.email}>
                            {user.name} ({user.email})
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                    
                    <Form.Item
                      {...restField}
                      name={[name, 'amount']}
                      rules={[{ 
                        required: true, 
                        message: 'Введите количество',
                        type: 'number',
                        transform: value => Number(value)
                      }]}
                    >
                      <Input type="number" placeholder="Количество" min={1} />
                    </Form.Item>
                    
                    <CloseOutlined onClick={() => remove(name)} />
                  </Space>
                ))}
                
                <Button
                  type="dashed"
                  onClick={() => add()}
                  icon={<UserAddOutlined />}
                >
                  Добавить пользователя
                </Button>
              </>
            )}
          </Form.List>
        </Form>
      </Modal>
    </div>
  );
};

export default ItemsAdmin;