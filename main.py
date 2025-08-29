#!/usr/bin/env python3
"""
API REST para Dataset MBST - Placas de Sinalização Brasileiras
=============================================================

Esta API permite consultar, buscar e gerenciar o dataset oficial do MBST
com suporte a múltiplos bancos de dados.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import json
import os
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="API Dataset MBST",
    description="API para consulta de placas de sinalização brasileiras do MBST",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class PlacaResponse(BaseModel):
    codigo: str
    nome: str
    tipo: str
    significado: str
    acao: str
    penalidade: str
    cores: List[str]
    formas: List[str]
    fonte: str

class SearchRequest(BaseModel):
    query: str
    tipo: Optional[str] = None
    cores: Optional[List[str]] = None
    formas: Optional[List[str]] = None

class StatsResponse(BaseModel):
    total_placas: int
    por_tipo: Dict[str, int]
    por_codigo: Dict[str, int]
    data_geracao: str

# Carregar dataset
def load_dataset():
    """Carrega o dataset MBST"""
    try:
        dataset_path = "dataset_mbst/dataset_completo_mbst.json"
        if os.path.exists(dataset_path):
            with open(dataset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.error("Dataset não encontrado")
            return {"placas": {}, "metadata": {}}
    except Exception as e:
        logger.error(f"Erro ao carregar dataset: {e}")
        return {"placas": {}, "metadata": {}}

# Rotas da API
@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial da API"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Dataset MBST</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { color: #007bff; font-weight: bold; }
            .url { color: #28a745; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚦 API Dataset MBST - Placas de Sinalização Brasileiras</h1>
            <p>Bem-vindo à API oficial do dataset MBST!</p>
            
            <h2>📚 Endpoints Disponíveis:</h2>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="url">/placas</span>
                <p>Lista todas as placas do dataset</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="url">/placas/{codigo}</span>
                <p>Busca uma placa específica por código</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="url">/placas/tipo/{tipo}</span>
                <p>Filtra placas por tipo (regulamentacao, advertencia, etc.)</p>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span> <span class="url">/placas/buscar</span>
                <p>Busca avançada por características</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="url">/stats</span>
                <p>Estatísticas do dataset</p>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <span class="url">/download</span>
                <p>Download do dataset completo em JSON</p>
            </div>
            
            <h2>🔗 Documentação:</h2>
            <ul>
                <li><a href="/docs">📖 Swagger UI</a></li>
                <li><a href="/redoc">📋 ReDoc</a></li>
            </ul>
            
            <h2>📊 Dataset Info:</h2>
            <p>Este dataset contém <strong>68 placas oficiais</strong> do Manual Brasileiro de Sinalização de Trânsito (MBST).</p>
        </div>
    </body>
    </html>
    """

@app.get("/placas", response_model=List[PlacaResponse])
async def listar_placas(
    limit: int = Query(100, description="Número máximo de placas retornadas"),
    offset: int = Query(0, description="Número de placas para pular")
):
    """Lista todas as placas do dataset com paginação"""
    try:
        dataset = load_dataset()
        placas = list(dataset.get("placas", {}).values())
        
        # Aplicar paginação
        total = len(placas)
        placas = placas[offset:offset + limit]
        
        # Converter para formato de resposta
        response = []
        for codigo, placa in dataset.get("placas", {}).items():
            if len(response) >= limit:
                break
            response.append(PlacaResponse(
                codigo=codigo,
                nome=placa.get("nome", ""),
                tipo=placa.get("tipo", ""),
                significado=placa.get("significado", ""),
                acao=placa.get("acao", ""),
                penalidade=placa.get("penalidade", ""),
                cores=placa.get("cores", []),
                formas=placa.get("formas", []),
                fonte="Dataset MBST Oficial"
            ))
        
        return response[:limit]
        
    except Exception as e:
        logger.error(f"Erro ao listar placas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/placas/{codigo}", response_model=PlacaResponse)
