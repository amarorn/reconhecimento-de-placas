// Tipos para integração com a API de Visão Computacional
// =====================================================

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  username: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  uptime: number;
  components: {
    api: string;
    database: string;
    cache: string;
  };
  memory_usage: number;
  cpu_usage: number;
}

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Detection {
  class_name: string;
  confidence: number;
  bbox: BoundingBox;
}

export interface SignalPlateRequest {
  image: string; // base64
  confidence_threshold?: number;
}

export interface SignalPlateResponse {
  success: boolean;
  message: string;
  timestamp: string;
  image_id: string;
  detections: Detection[];
  total_detections: number;
}

export interface VehiclePlateRequest {
  image: string; // base64
  confidence_threshold?: number;
}

export interface VehiclePlateResponse {
  success: boolean;
  message: string;
  timestamp: string;
  image_id: string;
  detections: Detection[];
  total_vehicles: number;
  total_plates: number;
}

export interface GeneralDetectionRequest {
  image: string; // base64
  confidence_threshold?: number;
}

export interface GeneralDetectionResponse {
  success: boolean;
  message: string;
  timestamp: string;
  image_id: string;
  detections: Detection[];
  total_detections: number;
}

export interface ModelInfo {
  name: string;
  description: string;
  model_path: string;
  status: string;
}

export interface ModelsResponse {
  models: {
    vehicle_detector: ModelInfo;
    signal_detector: ModelInfo;
    pothole_detector: ModelInfo;
  };
  timestamp: string;
}

export interface MonitoringStatus {
  pipeline_status: string;
  active_models: number;
  total_requests: number;
  success_rate: number;
  average_processing_time: number;
  memory_usage: number;
  cpu_usage: number;
  timestamp: string;
}

export interface UserProfile {
  username: string;
  email?: string;
  role: string;
  created_at: string;
  last_login: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}
