/** WebSocket message types */
export interface WSMessage {
    type: 'waveform' | 'prediction' | 'alert';
    data: any;
}

export interface WSWaveformData {
    session_id: string;
    ts_start: string;
    fs: number;
    lead: string[];
    samples: number[][];
    sqi: number;
}

export interface WSPredictionData {
    session_id: string;
    beat_ts_sec: number;
    pred_class: string;
    confidence: number;
    pA: number;
    probs: Record<string, number>;
    gated_A: boolean;
}

export interface WSAlertData {
    alert_id: string;
    session_id: string;
    alert_type: string;
    status: string;
    severity: number;
    evidence: Record<string, any>;
}
