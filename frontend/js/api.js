import { CONFIG } from './config.js';

export class ApiError extends Error {
  constructor(message, statusCode, errors = []) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.errors = errors;
  }
}

class ApiClient {
  constructor() {
    this.baseUrl = CONFIG.API_BASE_URL;
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    const token = localStorage.getItem(CONFIG.TOKEN_KEY);
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...(options.headers || {})
      }
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        // Auto-Refresh Token attempt on 401
        if (response.status === 401 && !endpoint.includes('/auth/refresh') && !endpoint.includes('/auth/login')) {
          const refreshed = await this.refreshToken();
          if (refreshed) {
            return this.request(endpoint, options);
          }
        }

        const errorMessage = data.message || `HTTP Error ${response.status}`;
        const errors = data.errors || [];
        throw new ApiError(errorMessage, response.status, errors);
      }

      return data;
    } catch (err) {
      if (err instanceof ApiError) throw err;
      throw new ApiError(err.message || 'Network connection failed', 0);
    }
  }

  async refreshToken() {
    const refreshTokenStr = localStorage.getItem(CONFIG.REFRESH_TOKEN_KEY);
    if (!refreshTokenStr) return false;

    try {
      const res = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshTokenStr })
      });

      if (res.ok) {
        const payload = await res.json();
        localStorage.setItem(CONFIG.TOKEN_KEY, payload.data.access_token);
        localStorage.setItem(CONFIG.REFRESH_TOKEN_KEY, payload.data.refresh_token);
        return true;
      }
    } catch {
      localStorage.removeItem(CONFIG.TOKEN_KEY);
      localStorage.removeItem(CONFIG.REFRESH_TOKEN_KEY);
    }
    return false;
  }

  // HTTP Helpers
  get(endpoint) { return this.request(endpoint, { method: 'GET' }); }
  post(endpoint, body) { return this.request(endpoint, { method: 'POST', body: JSON.stringify(body) }); }
  put(endpoint, body) { return this.request(endpoint, { method: 'PUT', body: JSON.stringify(body) }); }
  patch(endpoint, body) { return this.request(endpoint, { method: 'PATCH', body: JSON.stringify(body) }); }
  delete(endpoint) { return this.request(endpoint, { method: 'DELETE' }); }
}

export const api = new ApiClient();
