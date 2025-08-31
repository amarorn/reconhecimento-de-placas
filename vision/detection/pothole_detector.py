#!/usr/bin/env python3

import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from pathlib import Path
import time
from dataclasses import dataclass
from collections import defaultdict, deque
import json

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    YOLO = None

@dataclass
class PotholeDetection:
    bbox: Tuple[int, int, int, int]
    confidence: float
    class_name: str
    pothole_type: Optional[str] = None
    severity_level: Optional[str] = None
    depth_estimate: Optional[float] = None
    area_estimate: Optional[float] = None
    risk_score: Optional[float] = None

@dataclass
class VideoPotholeAnalysis:
    frame_number: int
    timestamp: float
    detections: List[PotholeDetection]
    frame_quality: float
    road_condition: str
    maintenance_priority: str

@dataclass
class PotholeTrack:
    track_id: int
    first_frame: int
    last_frame: int
    detections: List[PotholeDetection]
    average_confidence: float
    average_risk_score: float
    severity_level: str
    total_frames: int
    stability_score: float

class PotholeDetector:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = None
        self.device = "auto"
        self.confidence_threshold = config.get('confidence_threshold', 0.5)
        self.iou_threshold = config.get('iou_threshold', 0.45)
        self.model_path = config.get('model_path', 'models/pothole_yolo.pt')
        
        # Configurações para análise de vídeo
        self.video_config = config.get('video_analysis', {})
        self.frame_skip = self.video_config.get('frame_skip', 1)
        self.min_track_length = self.video_config.get('min_track_length', 3)
        self.tracking_threshold = self.video_config.get('tracking_threshold', 0.7)
        self.max_tracks = self.video_config.get('max_tracks', 50)
        
        # Sistema de tracking
        self.tracks = {}
        self.next_track_id = 0
        self.frame_history = deque(maxlen=30)
        
        self.pothole_types = [
            'small_pothole', 'medium_pothole', 'large_pothole', 'crack',
            'sinkhole', 'road_damage', 'surface_deterioration', 'edge_drop'
        ]
        
        self.severity_levels = {
            'low': {'depth_range': (0.01, 0.05), 'risk_score': (0.1, 0.3)},
            'medium': {'depth_range': (0.05, 0.15), 'risk_score': (0.3, 0.6)},
            'high': {'depth_range': (0.15, 0.30), 'risk_score': (0.6, 0.8)},
            'critical': {'depth_range': (0.30, 1.0), 'risk_score': (0.8, 1.0)}
        }
        
        self.initialize()
    
    def initialize(self):
        if not YOLO_AVAILABLE:
            raise RuntimeError("Ultralytics YOLO não está disponível")
        
        try:
            self.model = YOLO(self.model_path)
            self.device = self._detect_device()
            self.logger.info(f"PotholeDetector inicializado com modelo: {self.model_path}")
            self.logger.info(f"Dispositivo detectado: {self.device}")
            self.logger.info(f"Configuração de vídeo: frame_skip={self.frame_skip}, min_track_length={self.min_track_length}")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar modelo: {e}")
            raise
    
    def _detect_device(self) -> str:
        if not YOLO_AVAILABLE:
            return "cpu"
        
        try:
            if self.model.device.type == "cuda":
                return "cuda"
            elif self.model.device.type == "mps":
                return "mps"
            else:
                return "cpu"
        except:
            return "cpu"
    
    def detect(self, image: np.ndarray) -> List[PotholeDetection]:
        if self.model is None:
            return []
        
        try:
            start_time = time.time()
            
            results = self.model(
                image,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False
            )
            
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is None:
                    continue
                
                for box in boxes:
                    bbox = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    
                    detection = PotholeDetection(
                        bbox=tuple(bbox.astype(int)),
                        confidence=confidence,
                        class_name=class_name
                    )
                    
                    detection = self._analyze_pothole(detection, image)
                    detections.append(detection)
            
            processing_time = time.time() - start_time
            self.logger.info(f"Detectados {len(detections)} buracos em {processing_time:.3f}s")
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Erro na detecção: {e}")
            return []
    
    def process_video(self, video_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Processa um vídeo completo para análise de buracos"""
        
        if not Path(video_path).exists():
            raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")
        
        self.logger.info(f"Iniciando processamento do vídeo: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Não foi possível abrir o vídeo: {video_path}")
        
        # Informações do vídeo
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps
        
        self.logger.info(f"Vídeo: {width}x{height}, {fps} FPS, {total_frames} frames, {duration:.2f}s")
        
        # Preparar vídeo de saída se especificado
        output_video = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            output_video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Análise do vídeo
        frame_analyses = []
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Processar apenas frames específicos (frame_skip)
                if frame_count % self.frame_skip != 0:
                    frame_count += 1
                    continue
                
                # Detectar buracos no frame
                detections = self.detect(frame)
                
                # Atualizar sistema de tracking
                self._update_tracking(detections, frame_count)
                
                # Analisar qualidade do frame
                frame_quality = self._assess_frame_quality(frame)
                
                # Gerar análise do frame
                frame_analysis = VideoPotholeAnalysis(
                    frame_number=frame_count,
                    timestamp=frame_count / fps,
                    detections=detections,
                    frame_quality=frame_quality,
                    road_condition=self._assess_road_condition_from_detections(detections),
                    maintenance_priority=self._assess_maintenance_priority_from_detections(detections)
                )
                
                frame_analyses.append(frame_analysis)
                
                # Desenhar detecções no frame
                annotated_frame = self.draw_detections(frame, detections)
                
                # Adicionar informações de tracking
                annotated_frame = self._draw_tracking_info(annotated_frame, frame_count)
                
                # Salvar frame no vídeo de saída
                if output_video:
                    output_video.write(annotated_frame)
                
                # Log de progresso
                if frame_count % (fps * 5) == 0:  # A cada 5 segundos
                    elapsed_time = time.time() - start_time
                    progress = (frame_count / total_frames) * 100
                    self.logger.info(f"Progresso: {progress:.1f}% ({frame_count}/{total_frames}) - Tempo: {elapsed_time:.1f}s")
                
                frame_count += 1
                
                # Limitar processamento para evitar sobrecarga
                if len(frame_analyses) > 1000:
                    self.logger.warning("Limite de frames atingido, parando processamento")
                    break
                
        finally:
            cap.release()
            if output_video:
                output_video.release()
        
        # Finalizar análise
        processing_time = time.time() - start_time
        self.logger.info(f"Processamento concluído em {processing_time:.2f}s")
        
        # Gerar relatório final
        final_report = self._generate_video_report(frame_analyses, fps, total_frames, duration)
        
        return final_report
    
    def _update_tracking(self, detections: List[PotholeDetection], frame_number: int):
        """Atualiza o sistema de tracking de buracos"""
        
        current_tracks = {}
        
        for detection in detections:
            best_track_id = None
            best_overlap = 0
            
            # Encontrar track mais similar
            for track_id, track in self.tracks.items():
                if not track.detections:
                    continue
                
                last_detection = track.detections[-1]
                overlap = self._calculate_bbox_overlap(detection.bbox, last_detection.bbox)
                
                if overlap > self.tracking_threshold and overlap > best_overlap:
                    best_overlap = overlap
                    best_track_id = track_id
            
            if best_track_id is not None:
                # Atualizar track existente
                track = self.tracks[best_track_id]
                track.detections.append(detection)
                track.last_frame = frame_number
                track.total_frames += 1
                
                # Atualizar estatísticas
                confidences = [d.confidence for d in track.detections]
                risk_scores = [d.risk_score for d in track.detections if d.risk_score]
                
                track.average_confidence = np.mean(confidences)
                if risk_scores:
                    track.average_risk_score = np.mean(risk_scores)
                
                # Atualizar severidade baseada na média
                track.severity_level = self._classify_severity_from_track(track)
                
                current_tracks[best_track_id] = track
                
            else:
                # Criar novo track
                new_track = PotholeTrack(
                    track_id=self.next_track_id,
                    first_frame=frame_number,
                    last_frame=frame_number,
                    detections=[detection],
                    average_confidence=detection.confidence,
                    average_risk_score=detection.risk_score or 0.0,
                    severity_level=detection.severity_level or 'low',
                    total_frames=1,
                    stability_score=1.0
                )
                
                self.tracks[self.next_track_id] = new_track
                current_tracks[self.next_track_id] = new_track
                self.next_track_id += 1
        
        # Limpar tracks antigos
        active_tracks = {}
        for track_id, track in self.tracks.items():
            if track_id in current_tracks or track.total_frames >= self.min_track_length:
                active_tracks[track_id] = track
        
        self.tracks = active_tracks
        
        # Manter apenas o número máximo de tracks
        if len(self.tracks) > self.max_tracks:
            sorted_tracks = sorted(self.tracks.items(), key=lambda x: x[1].total_frames, reverse=True)
            self.tracks = dict(sorted_tracks[:self.max_tracks])
    
    def _calculate_bbox_overlap(self, bbox1: Tuple[int, int, int, int], 
                               bbox2: Tuple[int, int, int, int]) -> float:
        """Calcula sobreposição entre duas bounding boxes"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calcular interseção
        x_left = max(x1_1, x1_2)
        y_top = max(y1_1, y1_2)
        x_right = min(x2_1, x2_2)
        y_bottom = min(y2_1, y2_2)
        
        if x_right < x_left or y_bottom < y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def _classify_severity_from_track(self, track: PotholeTrack) -> str:
        """Classifica severidade baseada no histórico do track"""
        if not track.detections:
            return 'low'
        
        # Calcular severidade média
        severity_scores = []
        for detection in track.detections:
            if detection.severity_level:
                severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
                severity_scores.append(severity_map.get(detection.severity_level, 1))
        
        if not severity_scores:
            return 'low'
        
        avg_severity = np.mean(severity_scores)
        
        if avg_severity >= 3.5:
            return 'critical'
        elif avg_severity >= 2.5:
            return 'high'
        elif avg_severity >= 1.5:
            return 'medium'
        else:
            return 'low'
    
    def _assess_frame_quality(self, frame: np.ndarray) -> float:
        """Avalia a qualidade do frame para análise"""
        try:
            # Converter para escala de cinza
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calcular variância (maior variância = mais detalhes)
            variance = np.var(gray)
            
            # Calcular gradiente (maior gradiente = mais bordas)
            grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            avg_gradient = np.mean(gradient_magnitude)
            
            # Normalizar scores
            variance_score = min(variance / 1000, 1.0)
            gradient_score = min(avg_gradient / 50, 1.0)
            
            # Score final
            quality_score = (variance_score * 0.6 + gradient_score * 0.4)
            
            return min(max(quality_score, 0.0), 1.0)
            
        except Exception as e:
            self.logger.warning(f"Erro ao avaliar qualidade do frame: {e}")
            return 0.5
    
    def _assess_road_condition_from_detections(self, detections: List[PotholeDetection]) -> str:
        """Avalia condição da estrada baseada nas detecções do frame"""
        if not detections:
            return "excellent"
        
        total_risk = sum(det.risk_score or 0.0 for det in detections)
        avg_risk = total_risk / len(detections)
        
        if avg_risk <= 0.3:
            return "good"
        elif avg_risk <= 0.6:
            return "fair"
        elif avg_risk <= 0.8:
            return "poor"
        else:
            return "critical"
    
    def _assess_maintenance_priority_from_detections(self, detections: List[PotholeDetection]) -> str:
        """Avalia prioridade de manutenção baseada nas detecções do frame"""
        if not detections:
            return "low"
        
        critical_count = sum(1 for det in detections if det.severity_level == 'critical')
        high_count = sum(1 for det in detections if det.severity_level == 'high')
        
        if critical_count > 0:
            return "immediate"
        elif high_count > 2:
            return "high"
        elif high_count > 0:
            return "medium"
        else:
            return "low"
    
    def _draw_tracking_info(self, frame: np.ndarray, frame_number: int) -> np.ndarray:
        """Desenha informações de tracking no frame"""
        output_frame = frame.copy()
        
        # Informações do frame
        cv2.putText(output_frame, f"Frame: {frame_number}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(output_frame, f"Tracks: {len(self.tracks)}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Estatísticas dos tracks
        if self.tracks:
            active_tracks = [t for t in self.tracks.values() if t.total_frames >= self.min_track_length]
            if active_tracks:
                avg_confidence = np.mean([t.average_confidence for t in active_tracks])
                avg_risk = np.mean([t.average_risk_score for t in active_tracks])
                
                cv2.putText(output_frame, f"Avg Conf: {avg_confidence:.2f}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(output_frame, f"Avg Risk: {avg_risk:.2f}", (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return output_frame
    
    def _generate_video_report(self, frame_analyses: List[VideoPotholeAnalysis], 
                              fps: float, total_frames: int, duration: float) -> Dict[str, Any]:
        """Gera relatório final da análise do vídeo"""
        
        # Estatísticas gerais
        total_detections = sum(len(analysis.detections) for analysis in frame_analyses)
        frames_with_detections = sum(1 for analysis in frame_analyses if analysis.detections)
        
        # Análise de qualidade dos frames
        frame_qualities = [analysis.frame_quality for analysis in frame_analyses]
        avg_frame_quality = np.mean(frame_qualities) if frame_qualities else 0.0
        
        # Análise de condição da estrada
        road_conditions = [analysis.road_condition for analysis in frame_analyses]
        road_condition_counts = defaultdict(int)
        for condition in road_conditions:
            road_condition_counts[condition] += 1
        
        # Análise de prioridade de manutenção
        maintenance_priorities = [analysis.maintenance_priority for analysis in frame_analyses]
        priority_counts = defaultdict(int)
        for priority in maintenance_priorities:
            priority_counts[priority] += 1
        
        # Análise dos tracks
        track_analysis = []
        for track in self.tracks.values():
            if track.total_frames >= self.min_track_length:
                track_analysis.append({
                    'track_id': track.track_id,
                    'first_frame': track.first_frame,
                    'last_frame': track.last_frame,
                    'total_frames': track.total_frames,
                    'average_confidence': track.average_confidence,
                    'average_risk_score': track.average_risk_score,
                    'severity_level': track.severity_level,
                    'stability_score': track.stability_score
                })
        
        # Relatório final
        report = {
            'video_info': {
                'path': str(Path(video_path)) if 'video_path' in locals() else 'unknown',
                'fps': fps,
                'total_frames': total_frames,
                'duration': duration,
                'processed_frames': len(frame_analyses)
            },
            'detection_summary': {
                'total_detections': total_detections,
                'frames_with_detections': frames_with_detections,
                'detection_rate': frames_with_detections / len(frame_analyses) if frame_analyses else 0.0
            },
            'quality_analysis': {
                'average_frame_quality': avg_frame_quality,
                'quality_distribution': {
                    'excellent': sum(1 for q in frame_qualities if q >= 0.8),
                    'good': sum(1 for q in frame_qualities if 0.6 <= q < 0.8),
                    'fair': sum(1 for q in frame_qualities if 0.4 <= q < 0.6),
                    'poor': sum(1 for q in frame_qualities if q < 0.4)
                }
            },
            'road_condition_analysis': {
                'condition_distribution': dict(road_condition_counts),
                'overall_condition': max(road_condition_counts.items(), key=lambda x: x[1])[0] if road_condition_counts else 'unknown'
            },
            'maintenance_analysis': {
                'priority_distribution': dict(priority_counts),
                'overall_priority': max(priority_counts.items(), key=lambda x: x[1])[0] if priority_counts else 'low'
            },
            'tracking_analysis': {
                'total_tracks': len(self.tracks),
                'stable_tracks': len([t for t in self.tracks.values() if t.total_frames >= self.min_track_length]),
                'track_details': track_analysis
            },
            'recommendations': self._generate_video_recommendations(
                total_detections, avg_frame_quality, road_condition_counts, priority_counts
            )
        }
        
        return report
    
    def _generate_video_recommendations(self, total_detections: int, avg_quality: float,
                                      road_conditions: Dict[str, int], priorities: Dict[str, int]) -> List[str]:
        """Gera recomendações baseadas na análise do vídeo"""
        
        recommendations = []
        
        # Recomendações baseadas no número de detecções
        if total_detections > 100:
            recommendations.append("Número elevado de buracos detectados - intervenção urgente necessária")
        elif total_detections > 50:
            recommendations.append("Múltiplos buracos detectados - manutenção programada recomendada")
        elif total_detections > 10:
            recommendations.append("Alguns buracos detectados - manutenção preventiva recomendada")
        else:
            recommendations.append("Poucos buracos detectados - condição da estrada aceitável")
        
        # Recomendações baseadas na qualidade dos frames
        if avg_quality < 0.4:
            recommendations.append("Qualidade dos frames baixa - considerar melhorar iluminação ou resolução")
        elif avg_quality < 0.6:
            recommendations.append("Qualidade dos frames moderada - otimizar condições de captura")
        
        # Recomendações baseadas na condição da estrada
        if road_conditions.get('critical', 0) > 0:
            recommendations.append("Condição crítica detectada - intervenção imediata necessária")
        if road_conditions.get('poor', 0) > len(road_conditions) * 0.3:
            recommendations.append("Condição geral da estrada ruim - manutenção abrangente recomendada")
        
        # Recomendações baseadas na prioridade de manutenção
        if priorities.get('immediate', 0) > 0:
            recommendations.append("Prioridade imediata identificada - ação urgente necessária")
        if priorities.get('high', 0) > len(priorities) * 0.2:
            recommendations.append("Múltiplas prioridades altas - planejamento de manutenção urgente")
        
        return recommendations
    
    def _analyze_pothole(self, detection: PotholeDetection, image: np.ndarray) -> PotholeDetection:
        x1, y1, x2, y2 = detection.bbox
        
        detection.pothole_type = detection.class_name
        detection.area_estimate = self._estimate_area(detection.bbox)
        detection.depth_estimate = self._estimate_depth(image, detection.bbox)
        detection.severity_level = self._classify_severity(detection.depth_estimate)
        detection.risk_score = self._calculate_risk_score(detection)
        
        return detection
    
    def _estimate_area(self, bbox: Tuple[int, int, int, int]) -> float:
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        return width * height
    
    def _estimate_depth(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> float:
        x1, y1, x2, y2 = bbox
        roi = image[y1:y2, x1:x2]
        
        if roi.size == 0:
            return 0.0
        
        try:
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY) if len(roi.shape) == 3 else roi
            
            mean_intensity = np.mean(gray_roi)
            std_intensity = np.std(gray_roi)
            
            depth_estimate = (255 - mean_intensity) / 255.0 * 0.5
            depth_estimate += (std_intensity / 255.0) * 0.3
            
            return min(max(depth_estimate, 0.01), 1.0)
            
        except Exception as e:
            self.logger.warning(f"Erro ao estimar profundidade: {e}")
            return 0.05
    
    def _classify_severity(self, depth_estimate: float) -> str:
        for level, ranges in self.severity_levels.items():
            min_depth, max_depth = ranges['depth_range']
            if min_depth <= depth_estimate <= max_depth:
                return level
        return 'low'
    
    def _calculate_risk_score(self, detection: PotholeDetection) -> float:
        base_score = detection.confidence
        
        severity_multiplier = {
            'low': 1.0,
            'medium': 1.5,
            'high': 2.0,
            'critical': 3.0
        }
        
        area_factor = min(detection.area_estimate / 10000, 2.0)
        severity_factor = severity_multiplier.get(detection.severity_level, 1.0)
        
        risk_score = base_score * severity_factor * area_factor
        return min(risk_score, 1.0)
    
    def filter_by_severity(self, detections: List[PotholeDetection], severity: str) -> List[PotholeDetection]:
        return [det for det in detections if det.severity_level == severity]
    
    def filter_by_type(self, detections: List[PotholeDetection], pothole_type: str) -> List[PotholeDetection]:
        return [det for det in detections if det.pothole_type == pothole_type]
    
    def filter_high_risk(self, detections: List[PotholeDetection], threshold: float = 0.7) -> List[PotholeDetection]:
        return [det for det in detections if det.risk_score >= threshold]
    
    def get_detection_statistics(self, detections: List[PotholeDetection]) -> Dict[str, Any]:
        if not detections:
            return {
                'total_detections': 0,
                'severity_distribution': {},
                'average_risk_score': 0.0,
                'total_area': 0.0
            }
        
        severity_counts = {}
        risk_scores = []
        total_area = 0.0
        
        for detection in detections:
            severity = detection.severity_level
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            if detection.risk_score:
                risk_scores.append(detection.risk_score)
            
            if detection.area_estimate:
                total_area += detection.area_estimate
        
        return {
            'total_detections': len(detections),
            'severity_distribution': severity_counts,
            'average_risk_score': np.mean(risk_scores) if risk_scores else 0.0,
            'min_risk_score': np.min(risk_scores) if risk_scores else 0.0,
            'max_risk_score': np.max(risk_scores) if risk_scores else 0.0,
            'total_area': total_area,
            'average_area': total_area / len(detections) if detections else 0.0
        }
    
    def get_tracking_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de tracking"""
        
        if not self.tracks:
            return {
                'total_tracks': 0,
                'stable_tracks': 0,
                'average_track_length': 0.0
            }
        
        track_lengths = [track.total_frames for track in self.tracks.values()]
        stable_tracks = [track for track in self.tracks.values() if track.total_frames >= self.min_track_length]
        
        return {
            'total_tracks': len(self.tracks),
            'stable_tracks': len(stable_tracks),
            'average_track_length': np.mean(track_lengths) if track_lengths else 0.0,
            'max_track_length': np.max(track_lengths) if track_lengths else 0,
            'track_distribution': {
                'short': len([t for t in track_lengths if t < self.min_track_length]),
                'stable': len(stable_tracks),
                'long': len([t for t in track_lengths if t > self.min_track_length * 2])
            }
        }
    
    def draw_detections(self, image: np.ndarray, detections: List[PotholeDetection]) -> np.ndarray:
        output_image = image.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection.bbox
            confidence = detection.confidence
            severity = detection.severity_level
            risk_score = detection.risk_score or 0.0
            
            if severity == 'critical':
                color = (0, 0, 255)
            elif severity == 'high':
                color = (0, 165, 255)
            elif severity == 'medium':
                color = (0, 255, 255)
            else:
                color = (0, 255, 0)
            
            label = f"Buraco: {detection.pothole_type} ({confidence:.2f})"
            label += f" | Severidade: {severity} | Risco: {risk_score:.2f}"
            
            cv2.rectangle(output_image, (x1, y1), (x2, y2), color, 2)
            
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 2)[0]
            cv2.rectangle(output_image, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(output_image, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 2)
        
        return output_image
    
    def generate_road_report(self, detections: List[PotholeDetection]) -> Dict[str, Any]:
        stats = self.get_detection_statistics(detections)
        
        report = {
            'timestamp': time.time(),
            'summary': {
                'total_potholes': stats['total_detections'],
                'road_condition': self._assess_road_condition_from_detections(detections),
                'maintenance_priority': self._assess_maintenance_priority_from_detections(detections)
            },
            'statistics': stats,
            'recommendations': self._generate_recommendations(stats)
        }
        
        return report
    
    def _assess_road_condition(self, stats: Dict[str, Any]) -> str:
        total_potholes = stats['total_detections']
        avg_risk = stats['average_risk_score']
        
        if total_potholes == 0:
            return "excellent"
        elif total_potholes <= 3 and avg_risk <= 0.3:
            return "good"
        elif total_potholes <= 8 and avg_risk <= 0.6:
            return "fair"
        elif total_potholes <= 15 and avg_risk <= 0.8:
            return "poor"
        else:
            return "critical"
    
    def _assess_maintenance_priority(self, stats: Dict[str, Any]) -> str:
        severity_dist = stats['severity_distribution']
        critical_count = severity_dist.get('critical', 0)
        high_count = severity_dist.get('high', 0)
        
        if critical_count > 0:
            return "immediate"
        elif high_count > 2:
            return "high"
        elif high_count > 0:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        recommendations = []
        
        severity_dist = stats['severity_distribution']
        total_area = stats['total_area']
        
        if severity_dist.get('critical', 0) > 0:
            recommendations.append("Intervenção imediata necessária para buracos críticos")
        
        if severity_dist.get('high', 0) > 3:
            recommendations.append("Manutenção urgente recomendada para múltiplos buracos de alta severidade")
        
        if total_area > 50000:
            recommendations.append("Área total de danos significativa - considerar recapeamento")
        
        if not recommendations:
            recommendations.append("Condição da estrada aceitável - manutenção preventiva recomendada")
        
        return recommendations
    
    def cleanup(self):
        if self.model:
            del self.model
            self.model = None
        
        # Limpar tracking
        self.tracks.clear()
        self.frame_history.clear()
