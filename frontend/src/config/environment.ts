// Configurações de Ambiente
// ========================

export const config = {
  // URL da API
  API_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  
  // Configurações de desenvolvimento
  ENVIRONMENT: process.env.REACT_APP_ENVIRONMENT || 'development',
  VERSION: process.env.REACT_APP_VERSION || '2.0.0',
  
  // Configurações de timeout
  API_TIMEOUT: parseInt(process.env.REACT_APP_API_TIMEOUT || '30000'),
  
  // Configurações de upload
  MAX_FILE_SIZE: parseInt(process.env.REACT_APP_MAX_FILE_SIZE || '10485760'), // 10MB
  ALLOWED_IMAGE_TYPES: (process.env.REACT_APP_ALLOWED_IMAGE_TYPES || 'image/jpeg,image/png,image/bmp,image/gif').split(','),
  ALLOWED_VIDEO_TYPES: (process.env.REACT_APP_ALLOWED_VIDEO_TYPES || 'video/mp4,video/avi,video/mov,video/mpeg').split(','),
  
  // Configurações de confiança
  DEFAULT_CONFIDENCE_THRESHOLD: parseFloat(process.env.REACT_APP_DEFAULT_CONFIDENCE_THRESHOLD || '0.5'),
  MIN_CONFIDENCE_THRESHOLD: parseFloat(process.env.REACT_APP_MIN_CONFIDENCE_THRESHOLD || '0.1'),
  MAX_CONFIDENCE_THRESHOLD: parseFloat(process.env.REACT_APP_MAX_CONFIDENCE_THRESHOLD || '1.0'),
};

export default config;
