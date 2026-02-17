import { Card, Form, InputNumber, Button, Typography, message, Row, Col, Divider } from 'antd';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getSettings, updateSettings } from '../api/endpoints';
import { useEffect } from 'react';

const { Title } = Typography;

export default function AdminSettingsPage() {
    const queryClient = useQueryClient();
    const [form] = Form.useForm();
    const { data: settings } = useQuery({ queryKey: ['settings'], queryFn: getSettings });

    useEffect(() => {
        if (settings) {
            const values: Record<string, any> = {};
            settings.forEach((s) => { values[s.key] = s.value; });
            form.setFieldsValue(values);
        }
    }, [settings, form]);

    const mutation = useMutation({
        mutationFn: updateSettings,
        onSuccess: () => { message.success('Settings updated'); queryClient.invalidateQueries({ queryKey: ['settings'] }); },
    });

    return (
        <div>
            <Title level={4} style={{ marginBottom: 16 }}>System Settings</Title>
            <Card>
                <Form form={form} layout="vertical" onFinish={(v) => mutation.mutate(v)}>
                    <Title level={5}>Inference</Title>
                    <Row gutter={16}>
                        <Col span={8}><Form.Item name="thr_A" label="A-Threshold"><InputNumber step={0.05} min={0} max={1} style={{ width: '100%' }} /></Form.Item></Col>
                    </Row>
                    <Divider />
                    <Title level={5}>V Alert Rules</Title>
                    <Row gutter={16}>
                        <Col span={8}><Form.Item name="V_WINDOW" label="Window (sec)"><InputNumber min={1} style={{ width: '100%' }} /></Form.Item></Col>
                        <Col span={8}><Form.Item name="V_THRESH" label="Threshold"><InputNumber min={1} style={{ width: '100%' }} /></Form.Item></Col>
                        <Col span={8}><Form.Item name="COOLDOWN_V" label="Cooldown (sec)"><InputNumber min={1} style={{ width: '100%' }} /></Form.Item></Col>
                    </Row>
                    <Divider />
                    <Title level={5}>A Alert Rules</Title>
                    <Row gutter={16}>
                        <Col span={8}><Form.Item name="A_WINDOW" label="Window (sec)"><InputNumber min={1} style={{ width: '100%' }} /></Form.Item></Col>
                        <Col span={8}><Form.Item name="A_THRESH" label="Threshold"><InputNumber min={1} style={{ width: '100%' }} /></Form.Item></Col>
                        <Col span={8}><Form.Item name="COOLDOWN_A" label="Cooldown (sec)"><InputNumber min={1} style={{ width: '100%' }} /></Form.Item></Col>
                    </Row>
                    <Form.Item style={{ marginTop: 16 }}>
                        <Button type="primary" htmlType="submit" loading={mutation.isPending} size="large">Save Settings</Button>
                    </Form.Item>
                </Form>
            </Card>
        </div>
    );
}
