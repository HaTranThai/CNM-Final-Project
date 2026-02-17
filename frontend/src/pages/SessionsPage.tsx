import { Table, Tag, Button, Typography } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { getSessions } from '../api/endpoints';
import type { Session } from '../types/domain';

const { Title } = Typography;

export default function SessionsPage() {
    const navigate = useNavigate();
    const { data: sessions, isLoading } = useQuery({
        queryKey: ['sessions'],
        queryFn: getSessions,
        refetchInterval: 10000,
    });

    const columns = [
        {
            title: 'Record',
            dataIndex: 'record_name',
            render: (v: string, r: Session) => v || r.session_id.slice(0, 8),
        },
        {
            title: 'Status',
            dataIndex: 'status',
            render: (s: string) => (
                <span>
                    <span className={`status-dot ${s === 'RUNNING' ? 'running' : 'stopped'}`} />
                    {s}
                </span>
            ),
        },
        { title: 'Start', dataIndex: 'start_time', render: (t: string) => t?.slice(0, 19) },
        { title: 'End', dataIndex: 'end_time', render: (t: string) => t?.slice(0, 19) || '—' },
        { title: 'Source', dataIndex: 'source_type' },
        {
            title: '',
            render: (_: any, r: Session) => (
                <Button size="small" type="link" onClick={() => navigate(`/sessions/${r.session_id}`)}>
                    View
                </Button>
            ),
        },
    ];

    return (
        <div>
            <Title level={4} style={{ marginBottom: 16 }}>Sessions</Title>
            <Table dataSource={sessions} columns={columns} rowKey="session_id" loading={isLoading} pagination={{ pageSize: 20 }} />
        </div>
    );
}
