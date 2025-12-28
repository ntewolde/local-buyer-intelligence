/**
 * Authentication Service
 */
import api from './api';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface User {
  id: string;
  email: string;
  role: string;
  client_id?: string;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export const authService = {
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    // OAuth2 compatible format
    const params = new URLSearchParams();
    params.append('username', credentials.email);
    params.append('password', credentials.password);

    const response = await api.post('/api/v1/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    const tokenData = response.data;
    localStorage.setItem('access_token', tokenData.access_token);
    return tokenData;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/api/v1/auth/me');
    return response.data;
  },

  logout(): void {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },
};

