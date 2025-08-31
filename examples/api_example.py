

import time
import requests
import json
import base64
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30

class VisionAPIClient:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if include_auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        return headers
    
    def login(self, username: str, password: str) -> bool:
        try:
            if not self.refresh_token:
                print("❌ Nenhum refresh token disponível")
                return False
            
            url = f"{self.base_url}/auth/refresh"
            data = {"refresh_token": self.refresh_token}
            
            response = self.session.post(
                url,
                json=data,
                headers=self._get_headers(include_auth=False),
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                self.access_token = result["access_token"]
                print("✅ Token de acesso renovado com sucesso")
                return True
            else:
                print(f"❌ Falha na renovação do token: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Erro na renovação do token: {e}")
            return False
    
    def get_user_info(self) -> dict:
        try:
            url = f"{self.base_url}/health"
            
            response = self.session.get(
                url,
                headers=self._get_headers(include_auth=False),
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Falha na verificação de saúde: {response.status_code}")
                return {}
        
        except Exception as e:
            print(f"❌ Erro na verificação de saúde: {e}")
            return {}
    
    def get_api_info(self) -> dict:
        try:
            url = f"{self.base_url}/vision/status"
            
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Falha ao obter status da visão: {response.status_code}")
                return {}
        
        except Exception as e:
            print(f"❌ Erro ao obter status da visão: {e}")
            return {}
    
    def process_image(self, image_path: str, processing_options: dict = None) -> dict:
        try:
            requests_list = []
            
            for image_path in image_paths:
                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode()
                
                request_item = {
                    "image_request": {
                        "image_data": f"data:image/jpeg;base64,{image_data}",
                        "image_format": "jpeg",
                        "processing_mode": "balanced",
                        "detection_types": ["traffic_sign", "license_plate"],
                        "ocr_types": ["auto"],
                        "confidence_threshold": 0.7,
                        "max_detections": 10
                    },
                    "save_results": True,
                    "return_annotated_image": False,
                    "return_confidence_scores": True,
                    "return_processing_time": True
                }
                
                requests_list.append(request_item)
            
            batch_data = {
                "requests": requests_list,
                "batch_size": len(image_paths),
                "parallel_processing": True,
                "priority": "normal"
            }
            
            if batch_options:
                batch_data.update(batch_options)
            
            url = f"{self.base_url}/vision/batch"
            
            response = self.session.post(
                url,
                json=batch_data,
                headers=self._get_headers(),
                timeout=API_TIMEOUT * 2
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Falha no processamento em lote: {response.status_code} - {response.text}")
                return {}
        
        except Exception as e:
            print(f"❌ Erro no processamento em lote: {e}")
            return {}
    
    def get_system_metrics(self) -> dict:
        try:
            url = f"{self.base_url}/monitoring/alerts"
            
            response = self.session.get(
                url,
                headers=self._get_headers(),
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Falha ao obter alertas: {response.status_code}")
                return {}
        
        except Exception as e:
            print(f"❌ Erro ao obter alertas: {e}")
            return {}

def create_sample_image():
    print("🚀 EXEMPLO DE USO DA API REST - VISÃO COMPUTACIONAL")
    print("=" * 60)
    
    client = VisionAPIClient()
    
    try:
        print("\n🔍 Verificando saúde da API...")
        health = client.check_health()
        if health:
            print(f"✅ Status: {health.get('status', 'unknown')}")
            print(f"✅ Versão: {health.get('version', 'unknown')}")
            print(f"✅ Uptime: {health.get('uptime', 0):.1f}s")
        else:
            print("❌ Não foi possível verificar saúde da API")
            return
        
        print("\n📊 Obtendo informações da API...")
        api_info = client.get_api_info()
        if api_info:
            print(f"✅ Título: {api_info.get('title', 'unknown')}")
            print(f"✅ Descrição: {api_info.get('description', 'unknown')}")
            print(f"✅ Versão: {api_info.get('version', 'unknown')}")
            print(f"✅ Debug: {api_info.get('debug', False)}")
        
        print("\n🔐 Fazendo login...")
        if client.login("admin", "admin123"):
            print("✅ Login realizado com sucesso")
            
            user_info = client.get_user_info()
            if user_info:
                print(f"✅ Usuário: {user_info.get('username', 'unknown')}")
                print(f"✅ Email: {user_info.get('email', 'unknown')}")
                print(f"✅ Permissões: {', '.join(user_info.get('permissions', []))}")
        else:
            print("❌ Falha no login, tentando com usuário de teste...")
            if client.login("test", "test123"):
                print("✅ Login com usuário de teste realizado")
            else:
                print("❌ Falha no login com usuário de teste")
                return
        
        print("\n👁️ Verificando status da visão computacional...")
        vision_status = client.get_vision_status()
        if vision_status:
            print(f"✅ Status: {vision_status.get('status', 'unknown')}")
            print(f"✅ Pipeline disponível: {vision_status.get('pipeline_available', False)}")
            print(f"✅ Monitoramento disponível: {vision_status.get('monitoring_available', False)}")
        
        print("\n🖼️ Processando imagem de exemplo...")
        sample_image = create_sample_image()
        
        if sample_image and Path(sample_image).exists():
            processing_options = {
                "resize": {"width": 640, "height": 640},
                "enhancement": "contrast",
                "denoising": "gaussian"
            }
            
            result = client.process_image(sample_image, processing_options)
            
            if result:
                print("✅ Imagem processada com sucesso!")
                print(f"✅ Request ID: {result.get('request_id', 'unknown')}")
                print(f"✅ Timestamp: {result.get('timestamp', 'unknown')}")
                
                processing_result = result.get('result', {})
                if processing_result:
                    print(f"✅ Sucesso: {processing_result.get('success', False)}")
                    print(f"✅ Tempo de processamento: {processing_result.get('processing_time', 0):.3f}s")
                    print(f"✅ Detecções: {len(processing_result.get('detections', []))}")
                    print(f"✅ Resultados OCR: {len(processing_result.get('ocr_results', []))}")
                    
                    detections = processing_result.get('detections', [])
                    for i, det in enumerate(detections):
                        print(f"   📍 Detecção {i+1}: {det.get('class_name', 'unknown')} "
                              f"(conf: {det.get('confidence', 0):.2f})")
                    
                    ocr_results = processing_result.get('ocr_results', [])
                    for i, ocr in enumerate(ocr_results):
                        print(f"   📝 OCR {i+1}: '{ocr.get('text', '')}' "
                              f"(conf: {ocr.get('confidence', 0):.2f})")
            else:
                print("❌ Falha no processamento da imagem")
        else:
            print("⚠️ Imagem de exemplo não disponível, pulando processamento")
        
        print("\n📈 Obtendo métricas do sistema...")
        metrics = client.get_system_metrics()
        if metrics:
            print("✅ Métricas obtidas com sucesso")
            print(f"✅ Timestamp: {metrics.get('timestamp', 'unknown')}")
            
            system_metrics = metrics.get('system_metrics', {})
            if system_metrics:
                print(f"   🖥️ CPU: {system_metrics.get('cpu_percent', 0):.1f}%")
                print(f"   💾 Memória: {system_metrics.get('memory_percent', 0):.1f}%")
        
        print("\n🚨 Obtendo alertas do sistema...")
        alerts = client.get_system_alerts()
        if alerts:
            print("✅ Alertas obtidos com sucesso")
            print(f"✅ Total de alertas: {alerts.get('total_alerts', 0)}")
            print(f"✅ Alertas críticos: {alerts.get('critical_alerts', 0)}")
            print(f"✅ Alertas de aviso: {alerts.get('warning_alerts', 0)}")
            print(f"✅ Alertas informativos: {alerts.get('info_alerts', 0)}")
        
        print("\n🎉 Exemplo da API concluído com sucesso!")
        print("\n🌐 Para acessar a documentação da API:")
        print(f"   Swagger UI: {API_BASE_URL}/docs")
        print(f"   ReDoc: {API_BASE_URL}/redoc")
        print(f"   OpenAPI JSON: {API_BASE_URL}/openapi.json")
        
    except KeyboardInterrupt:
        print("\n⏹️ Exemplo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no exemplo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()