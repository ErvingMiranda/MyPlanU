import React, { createContext, useState, useEffect, useContext } from 'react';
import { hasAuthToken, storeAuthSession, clearAuthSession } from './session';

interface AuthContextData {
  isLoggedIn: boolean;
  login: (token: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextData>({} as AuthContextData);

export const AuthProvider: React.FC = ({ children }) => {
  const [isLoggedIn, setLoggedIn] = useState(false);
  const [isLoading, setLoading] = useState(true);

  useEffect(() => {
    const checkToken = async () => {
      try {
        const tokenExists = await hasAuthToken();
        setLoggedIn(tokenExists);
      } finally {
        setLoading(false);
      }
    };
    checkToken();
  }, []);

  const login = async (token: string) => {
    await storeAuthSession(token);
    setLoggedIn(true);
  };

  const logout = async () => {
    await clearAuthSession();
    setLoggedIn(false);
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);