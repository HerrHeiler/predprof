import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout, Button, Card, Space, Typography, theme } from 'antd';
import { 
  LogoutOutlined, 
  ToolOutlined, 
  ShoppingCartOutlined, 
  FileTextOutlined 
} from '@ant-design/icons';

const { Content, Header } = Layout;
const { Title } = Typography;

const HomePageUser = () => {
  const navigate = useNavigate();
  const { token: { colorBgContainer, borderRadiusLG } } = theme.useToken();

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    const role = localStorage.getItem('userRole');
    const email = localStorage.getItem("userEmail")
  })

  const handleNavigation = (path) => navigate(path);

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userEmail');
    navigate('/login');
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: colorBgContainer,
        padding: '0 24px'
      }}>
        <Title level={3} style={{ margin: 0 }}>Пользовательская Панель</Title>
        <Button
          type="primary"
          danger
          icon={<LogoutOutlined />}
          onClick={handleLogout}
        >
          Выйти
        </Button>
      </Header>
      
      <Content style={{ padding: '24px 50px', marginTop: 20 }}>
        <div style={{ 
          background: colorBgContainer, 
          minHeight: 280, 
          padding: 24,
          borderRadius: borderRadiusLG 
        }}>
          <Card title="Упралвние" bordered={false}>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <Button
                type="primary"
                size="large"
                block
                icon={<ToolOutlined />}
                onClick={() => handleNavigation('/itemsuser')}
                style={{ height: 60, fontSize: 16 }}
              >
                Создание заявок на инвентарь
              </Button>
            </Space>
          </Card>
        </div>
      </Content>
    </Layout>
  );
};

export default HomePageUser;