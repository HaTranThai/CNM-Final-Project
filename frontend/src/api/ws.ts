/** WebSocket client wrapper */
import { useEffect, useRef, useCallback, useState } from 'react';
import type { WSMessage } from '../types/ws';

const WS_BASE = import.meta.env.VITE_WS_BASE_URL || `ws://${window.location.host}`;

export function useWebSocket(sessionId: string | null) {
    const wsRef = useRef<WebSocket | null>(null);
    const [connected, setConnected] = useState(false);
    const [lastWaveform, setLastWaveform] = useState<any>(null);
    const [lastPrediction, setLastPrediction] = useState<any>(null);
    const [alerts, setAlerts] = useState<any[]>([]);

    const connect = useCallback(() => {
        if (!sessionId) return;
        const token = localStorage.getItem('token') || '';
        const url = `${WS_BASE}/ws/live?session_id=${sessionId}&token=${token}`;

        const ws = new WebSocket(url);

        ws.onopen = () => {
            setConnected(true);
            console.log('WS connected to', sessionId);
        };

        ws.onmessage = (event) => {
            try {
                const msg: WSMessage = JSON.parse(event.data);
                switch (msg.type) {
                    case 'waveform':
                        setLastWaveform(msg.data);
                        break;
                    case 'prediction':
                        setLastPrediction(msg.data);
                        break;
                    case 'alert':
                        setAlerts((prev) => [msg.data, ...prev].slice(0, 50));
                        break;
                }
            } catch (e) {
                console.error('WS parse error:', e);
            }
        };

        ws.onclose = () => {
            setConnected(false);
            // Auto-reconnect after 3 seconds
            setTimeout(() => connect(), 3000);
        };

        ws.onerror = () => {
            ws.close();
        };

        wsRef.current = ws;
    }, [sessionId]);

    useEffect(() => {
        connect();
        return () => wsRef.current?.close();
    }, [connect]);

    return { connected, lastWaveform, lastPrediction, alerts };
}
