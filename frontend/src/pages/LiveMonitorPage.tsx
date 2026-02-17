import { useEffect } from 'react';
import { Row, Col, Card, Typography, Tag, Space, Badge, Select, Statistic, Progress } from 'antd';
import { HeartOutlined, ThunderboltOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { useQuery } from '@tanstack/react-query';
import { getSessions } from '../api/endpoints';
import { useLiveMonitorStore } from '../stores/liveMonitorStore';
import type { WSPredictionData, WSWaveformData } from '../types/ws';

const { Title, Text } = Typography;

export default function LiveMonitorPage() {
    const { data: sessions } = useQuery({ queryKey: ['sessions'], queryFn: getSessions });

    // Global store — survives page navigation
    const {
        sessionId: selectedSession,
        setSessionId: setSelectedSession,
        connected,
        waveformData,
        lastWaveform,
        lastPrediction,
        alerts,
    } = useLiveMonitorStore();

    // Auto-select first running session (only if none selected yet)
    useEffect(() => {
        if (sessions && sessions.length > 0 && !selectedSession) {
            const running = sessions.find((s) => s.status === 'RUNNING');
            if (running) setSelectedSession(running.session_id);
            else setSelectedSession(sessions[0].session_id);
        }
    }, [sessions, selectedSession, setSelectedSession]);

    const pred = lastPrediction as WSPredictionData | null;
    const sqi = (lastWaveform as WSWaveformData)?.sqi ?? 1.0;

    const chartOption = {
        animation: false,
        grid: { top: 20, right: 20, bottom: 30, left: 50 },
        xAxis: { type: 'category' as const, show: false, data: waveformData.map((_: number, i: number) => i) },
        yAxis: { type: 'value' as const, show: false },
        series: [
            {
                type: 'line' as const,
                data: waveformData,
                smooth: false,
                symbol: 'none',
                lineStyle: { color: '#00d4aa', width: 1.5 },
                areaStyle: { color: 'rgba(0, 212, 170, 0.05)' },
            },
        ],
        backgroundColor: 'transparent',
    };

    return (
        <div>
            <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
                <Col span={12}>
                    <Title level={4} style={{ margin: 0 }}>
                        <HeartOutlined style={{ marginRight: 8, color: '#00d4aa' }} />
                        Live ECG Monitor
                    </Title>
                </Col>
                <Col span={12} style={{ textAlign: 'right' }}>
                    <Space>
                        <Badge status={connected ? 'success' : 'error'} text={connected ? 'Connected' : 'Disconnected'} />
                        <Select
                            placeholder="Select session"
                            value={selectedSession}
                            onChange={setSelectedSession}
                            style={{ width: 280 }}
                            options={sessions?.map((s) => ({
                                value: s.session_id,
                                label: `${s.record_name || s.session_id.slice(0, 8)} — ${s.status}`,
                            }))}
                        />
                    </Space>
                </Col>
            </Row>

            {/* ECG Waveform */}
            <Card className="ecg-monitor-container" style={{ marginBottom: 16 }}>
                <ReactECharts option={chartOption} style={{ height: 280 }} notMerge />
            </Card>

            <Row gutter={[16, 16]}>
                {/* Prediction Badge */}
                <Col xs={24} md={8}>
                    <Card style={{ textAlign: 'center' }}>
                        <Text style={{ color: '#9ca3af', fontSize: 12, textTransform: 'uppercase', letterSpacing: 1 }}>
                            Current Prediction
                        </Text>
                        <div style={{ margin: '16px 0' }}>
                            {pred ? (
                                <div className={`pred-badge pred-${pred.pred_class}`} style={{ display: 'inline-flex', fontSize: 24 }}>
                                    <ThunderboltOutlined />
                                    {pred.pred_class === 'N' ? 'Normal' : pred.pred_class === 'A' ? 'PAC (Atrial)' : 'PVC (Ventricular)'}
                                </div>
                            ) : (
                                <Tag color="default" style={{ fontSize: 18, padding: '8px 24px' }}>Waiting...</Tag>
                            )}
                        </div>
                        {pred && (
                            <Statistic
                                title="Confidence"
                                value={(pred.confidence * 100).toFixed(1)}
                                suffix="%"
                                valueStyle={{ color: '#00d4aa', fontSize: 20 }}
                            />
                        )}
                    </Card>
                </Col>

                {/* Signal Quality */}
                <Col xs={24} md={8}>
                    <Card style={{ textAlign: 'center' }}>
                        <Text style={{ color: '#9ca3af', fontSize: 12, textTransform: 'uppercase', letterSpacing: 1 }}>
                            Signal Quality (SQI)
                        </Text>
                        <div style={{ margin: '24px 0' }}>
                            <Progress
                                type="circle"
                                percent={Math.round(sqi * 100)}
                                strokeColor={sqi > 0.7 ? '#22c55e' : sqi > 0.4 ? '#f59e0b' : '#ef4444'}
                                trailColor="rgba(255,255,255,0.05)"
                                size={100}
                            />
                        </div>
                    </Card>
                </Col>

                {/* Active Alerts */}
                <Col xs={24} md={8}>
                    <Card>
                        <Text style={{ color: '#9ca3af', fontSize: 12, textTransform: 'uppercase', letterSpacing: 1 }}>
                            Active Alerts
                        </Text>
                        <div style={{ marginTop: 16, maxHeight: 200, overflow: 'auto' }}>
                            {alerts.length === 0 ? (
                                <Text style={{ color: '#6b7280' }}>No active alerts</Text>
                            ) : (
                                alerts.slice(0, 5).map((a: any, i: number) => (
                                    <div
                                        key={i}
                                        style={{
                                            padding: '8px 12px',
                                            marginBottom: 8,
                                            borderRadius: 8,
                                            background: a.alert_type === 'V' ? 'rgba(239,68,68,0.1)' : 'rgba(245,158,11,0.1)',
                                            border: `1px solid ${a.alert_type === 'V' ? 'rgba(239,68,68,0.3)' : 'rgba(245,158,11,0.3)'}`,
                                        }}
                                    >
                                        <Tag color={a.alert_type === 'V' ? 'red' : 'orange'}>{a.alert_type} Alert</Tag>
                                        <Text style={{ fontSize: 12 }}>Severity: {((a.severity || 0) * 100).toFixed(0)}%</Text>
                                    </div>
                                ))
                            )}
                        </div>
                    </Card>
                </Col>
            </Row>
        </div>
    );
}
