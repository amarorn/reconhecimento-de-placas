// Contexto de Autenticação
// =======================

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { LoginRequest, LoginResponse, UserProfile } from '../types/api';
import apiService from '../services/api';

interface AuthContextType {
  isAuthenticated: boolean;
  user: UserProfile | null;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  loading: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (apiService.isAuthenticated()) {
          setIsAuthenticated(true);
          // Tentar carregar perfil do usuário
          try {
            const userProfile = await apiService.getProfile();
            setUser(userProfile);
          } catch (err) {
            console.warn('Não foi possível carregar perfil do usuário:', err);
          }
        }
      } catch (err) {
        console.error('Erro ao inicializar autenticação:', err);
        apiService.clearToken();
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (credentials: LoginRequest): Promise<void> => {
    try {
      setLoading(true);
      setError(null);

      const response: LoginResponse = await apiService.login(credentials);
      
      setIsAuthenticated(true);
      
      // Criar perfil básico do usuário
      const userProfile: UserProfile = {
        username: response.username,
        role: 'user',
        created_at: new Date().toISOString(),
        last_login: new Date().toISOString(),
      };
      
      setUser(userProfile);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Erro ao fazer login';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const logout = (): void => {
    apiService.logout();
    setIsAuthenticated(false);
    setUser(null);
    setError(null);
  };

  const value: AuthContextType = {
    isAuthenticated,
    user,
    login,
    logout,
    loading,
    error,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};
