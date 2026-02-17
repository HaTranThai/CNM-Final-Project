import { Table, Button, Typography, Modal, Form, Input, Select, message, Tag } from 'antd';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getUsers, createUser, updateUser, deleteUser } from '../api/endpoints';
import { useState } from 'react';

const { Title } = Typography;

export default function AdminUsersPage() {
    const qc = useQueryClient();
    const [open, setOpen] = useState(false);
    const [form] = Form.useForm();
    const { data: users, isLoading } = useQuery({ queryKey: ['users'], queryFn: getUsers });

    const createMut = useMutation({
        mutationFn: createUser,
        onSuccess: () => { message.success('User created'); qc.invalidateQueries({ queryKey: ['users'] }); setOpen(false); form.resetFields(); },
    });

    const deleteMut = useMutation({
        mutationFn: deleteUser,
        onSuccess: () => { message.success('User deactivated'); qc.invalidateQueries({ queryKey: ['users'] }); },
    });

    const columns = [
        { title: 'Username', dataIndex: 'username' },
        { title: 'Display Name', dataIndex: 'display_name' },
        { title: 'Role', dataIndex: 'role_name', render: (r: string) => <Tag>{r}</Tag> },
        { title: 'Active', dataIndex: 'is_active', render: (v: boolean) => <Tag color={v ? 'green' : 'red'}>{v ? 'Yes' : 'No'}</Tag> },
        { title: 'Created', dataIndex: 'created_at', render: (t: string) => t?.slice(0, 19) },
        {
            title: 'Actions',
            render: (_: any, r: any) => (
                <Button size="small" danger onClick={() => deleteMut.mutate(r.user_id)}>Deactivate</Button>
            ),
        },
    ];

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
                <Title level={4} style={{ margin: 0 }}>User Management</Title>
                <Button type="primary" onClick={() => setOpen(true)}>Add User</Button>
            </div>
            <Table dataSource={users} columns={columns} rowKey="user_id" loading={isLoading} />
            <Modal title="Create User" open={open} onCancel={() => setOpen(false)} onOk={() => form.submit()} confirmLoading={createMut.isPending}>
                <Form form={form} layout="vertical" onFinish={(v) => createMut.mutate(v)}>
                    <Form.Item name="username" label="Username" rules={[{ required: true }]}><Input /></Form.Item>
                    <Form.Item name="password" label="Password" rules={[{ required: true }]}><Input.Password /></Form.Item>
                    <Form.Item name="display_name" label="Display Name"><Input /></Form.Item>
                    <Form.Item name="role_id" label="Role ID" rules={[{ required: true }]}><Input placeholder="UUID of the role" /></Form.Item>
                </Form>
            </Modal>
        </div>
    );
}
