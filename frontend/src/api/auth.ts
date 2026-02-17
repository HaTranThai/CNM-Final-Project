/** Auth API */
import http from './http';
import type { UserProfile } from '../types/domain';

export const login = async (username: string, password: string) => {
    const res = await http.post('/api/auth/login', { username, password });
    return res.data as { access_token: string; token_type: string };
};

export const getMe = async () => {
    const res = await http.get('/api/auth/me');
    return res.data as UserProfile;
};
