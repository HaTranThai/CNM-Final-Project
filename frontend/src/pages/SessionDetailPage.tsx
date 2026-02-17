import { useParams } from 'react-router-dom';
import { Card, Table, Tag, Typography, Row, Col, Statistic, Descriptions } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { getSession, getSessionPredictions, getSessionAlerts } from '../api/endpoints';

const { Title } = Typography;

export default function SessionDetailPage() {
    const { id } = useParams<{ id: string }>();

    const { data: session } = useQuery({ queryKey: ['session', id], queryFn: () => getSession(id!) });
    const { data: predictions } = useQuery({ queryKey: ['predictions', id], queryFn: () => getSessionPredictions(id!) });
    const { data: alerts } = useQuery({ queryKey: ['sessionAlerts', id], queryFn: () => getSessionAlerts(id!) });

    const predColumns = [
        { title: 'Time (s)', dataIndex: 'beat_ts_sec', render: (v: number) => v?.toFixed(2) },
        {
            title: 'Class',
            dataIndex: 'pred_class',
            render: (c: string) => <Tag color={c === 'V' ? 'red' : c === 'A' ? 'orange' : 'green'}>{c}</Tag>,
        },
        { title: 'Confidence', dataIndex: 'confidence', render: (v: number) => `${((v || 0) * 100).toFixed(1)}%` },
        { title: 'pA', dataIndex: 'p_a', render: (v: number) => v?.toFixed(3) },
    ];

    const alertColumns = [
        { title: 'Type', dataIndex: 'alert_type', render: (t: string) => <Tag color={t === 'V' ? 'red' : 'orange'}>{t}</Tag> },
        { title: 'Status', dataIndex: 'status', render: (s: string) => <Tag>{s}</Tag> },
        { title: 'Severity', dataIndex: 'severity', render: (v: number) => `${((v || 0) * 100).toFixed(0)}%` },
        { title: 'Time', dataIndex: 'start_time', render: (t: string) => t?.slice(0, 19) },
    ];

    return (
        <div>
            <Title level={4} style={{ marginBottom: 16 }}>Session Detail</Title>

            {session && (
                <Card style={{ marginBottom: 16 }}>
                    <Descriptions column={3}>
                        <Descriptions.Item label="Session ID">{session.session_id.slice(0, 12)}…</Descriptions.Item>
                        <Descriptions.Item label="Record">{session.record_name}</Descriptions.Item>
                        <Descriptions.Item label="Status">
                            <span className={`status-dot ${session.status === 'RUNNING' ? 'running' : 'stopped'}`} />
                            {session.status}
                        </Descriptions.Item>
                        <Descriptions.Item label="Start">{session.start_time?.slice(0, 19)}</Descriptions.Item>
                        <Descriptions.Item label="End">{session.end_time?.slice(0, 19) || '—'}</Descriptions.Item>
                        <Descriptions.Item label="Source">{session.source_type}</Descriptions.Item>
                    </Descriptions>
                </Card>
            )}

            <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
                <Col span={8}>
                    <Card><Statistic title="Total Predictions" value={predictions?.length || 0} /></Card>
                </Col>
                <Col span={8}>
                    <Card><Statistic title="Alerts" value={alerts?.length || 0} valueStyle={{ color: '#ef4444' }} /></Card>
                </Col>
                <Col span={8}>
                    <Card><Statistic title="Arrhythmia Rate" value={predictions ? ((predictions.filter(p => p.pred_class !== 'N').length / Math.max(predictions.length, 1)) * 100).toFixed(1) : 0} suffix="%" /></Card>
                </Col>
            </Row>

            <Card title="Alerts" style={{ marginBottom: 16 }}>
                <Table dataSource={alerts} columns={alertColumns} rowKey="alert_id" pagination={{ pageSize: 10 }} size="small" />
            </Card>

            <Card title="Recent Predictions">
                <Table dataSource={predictions?.slice(0, 100)} columns={predColumns} rowKey="pred_id" pagination={{ pageSize: 20 }} size="small" />
            </Card>
        </div>
    );
}
