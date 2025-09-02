// Componente de Exibição de Resultados
// ===================================

import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Grid,
  LinearProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  ExpandMore,
  Visibility,
  Speed,
  CheckCircle,
  Error,
  Info,
  Image,
  VideoFile,
} from '@mui/icons-material';
import { Detection, SignalPlateResponse, VehiclePlateResponse, GeneralDetectionResponse } from '../types/api';

interface ResultsDisplayProps {
  results: SignalPlateResponse | VehiclePlateResponse | GeneralDetectionResponse | null;
  loading: boolean;
  error: string | null;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({
  results,
  loading,
  error,
}) => {
  const getDetectionIcon = (className: string | undefined) => {
    if (!className) return '❓';
    switch (className.toLowerCase()) {
      case 'license_plate':
        return '🚗';
      case 'traffic_sign':
        return '🚦';
      case 'pothole':
        return '🕳️';
      default:
        return '🔍';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  const formatConfidence = (confidence: number) => {
    return `${(confidence * 100).toFixed(1)}%`;
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('pt-BR');
  };

  const DetectionItem: React.FC<{ detection: Detection; index: number }> = ({
    detection,
    index,
  }) => (
    <Card variant="outlined" sx={{ mb: 1 }}>
      <CardContent sx={{ py: 1.5 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6" sx={{ mr: 1 }}>
            {getDetectionIcon(detection.class_name)}
          </Typography>
          <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
            Detecção {index + 1}
          </Typography>
          <Chip
            label={formatConfidence(detection.confidence)}
            color={getConfidenceColor(detection.confidence)}
            size="small"
          />
        </Box>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          <strong>Classe:</strong> {detection.class_name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          <strong>Área:</strong> [{detection.bbox.x1}, {detection.bbox.y1}, {detection.bbox.x2}, {detection.bbox.y2}]
        </Typography>
        <Box sx={{ mt: 1 }}>
          <LinearProgress
            variant="determinate"
            value={detection.confidence * 100}
            color={getConfidenceColor(detection.confidence)}
            sx={{ height: 6, borderRadius: 3 }}
          />
        </Box>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Speed sx={{ mr: 1, color: 'primary.main' }} />
            <Typography variant="h6">Processando...</Typography>
          </Box>
          <LinearProgress />
          <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
            Analisando arquivo, aguarde...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Erro no processamento
        </Typography>
        <Typography variant="body2">{error}</Typography>
      </Alert>
    );
  }

  if (!results) {
    return (
      <Card>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <Image sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Nenhum resultado disponível
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Faça upload de um arquivo para ver os resultados da análise
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      {/* Status Geral */}
      <Alert
        severity={results.success ? 'success' : 'error'}
        sx={{ mb: 2 }}
        icon={results.success ? <CheckCircle /> : <Error />}
      >
        <Typography variant="h6" gutterBottom>
          {results.success ? 'Processamento Concluído' : 'Erro no Processamento'}
        </Typography>
        <Typography variant="body2">{results.message}</Typography>
      </Alert>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {/* Informações Gerais */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Info sx={{ mr: 1 }} />
              Informações Gerais
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText
                  primary="ID da Imagem"
                  secondary={results.image_id}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Status"
                  secondary={
                    <Chip
                      label={results.success ? 'Sucesso' : 'Erro'}
                      color={results.success ? 'success' : 'error'}
                      size="small"
                    />
                  }
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Timestamp"
                  secondary={formatTimestamp(results.timestamp)}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Total de Detecções"
                  secondary={'total_detections' in results ? results.total_detections : 
                           'total_vehicles' in results ? results.total_vehicles : 0}
                />
              </ListItem>
              {'total_vehicles' in results && (
                <ListItem>
                  <ListItemText
                    primary="Total de Veículos"
                    secondary={results.total_vehicles}
                  />
                </ListItem>
              )}
              {'total_plates' in results && (
                <ListItem>
                  <ListItemText
                    primary="Total de Placas"
                    secondary={results.total_plates}
                  />
                </ListItem>
              )}
            </List>
          </CardContent>
        </Card>

        {/* Estatísticas de Confiança */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              <Visibility sx={{ mr: 1 }} />
              Estatísticas de Confiança
            </Typography>
            {results.detections.length > 0 ? (
              <Box>
                <Typography variant="body2" gutterBottom>
                  Confiança Média: {formatConfidence(
                    results.detections.reduce((sum, d) => sum + d.confidence, 0) / results.detections.length
                  )}
                </Typography>
                <Typography variant="body2" gutterBottom>
                  Maior Confiança: {formatConfidence(
                    Math.max(...results.detections.map(d => d.confidence))
                  )}
                </Typography>
                <Typography variant="body2">
                  Menor Confiança: {formatConfidence(
                    Math.min(...results.detections.map(d => d.confidence))
                  )}
                </Typography>
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Nenhuma detecção encontrada
              </Typography>
            )}
          </CardContent>
        </Card>

        {/* Detecções */}
        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6">
              Detecções Encontradas ({results.detections.length})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            {results.detections.length > 0 ? (
              <Box>
                {results.detections.map((detection, index) => (
                  <DetectionItem
                    key={index}
                    detection={detection}
                    index={index}
                  />
                ))}
              </Box>
            ) : (
              <Alert severity="info">
                Nenhuma detecção encontrada na imagem.
              </Alert>
            )}
          </AccordionDetails>
        </Accordion>
      </Box>
    </Box>
  );
};

export default ResultsDisplay;
