// Serviço de integração com a API de Visão Computacional
// =====================================================

import axios from 'axios';
import {
  LoginRequest,
  LoginResponse,
  HealthResponse,
  SignalPlateRequest,
  SignalPlateResponse,
  VehiclePlateRequest,
  VehiclePlateResponse,
  GeneralDetectionRequest,
  GeneralDetectionResponse,
  ModelsResponse,
  MonitoringStatus,
  UserProfile,
  ApiError
} from '../types/api';

class ApiService {
  private api: any;
  private token: string | null = null;

  constructor() {
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_URL || '',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para adicionar token de autenticação
    this.api.interceptors.request.use(
      (config: any) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error: any) => {
        return Promise.reject(error);
      }
    );

    // Interceptor para tratar respostas
    this.api.interceptors.response.use(
      (response: any) => {
        return response;
      },
      (error: any) => {
        if (error.response?.status === 401) {
          this.clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );

    // Carregar token do localStorage
    this.loadToken();
  }

  private loadToken(): void {
    const token = localStorage.getItem('auth_token');
    if (token) {
      this.token = token;
    }
  }

  public setToken(token: string): void {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  public clearToken(): void {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  public isAuthenticated(): boolean {
    return !!this.token;
  }

  // Autenticação
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await this.api.post('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    if (response.data.access_token) {
      this.setToken(response.data.access_token);
    }

    return response.data;
  }

  async logout(): Promise<void> {
    this.clearToken();
  }

  async getProfile(): Promise<UserProfile> {
    const response = await this.api.get('/api/v1/auth/profile');
    return response.data;
  }

  // Health Check
  async getHealth(): Promise<HealthResponse> {
    const response = await this.api.get('/health');
    return response.data;
  }

  // Modelos
  async getModels(): Promise<ModelsResponse> {
    const response = await this.api.get('/vision/models');
    return response.data;
  }

  // Detecção de Placas de Sinalização
  async detectSignalPlates(request: SignalPlateRequest): Promise<SignalPlateResponse> {
    const response = await this.api.post(
      '/api/v1/vision/detect/signal-plates',
      request
    );
    return response.data;
  }

  // Detecção de Placas de Veículos
  async detectVehiclePlates(request: VehiclePlateRequest): Promise<VehiclePlateResponse> {
    const response = await this.api.post(
      '/api/v1/vision/detect/vehicle-plates',
      request
    );
    return response.data;
  }

  // Detecção Geral
  async detectGeneral(request: GeneralDetectionRequest): Promise<GeneralDetectionResponse> {
    const response = await this.api.post(
      '/api/v1/vision/detect/general',
      request
    );
    return response.data;
  }

  // Monitoramento
  async getMonitoringStatus(): Promise<MonitoringStatus> {
    const response = await this.api.get('/api/v1/monitoring/status');
    return response.data;
  }

  // Utilitários
  async uploadFile(file: File): Promise<string> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.api.post('/api/v1/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data.file_id;
  }

  // Converter arquivo para base64
  fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        const result = reader.result as string;
        // Remove o prefixo data:image/...;base64,
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = (error) => reject(error);
    });
  }
}

// Instância singleton
export const apiService = new ApiService();
export default apiService;
