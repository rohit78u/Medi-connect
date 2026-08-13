import { CONFIG } from './config.js';

class AppState {
  constructor() {
    this.user = JSON.parse(localStorage.getItem(CONFIG.USER_KEY)) || null;
    this.token = localStorage.getItem(CONFIG.TOKEN_KEY) || null;
    this.currentView = 'triage'; // 'triage', 'doctors', 'appointments', 'auth'
    this.listeners = [];
  }

  setUser(user, token, refreshToken) {
    this.user = user;
    this.token = token;

    if (user && token) {
      localStorage.setItem(CONFIG.USER_KEY, JSON.stringify(user));
      localStorage.setItem(CONFIG.TOKEN_KEY, token);
      if (refreshToken) localStorage.setItem(CONFIG.REFRESH_TOKEN_KEY, refreshToken);
    } else {
      localStorage.removeItem(CONFIG.USER_KEY);
      localStorage.removeItem(CONFIG.TOKEN_KEY);
      localStorage.removeItem(CONFIG.REFRESH_TOKEN_KEY);
    }
    this.notify();
  }

  setView(viewName) {
    this.currentView = viewName;
    this.notify();
  }

  getUserRole() {
    if (!this.user || !this.user.roles || this.user.roles.length === 0) return 'PATIENT';
    return this.user.roles[0].name.toUpperCase();
  }

  subscribe(listener) {
    this.listeners.push(listener);
  }

  notify() {
    this.listeners.forEach(fn => fn(this));
  }
}

export const state = new AppState();
