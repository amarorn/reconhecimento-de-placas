// Página de Login
// ==============

import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import {
  Security,
  Login as LoginIcon,
  Visibility,
  VisibilityOff,
  InputAdornment,
  IconButton,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const LoginPage: React.FC = () => {
  const { login, loading, error } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: 'admin',
    password: 'admin123',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    setLocalError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    try {
      await login(formData);
      navigate('/');
    } catch (err: any) {
      setLocalError(err.message);
    }
  };

  const handleTogglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Card sx={{ width: '100%', maxWidth: 400 }}>
          <CardContent sx={{ p: 4 }}>
            {/* Header */}
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <Security sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
              <Typography component="h1" variant="h4" gutterBottom>
                Sistema de Visão Computacional
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Faça login para acessar o sistema
              </Typography>
            </Box>

            <Divider sx={{ mb: 3 }} />

            {/* Form */}
            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="username"
                label="Usuário"
                name="username"
                autoComplete="username"
                autoFocus
                value={formData.username}
                onChange={handleInputChange}
                disabled={loading}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Senha"
                type={showPassword ? 'text' : 'password'}
                id="password"
                autoComplete="current-password"
                value={formData.password}
                onChange={handleInputChange}
                disabled={loading}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        aria-label="toggle password visibility"
                        onClick={handleTogglePasswordVisibility}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              {/* Error Messages */}
              {(error || localError) && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error || localError}
                </Alert>
              )}

              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2, py: 1.5 }}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <LoginIcon />}
              >
                {loading ? 'Entrando...' : 'Entrar'}
              </Button>

              {/* Demo Credentials */}
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  mt: 2,
                  backgroundColor: 'grey.50',
                  border: '1px dashed',
                  borderColor: 'grey.300',
                }}
              >
                <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
                  <strong>Credenciais de Demonstração:</strong>
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Usuário: admin
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Senha: admin123
                </Typography>
              </Paper>
            </Box>
          </CardContent>
        </Card>

        {/* Footer */}
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Sistema de Reconhecimento de Placas v2.0
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block">
            Powered by React + TypeScript + FastAPI
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default LoginPage;
