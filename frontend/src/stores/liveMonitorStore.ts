/**
 * Global Zustand store for Live Monitor state.
 * Keeps WebSocket connection + ECG data alive across page navigation.
 */
import { create } from 'zustand';

interface LiveMonitorState {
    /* ── connection ── */
    sessionId: string | null;
    connected: boolean;
    ws: WebSocket | null;

    /* ── data ── */
    waveformData: number[];
    lastWaveform: any;
    lastPrediction: any;
    alerts: any[];

    /* ── actions ── */
    setSessionId: (id: string | null) => void;
    connectWs: () => void;
    disconnectWs: () => void;
}

const WS_BASE = (import.meta as any).env?.VITE_WS_BASE_URL || `ws://${window.location.host}`;
const MAX_WAVEFORM_POINTS = 1800; // ~5 seconds at 360 Hz

export const useLiveMonitorStore = create<LiveMonitorState>((set, get) => ({
    sessionId: null,
    connected: false,
    ws: null,
    waveformData: [],
    lastWaveform: null,
    lastPrediction: null,
    alerts: [],

    setSessionId: (id) => {
        const prev = get().sessionId;
        if (prev === id) return;
        // Disconnect old, then reconnect with new session
        get().disconnectWs();
        set({ sessionId: id, waveformData: [], lastPrediction: null, alerts: [] });
        if (id) {
            // Small delay so state settles
            setTimeout(() => get().connectWs(), 50);
        }
    },

    connectWs: () => {
        const { sessionId, ws: existingWs } = get();
        if (!sessionId) return;
        if (existingWs && existingWs.readyState === WebSocket.OPEN) return;

        const token = localStorage.getItem('token') || '';
        const url = `${WS_BASE}/ws/live?session_id=${sessionId}&token=${token}`;
        const ws = new WebSocket(url);

        ws.onopen = () => {
            set({ connected: true });
            console.log('[LiveStore] WS connected to', sessionId);
        };

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                switch (msg.type) {
                    case 'waveform': {
                        const wf = msg.data;
                        if (wf.samples?.[0]) {
                            set((state) => {
                                const updated = [...state.waveformData, ...wf.samples[0]];
                                return {
                                    lastWaveform: wf,
                                    waveformData: updated.slice(-MAX_WAVEFORM_POINTS),
                                };
                            });
                        }
                        break;
                    }
                    case 'prediction':
                        set({ lastPrediction: msg.data });
                        break;
                    case 'alert':
                        set((state) => ({
                            alerts: [msg.data, ...state.alerts].slice(0, 50),
                        }));
                        break;
                }
            } catch (e) {
                console.error('[LiveStore] WS parse error:', e);
            }
        };

        ws.onclose = () => {
            set({ connected: false, ws: null });
            // Auto-reconnect after 3s if session is still selected
            setTimeout(() => {
                const current = get();
                if (current.sessionId && !current.ws) {
                    current.connectWs();
                }
            }, 3000);
        };

        ws.onerror = () => ws.close();

        set({ ws });
    },

    disconnectWs: () => {
        const { ws } = get();
        if (ws) {
            ws.onclose = null; // prevent auto-reconnect
            ws.close();
        }
        set({ ws: null, connected: false });
    },
}));
