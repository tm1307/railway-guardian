import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('rg_token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      // Decode JWT to get user info (without verification - verification is server-side)
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUser({
          username: payload.sub,
          role: payload.role || 'viewer',
        });
      } catch {
        logout();
      }
    }
    setLoading(false);
  }, [token]);

  const login = (accessToken, userInfo) => {
    localStorage.setItem('rg_token', accessToken);
    localStorage.setItem('rg_user', JSON.stringify(userInfo));
    setToken(accessToken);
    setUser(userInfo);
  };

  const logout = () => {
    localStorage.removeItem('rg_token');
    localStorage.removeItem('rg_user');
    setToken(null);
    setUser(null);
  };

  const hasRole = (...roles) => user && roles.includes(user.role);

  return (
    <AuthContext.Provider value={{ user, token, login, logout, hasRole, loading, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
export default AuthContext;
