// Página Principal de Análise
// ==========================

import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Button,
  Tabs,
  Tab,
  Alert,
  Card,
  CardContent,
  Chip,
  Divider,
} from '@mui/material';
import {
  CloudUpload,
  Visibility,
  Speed,
  Security,
} from '@mui/icons-material';
import FileUpload from '../components/FileUpload';
import ResultsDisplay from '../components/ResultsDisplay';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';
import {
  SignalPlateResponse,
  VehiclePlateResponse,
  GeneralDetectionResponse,
} from '../types/api';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`analysis-tabpanel-${index}`}
      aria-labelledby={`analysis-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const AnalysisPage: React.FC = () => {
  const { user } = useAuth();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState<
    SignalPlateResponse | VehiclePlateResponse | GeneralDetectionResponse | null
  >(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setResults(null);
    setError(null);
  };

  const handleFileRemove = () => {
    setSelectedFile(null);
    setResults(null);
    setError(null);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const processFile = async () => {
    if (!selectedFile) return;

    setProcessing(true);
    setError(null);
    setResults(null);

    try {
      const base64Image = await apiService.fileToBase64(selectedFile);

      let response: SignalPlateResponse | VehiclePlateResponse | GeneralDetectionResponse;

      switch (activeTab) {
        case 0: // Placas de Sinalização
          response = await apiService.detectSignalPlates({
            image: base64Image,
            confidence_threshold: 0.5,
          });
          break;
        case 1: // Placas de Veículos
          response = await apiService.detectVehiclePlates({
            image: base64Image,
            confidence_threshold: 0.5,
          });
          break;
        case 2: // Detecção Geral
          response = await apiService.detectGeneral({
            image: base64Image,
            confidence_threshold: 0.5,
          });
          break;
        default:
          throw new Error('Tipo de análise não suportado');
      }

      setResults(response);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Erro ao processar arquivo';
      setError(errorMessage);
    } finally {
      setProcessing(false);
    }
  };

  const getTabIcon = (index: number) => {
    switch (index) {
      case 0:
        return '🚦';
      case 1:
        return '🚗';
      case 2:
        return '🔍';
      default:
        return '📁';
    }
  };

  const getTabLabel = (index: number) => {
    switch (index) {
      case 0:
        return 'Placas de Sinalização';
      case 1:
        return 'Placas de Veículos';
      case 2:
        return 'Detecção Geral';
      default:
        return 'Análise';
    }
  };

  const getTabDescription = (index: number) => {
    switch (index) {
      case 0:
        return 'Detecta e analisa placas de sinalização de trânsito';
      case 1:
        return 'Identifica e analisa placas de veículos (Mercosul e convencionais)';
      case 2:
        return 'Detecção geral de objetos em imagens';
      default:
        return 'Análise de imagem';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <Visibility sx={{ mr: 2, fontSize: 'inherit' }} />
          Análise de Visão Computacional
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Sistema de detecção e reconhecimento de placas, sinais de trânsito e análise de vídeo
        </Typography>
        {user && (
          <Chip
            label={`Bem-vindo, ${user.username}`}
            color="primary"
            variant="outlined"
            sx={{ mt: 1 }}
          />
        )}
      </Box>

      {/* Tabs de Tipo de Análise */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          {[0, 1, 2].map((index) => (
            <Tab
              key={index}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <span>{getTabIcon(index)}</span>
                  <span>{getTabLabel(index)}</span>
                </Box>
              }
              sx={{ py: 2 }}
            />
          ))}
        </Tabs>

        {[0, 1, 2].map((index) => (
          <TabPanel key={index} value={activeTab} index={index}>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
              {getTabDescription(index)}
            </Typography>
          </TabPanel>
        ))}
      </Paper>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Upload Section */}
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <CloudUpload sx={{ mr: 1 }} />
              Upload de Arquivo
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <FileUpload
              onFileSelect={handleFileSelect}
              onFileRemove={handleFileRemove}
              selectedFile={selectedFile}
              processing={processing}
              acceptedTypes="image"
              maxSize={10}
            />

            {selectedFile && (
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  onClick={processFile}
                  disabled={processing}
                  startIcon={processing ? <Speed /> : <Visibility />}
                >
                  {processing ? 'Processando...' : 'Analisar Arquivo'}
                </Button>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Results Section */}
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Visibility sx={{ mr: 1 }} />
              Resultados da Análise
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <ResultsDisplay
              results={results}
              loading={processing}
              error={error}
            />
          </CardContent>
        </Card>
      </Box>

      {/* Status da API */}
      <Box sx={{ mt: 4 }}>
        <Alert severity="info" sx={{ display: 'flex', alignItems: 'center' }}>
          <Security sx={{ mr: 1 }} />
          <Typography variant="body2">
            Sistema integrado com API de Visão Computacional - Status: Operacional
          </Typography>
        </Alert>
      </Box>
    </Container>
  );
};

export default AnalysisPage;
