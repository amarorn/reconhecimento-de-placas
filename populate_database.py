#!/usr/bin/env python3
"""
Script para popular banco de dados com dataset MBST
==================================================

Este script popula o banco de dados PostgreSQL com os dados do dataset MBST
"""

import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabasePopulator:
    """Classe para popular banco de dados com dataset MBST"""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = None
        
    def connect(self):
        """Conecta ao banco de dados"""
        try:
            self.conn = psycopg2.connect(self.db_url)
            logger.info("✅ Conectado ao banco de dados PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao banco: {e}")
            return False
    
    def disconnect(self):
        """Desconecta do banco de dados"""
        if self.conn:
            self.conn.close()
            logger.info("🔌 Desconectado do banco de dados")
    
    def create_tables(self):
        """Cria as tabelas necessárias"""
        try:
            with self.conn.cursor() as cursor:
                # Ler script SQL
                script_path = "init_scripts/init_mbst.sql"
                if os.path.exists(script_path):
                    with open(script_path, 'r', encoding='utf-8') as f:
                        sql_script = f.read()
                    
                    # Executar script
                    cursor.execute(sql_script)
                    self.conn.commit()
                    logger.info("✅ Tabelas criadas com sucesso")
                else:
                    logger.warning("⚠️ Script SQL não encontrado")
                    
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
            self.conn.rollback()
    
    def populate_placas(self):
        """Popula a tabela de placas com dados do MBST"""
        try:
            # Carregar dataset
            dataset_path = "dataset_mbst/dataset_completo_mbst.json"
            if not os.path.exists(dataset_path):
                logger.error("❌ Dataset não encontrado")
                return False
            
            with open(dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            # Inserir placas
            with self.conn.cursor() as cursor:
                for codigo, placa in dataset.get("placas", {}).items():
                    # Verificar se já existe
                    cursor.execute("SELECT id FROM placas_mbst WHERE codigo = %s", (codigo,))
                    if cursor.fetchone():
                        logger.info(f"⏭️ Placa {codigo} já existe, pulando...")
                        continue
                    
                    # Inserir nova placa
                    insert_query = """
                    INSERT INTO placas_mbst (
                        codigo, nome, tipo, significado, acao, penalidade,
                        cores, formas, aplicacao, observacoes, pagina,
                        pdf_source, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(insert_query, (
                        codigo,
                        placa.get("nome", ""),
                        placa.get("tipo", ""),
                        placa.get("significado", ""),
                        placa.get("acao", ""),
                        placa.get("penalidade", ""),
                        json.dumps(placa.get("cores", [])),
                        json.dumps(placa.get("formas", [])),
                        placa.get("aplicacao", ""),
                        placa.get("observacoes", ""),
                        placa.get("pagina"),
                        placa.get("pdf_source", ""),
                        json.dumps(placa.get("metadata", {}))
                    ))
                    
                    logger.info(f"✅ Placa {codigo} inserida")
                
                self.conn.commit()
                logger.info("✅ Todas as placas foram inseridas")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao popular placas: {e}")
            self.conn.rollback()
            return False
    
    def populate_estatisticas(self):
        """Popula a tabela de estatísticas"""
        try:
            # Carregar dataset
            dataset_path = "dataset_mbst/dataset_completo_mbst.json"
            with open(dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            metadata = dataset.get("metadata", {})
            
            with self.conn.cursor() as cursor:
                # Inserir estatísticas
                insert_query = """
                INSERT INTO estatisticas_mbst (
                    total_placas, por_tipo, por_codigo, data_geracao, versao
                ) VALUES (%s, %s, %s, %s, %s)
                """
                
                cursor.execute(insert_query, (
                    metadata.get("total_placas", 0),
                    json.dumps(metadata.get("por_tipo", {})),
                    json.dumps(metadata.get("por_codigo", {})),
                    metadata.get("data_geracao", datetime.now().isoformat()),
                    metadata.get("versao", "3.0")
                ))
                
                self.conn.commit()
                logger.info("✅ Estatísticas inseridas")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao inserir estatísticas: {e}")
            self.conn.rollback()
            return False
    
    def verify_data(self):
        """Verifica se os dados foram inseridos corretamente"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Contar placas
                cursor.execute("SELECT COUNT(*) as total FROM placas_mbst")
                total_placas = cursor.fetchone()['total']
                
                # Contar por tipo
                cursor.execute("""
                    SELECT tipo, COUNT(*) as quantidade 
                    FROM placas_mbst 
                    GROUP BY tipo 
                    ORDER BY quantidade DESC
                """)
                por_tipo = dict(cursor.fetchall())
                
                # Contar por código
                cursor.execute("SELECT COUNT(*) as total FROM estatisticas_mbst")
                stats_count = cursor.fetchone()['total']
                
                logger.info(f"📊 VERIFICAÇÃO DOS DADOS:")
                logger.info(f"   • Total de placas: {total_placas}")
                logger.info(f"   • Distribuição por tipo: {por_tipo}")
                logger.info(f"   • Estatísticas inseridas: {stats_count}")
                
                return total_placas > 0
                
        except Exception as e:
            logger.error(f"❌ Erro na verificação: {e}")
            return False
    
    def run(self):
        """Executa todo o processo de população"""
        try:
            logger.info("🚀 INICIANDO POPULAÇÃO DO BANCO DE DADOS MBST")
            
            # Conectar
            if not self.connect():
                return False
            
            # Criar tabelas
            self.create_tables()
            
            # Popular placas
            if not self.populate_placas():
                return False
            
            # Popular estatísticas
            if not self.populate_estatisticas():
                return False
            
            # Verificar dados
            if not self.verify_data():
                return False
            
            logger.info("🎉 POPULAÇÃO CONCLUÍDA COM SUCESSO!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante população: {e}")
            return False
        finally:
            self.disconnect()

def main():
    """Função principal"""
    # Configuração do banco (pode ser alterada)
    db_url = "postgresql://mbst_user:mbst_password@localhost:5432/mbst_dataset"
    
    # Para Docker, usar o nome do container
    # db_url = "postgresql://mbst_user:mbst_password@mbst_postgres:5432/mbst_dataset"
    
    # Verificar variáveis de ambiente
    if os.getenv("DATABASE_URL"):
        db_url = os.getenv("DATABASE_URL")
    
    logger.info(f"🔗 Conectando ao banco: {db_url.split('@')[1] if '@' in db_url else db_url}")
    
    # Executar população
    populator = DatabasePopulator(db_url)
    success = populator.run()
    
    if success:
        logger.info("✅ Banco de dados populado com sucesso!")
        logger.info("🌐 Você pode agora usar a API em http://localhost:8000")
    else:
        logger.error("❌ Falha na população do banco de dados")
        exit(1)

if __name__ == "__main__":
    main()