async def buscar_placa_por_codigo(codigo: str):
    """Busca uma placa específica por código"""
    try:
        dataset = load_dataset()
        placa = dataset.get("placas", {}).get(codigo.upper())
        
        if not placa:
            raise HTTPException(status_code=404, detail=f"Placa com código {codigo} não encontrada")
        
        return PlacaResponse(
            codigo=codigo.upper(),
            nome=placa.get("nome", ""),
            tipo=placa.get("tipo", ""),
            significado=placa.get("significado", ""),
            acao=placa.get("acao", ""),
            penalidade=placa.get("penalidade", ""),
            cores=placa.get("cores", []),
            formas=placa.get("formas", []),
            fonte="Dataset MBST Oficial"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar placa {codigo}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/placas/tipo/{tipo}", response_model=List[PlacaResponse])
async def filtrar_por_tipo(tipo: str):
    """Filtra placas por tipo"""
    try:
        dataset = load_dataset()
        placas_filtradas = []
        
        for codigo, placa in dataset.get("placas", {}).items():
            if placa.get("tipo", "").lower() == tipo.lower():
                placas_filtradas.append(PlacaResponse(
                    codigo=codigo,
                    nome=placa.get("nome", ""),
                    tipo=placa.get("tipo", ""),
                    significado=placa.get("significado", ""),
                    acao=placa.get("acao", ""),
                    penalidade=placa.get("penalidade", ""),
                    cores=placa.get("cores", []),
                    formas=placa.get("formas", []),
                    fonte="Dataset MBST Oficial"
                ))
        
        if not placas_filtradas:
            raise HTTPException(status_code=404, detail=f"Nenhuma placa encontrada para o tipo {tipo}")
        
        return placas_filtradas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao filtrar por tipo {tipo}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/placas/buscar", response_model=List[PlacaResponse])
async def buscar_avancada(request: SearchRequest):
    """Busca avançada por características"""
    try:
        dataset = load_dataset()
        placas_encontradas = []
        
        for codigo, placa in dataset.get("placas", {}).items():
            # Verificar se atende aos critérios
            match = True
            
            # Busca por texto
            if request.query:
                query_lower = request.query.lower()
                nome_lower = placa.get("nome", "").lower()
                significado_lower = placa.get("significado", "").lower()
                
                if query_lower not in nome_lower and query_lower not in significado_lower:
                    match = False
            
            # Filtro por tipo
            if request.tipo and placa.get("tipo", "").lower() != request.tipo.lower():
                match = False
            
            # Filtro por cores
            if request.cores:
                placa_cores = set(c.lower() for c in placa.get("cores", []))
                request_cores = set(c.lower() for c in request.cores)
                if not placa_cores.intersection(request_cores):
                    match = False
            
            # Filtro por formas
            if request.formas:
                placa_formas = set(f.lower() for f in placa.get("formas", []))
                request_formas = set(f.lower() for f in request.formas)
                if not placa_formas.intersection(request_formas):
                    match = False
            
            if match:
                placas_encontradas.append(PlacaResponse(
                    codigo=codigo,
                    nome=placa.get("nome", ""),
                    tipo=placa.get("tipo", ""),
                    significado=placa.get("significado", ""),
                    acao=placa.get("acao", ""),
                    penalidade=placa.get("penalidade", ""),
                    cores=placa.get("cores", []),
                    formas=placa.get("formas", []),
                    fonte="Dataset MBST Oficial"
                ))
        
        return placas_encontradas
        
    except Exception as e:
        logger.error(f"Erro na busca avançada: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/stats", response_model=StatsResponse)
async def estatisticas():
    """Retorna estatísticas do dataset"""
    try:
        dataset = load_dataset()
        metadata = dataset.get("metadata", {})
        
        return StatsResponse(
            total_placas=metadata.get("total_placas", 0),
            por_tipo=metadata.get("por_tipo", {}),
            por_codigo=metadata.get("por_codigo", {}),
            data_geracao=metadata.get("data_geracao", "")
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/download")
async def download_dataset():
    """Download do dataset completo em JSON"""
    try:
        dataset = load_dataset()
        return JSONResponse(
            content=dataset,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=dataset_mbst_{datetime.now().strftime('%Y%m%d')}.json"
            }
        )
        
    except Exception as e:
        logger.error(f"Erro ao fazer download: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/health")
async def health_check():
    """Verificação de saúde da API"""
    try:
        dataset = load_dataset()
        total_placas = len(dataset.get("placas", {}))
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "dataset_loaded": total_placas > 0,
            "total_placas": total_placas,
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
