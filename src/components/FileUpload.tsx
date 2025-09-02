// Componente de Upload de Arquivos
// ===============================

import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  Card,
  CardContent,
  CardMedia,
} from '@mui/material';
import {
  CloudUpload,
  Image,
  VideoFile,
  Delete,
  CheckCircle,
} from '@mui/icons-material';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
  selectedFile: File | null;
  processing: boolean;
  acceptedTypes: 'image' | 'video' | 'both';
  maxSize?: number; // em MB
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  onFileRemove,
  selectedFile,
  processing,
  acceptedTypes,
  maxSize = 10,
}) => {
  const [dragActive, setDragActive] = useState(false);

  const getAcceptedTypes = () => {
    switch (acceptedTypes) {
      case 'image':
        return {
          'image/*': ['.jpg', '.jpeg', '.png', '.bmp', '.gif'],
        };
      case 'video':
        return {
          'video/*': ['.mp4', '.avi', '.mov', '.mpeg', '.webm'],
        };
      case 'both':
        return {
          'image/*': ['.jpg', '.jpeg', '.png', '.bmp', '.gif'],
          'video/*': ['.mp4', '.avi', '.mov', '.mpeg', '.webm'],
        };
      default:
        return {};
    }
  };

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: getAcceptedTypes(),
    maxSize: maxSize * 1024 * 1024, // Converter MB para bytes
    multiple: false,
    disabled: processing,
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return <Image sx={{ fontSize: 40, color: 'primary.main' }} />;
    } else if (file.type.startsWith('video/')) {
      return <VideoFile sx={{ fontSize: 40, color: 'primary.main' }} />;
    }
    return <CloudUpload sx={{ fontSize: 40, color: 'primary.main' }} />;
  };

  const getFilePreview = (file: File) => {
    if (file.type.startsWith('image/')) {
      return (
        <CardMedia
          component="img"
          height="200"
          image={URL.createObjectURL(file)}
          alt="Preview"
          sx={{ objectFit: 'contain' }}
        />
      );
    }
    return null;
  };

  return (
    <Box sx={{ width: '100%' }}>
      {!selectedFile ? (
        <Paper
          {...getRootProps()}
          sx={{
            p: 4,
            textAlign: 'center',
            cursor: processing ? 'not-allowed' : 'pointer',
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : 'grey.300',
            backgroundColor: isDragActive ? 'primary.50' : 'background.paper',
            transition: 'all 0.3s ease',
            '&:hover': {
              borderColor: 'primary.main',
              backgroundColor: 'primary.50',
            },
            opacity: processing ? 0.6 : 1,
          }}
        >
          <input {...getInputProps()} />
          <CloudUpload sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? 'Solte o arquivo aqui' : 'Arraste e solte um arquivo'}
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            ou clique para selecionar
          </Typography>
          <Box sx={{ mt: 2 }}>
            <Chip
              label={`Máximo: ${maxSize}MB`}
              size="small"
              color="primary"
              variant="outlined"
            />
          </Box>
          <Typography variant="caption" display="block" sx={{ mt: 1 }}>
            Formatos suportados:{' '}
            {acceptedTypes === 'image' && 'JPG, PNG, BMP, GIF'}
            {acceptedTypes === 'video' && 'MP4, AVI, MOV, MPEG'}
            {acceptedTypes === 'both' && 'JPG, PNG, BMP, GIF, MP4, AVI, MOV'}
          </Typography>
        </Paper>
      ) : (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              {getFileIcon(selectedFile)}
              <Box sx={{ ml: 2, flexGrow: 1 }}>
                <Typography variant="h6" noWrap>
                  {selectedFile.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {formatFileSize(selectedFile.size)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {selectedFile.type}
                </Typography>
              </Box>
              <IconButton
                onClick={onFileRemove}
                disabled={processing}
                color="error"
              >
                <Delete />
              </IconButton>
            </Box>

            {getFilePreview(selectedFile)}

            {processing && (
              <Box sx={{ mt: 2 }}>
                <LinearProgress />
                <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
                  Processando arquivo...
                </Typography>
              </Box>
            )}

            {!processing && (
              <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
                <CheckCircle sx={{ color: 'success.main', mr: 1 }} />
                <Typography variant="body2" color="success.main">
                  Arquivo selecionado com sucesso
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default FileUpload;
