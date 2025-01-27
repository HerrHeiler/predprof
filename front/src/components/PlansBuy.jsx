import React, { useState } from "react";
import { Table, Button, Modal, Form, Input, InputNumber, DatePicker, Typography } from "antd";


const { Title } = Typography;
const { TextArea } = Input;

const PlansBuy = () => {
  const [data, setData] = useState([]); // Список запросов
  const [isModalOpen, setIsModalOpen] = useState(false); // Состояние модального окна

  const [form] = Form.useForm();

  const handleAdd = () => {
    form
      .validateFields()
      .then((values) => {
        const newData = {
          key: data.length + 1,
          text: values.text,
          items: values.items,
          amounts: values.amounts,
          prices: values.prices,
          deadline: values.deadline.format("YYYY-MM-DD"),
        };
        setData([...data, newData]);
        setIsModalOpen(false);
        form.resetFields();
      })
      .catch((info) => {
        console.log("Validation Failed:", info);
      });
  };

  const columns = [
    {
      title: "Описание",
      dataIndex: "text",
      key: "text",
    },
    {
      title: "Предметы",
      dataIndex: "items",
      key: "items",
    },
    {
      title: "Количество",
      dataIndex: "amounts",
      key: "amounts",
    },
    {
      title: "Цена",
      dataIndex: "prices",
      key: "prices",
    },
  ];

  return (
    <div style={{ padding: "20px" }}>
      <Title level={2}>Запросы на закупки</Title>

      <Table dataSource={data} columns={columns} pagination={{ pageSize: 5 }} />

      <Button
        type="primary"
        shape="circle"
        onClick={() => setIsModalOpen(true)}
        style={{ position: "fixed", bottom: "20px", right: "20px" }}
      >
        +
      </Button>

      <Modal
        title="Создать новый запрос"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={handleAdd}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="Описание"
            name="text"
            rules={[{ required: true, message: "Введите описание" }]}
          >
            <TextArea rows={3} placeholder="Описание запроса" />
          </Form.Item>

          <Form.Item
            label="Предметы"
            name="items"
            rules={[{ required: true, message: "Введите предметы" }]}
          >
            <Input placeholder="Введите названия предметов через запятую" />
          </Form.Item>

          <Form.Item
            label="Количество (через запятую)"
            name="amounts"
            rules={[{ required: true, message: "Введите количество" }]}
          >
            <Input placeholder="Введите количество через запятую" />
          </Form.Item>

          <Form.Item
            label="Цены (через запятую)"
            name="prices"
            rules={[{ required: true, message: "Введите цены" }]}
          >
            <Input placeholder="Введите цены через запятую" />
          </Form.Item>

        </Form>
      </Modal>
    </div>
  );
};

export default PlansBuy;
