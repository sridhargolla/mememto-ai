import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(null);

// Decode JWT payload without verifying signature (for expiry check only)
function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const json = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(json);
  } catch {
    return null;
  }
}

function isTokenExpired(token) {
  const payload = parseJwt(token);
  if (!payload || !payload.exp) return true;
  // exp is in seconds; add a 10-second buffer
  return Date.now() >= (payload.exp - 10) * 1000;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');
    setToken(null);
    setUser(null);
    navigate('/login');
  }, [navigate]);

  useEffect(() => {
    const storedToken = localStorage.getItem('token') || sessionStorage.getItem('token');
    const storedUser  = localStorage.getItem('user') || sessionStorage.getItem('user');

    if (storedToken && storedUser) {
      if (isTokenExpired(storedToken)) {
        // Token has expired — clear and redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('user');
      } else {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      }
    }
    setLoading(false);
  }, []);

  const login = (tokenData, userData, rememberMe = true) => {
    // Always persist to localStorage so all pages can access the token directly
    localStorage.setItem('token', tokenData);
    localStorage.setItem('user', JSON.stringify(userData));
    if (rememberMe) {
      sessionStorage.setItem('token', tokenData);
      sessionStorage.setItem('user', JSON.stringify(userData));
    }
    setToken(tokenData);
    setUser(userData);
  };

  const isAuthenticated = () => !!token && !!user;

  // Global fetch wrapper that auto-logs out on 401 from any API call
  const authFetch = useCallback(async (url, options = {}) => {
    const tok = localStorage.getItem('token');
    const headers = {
      ...(options.headers || {}),
      ...(tok ? { Authorization: `Bearer ${tok}` } : {}),
    };
    const res = await fetch(url, { ...options, headers });
    if (res.status === 401) {
      logout();
      throw new Error('Session expired. Please log in again.');
    }
    return res;
  }, [logout]);

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated, loading, authFetch }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
