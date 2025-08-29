-- Script de inicialização do banco de dados MBST
-- ===============================================

-- Criar tabela de placas
CREATE TABLE IF NOT EXISTS placas_mbst (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    significado TEXT,
    acao TEXT,
    penalidade TEXT,
    cores JSONB,
    formas JSONB,
    aplicacao TEXT,
    observacoes TEXT,
    pagina INTEGER,
    pdf_source VARCHAR(255),
    data_extracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_placas_codigo ON placas_mbst(codigo);
CREATE INDEX IF NOT EXISTS idx_placas_tipo ON placas_mbst(tipo);
CREATE INDEX IF NOT EXISTS idx_placas_cores ON placas_mbst USING GIN(cores);
CREATE INDEX IF NOT EXISTS idx_placas_formas ON placas_mbst USING GIN(formas);

-- Criar tabela de estatísticas
CREATE TABLE IF NOT EXISTS estatisticas_mbst (
    id SERIAL PRIMARY KEY,
    total_placas INTEGER NOT NULL,
    por_tipo JSONB,
    por_codigo JSONB,
    data_geracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    versao VARCHAR(20)
);

-- Inserir dados do dataset (será feito via Python)
-- Esta tabela será populada automaticamente pelo sistema

-- Criar view para consultas rápidas
CREATE OR REPLACE VIEW placas_resumo AS
SELECT 
    codigo,
    nome,
    tipo,
    cores,
    formas,
    data_extracao
FROM placas_mbst
ORDER BY codigo;

-- Função para buscar placas por características
CREATE OR REPLACE FUNCTION buscar_placas_por_caracteristicas(
    p_tipo VARCHAR DEFAULT NULL,
    p_cores TEXT[] DEFAULT NULL,
    p_formas TEXT[] DEFAULT NULL
)
RETURNS TABLE(
    codigo VARCHAR,
    nome VARCHAR,
    tipo VARCHAR,
    cores JSONB,
    formas JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.codigo,
        p.nome,
        p.tipo,
        p.cores,
        p.formas
    FROM placas_mbst p
    WHERE 
        (p_tipo IS NULL OR p.tipo ILIKE p_tipo)
        AND (p_cores IS NULL OR p.cores ?| p_cores)
        AND (p_formas IS NULL OR p.formas ?| p_formas)
    ORDER BY p.codigo;
END;
$$ LANGUAGE plpgsql;

-- Comentários nas tabelas
COMMENT ON TABLE placas_mbst IS 'Dataset oficial de placas de sinalização brasileiras do MBST';
COMMENT ON COLUMN placas_mbst.codigo IS 'Código oficial da placa (ex: R-1, A-6)';
COMMENT ON COLUMN placas_mbst.tipo IS 'Tipo da placa (regulamentacao, advertencia, informacao)';
COMMENT ON COLUMN placas_mbst.cores IS 'Array JSON com cores da placa';
COMMENT ON COLUMN placas_mbst.formas IS 'Array JSON com formas da placa';
