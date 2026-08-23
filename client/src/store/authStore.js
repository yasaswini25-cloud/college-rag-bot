import { useState, useEffect } from 'react';
import api from '../services/api';

let globalUser = null;
let globalToken = null;
const listeners = new Set();

try {
  const savedToken = localStorage.getItem('token');
  const savedUser = localStorage.getItem('user');
  if (savedToken) globalToken = savedToken;
  if (savedUser) globalUser = JSON.parse(savedUser);
} catch (e) {
  console.error("Failed to load initial auth state:", e);
}

function notify() {
  listeners.forEach((listener) => listener({ user: globalUser, token: globalToken, isAuthenticated: !!globalToken }));
}

export function useAuth() {
  const [state, setState] = useState({
    user: globalUser,
    token: globalToken,
    isAuthenticated: !!globalToken,
    loading: false
  });

  useEffect(() => {
    const listener = (newState) => setState((prev) => ({ ...prev, ...newState }));
    listeners.add(listener);
    return () => listeners.delete(listener);
  }, []);

  const login = async (email, password) => {
    setState((s) => ({ ...s, loading: true }));
    try {
      const res = await api.post('/auth/login', { email, password });
      const { user, token } = res.data;
      globalUser = user;
      globalToken = token;
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      notify();
      return { success: true, user };
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed. Please check your credentials.';
      return { success: false, error: msg };
    } finally {
      setState((s) => ({ ...s, loading: false }));
    }
  };

  const register = async (name, email, password, role = 'STUDENT') => {
    setState((s) => ({ ...s, loading: true }));
    try {
      const res = await api.post('/auth/register', { name, email, password, role });
      const { user, token } = res.data;
      globalUser = user;
      globalToken = token;
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      notify();
      return { success: true, user };
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed.';
      return { success: false, error: msg };
    } finally {
      setState((s) => ({ ...s, loading: false }));
    }
  };

  const logout = () => {
    globalUser = null;
    globalToken = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    notify();
  };

  return {
    ...state,
    login,
    register,
    logout,
    isAdmin: globalUser?.role === 'ADMIN'
  };
}
