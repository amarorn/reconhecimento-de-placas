#!/usr/bin/env python3
from typing import Any, Dict, List
import numpy as np

from ..preprocessing.image_preprocessor import ImagePreprocessor
from ..detection.yolo_detector import YOLODetector, DetectionResult
from ..ocr.text_extractor import TextExtractor


def node_preprocess(image: np.ndarray, preprocessor_config: Dict[str, Any]) -> np.ndarray:
    pre = ImagePreprocessor(preprocessor_config)
    return pre.preprocess(image).processed_image


def node_detect(image: np.ndarray, detector_config: Dict[str, Any]) -> List[DetectionResult]:
    det = YOLODetector(detector_config)
    return det.detect(image)


def node_ocr(image: np.ndarray, detections: List[DetectionResult], ocr_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    regions = [{"bbox": d.bbox} for d in detections]
    ocr = TextExtractor(ocr_config)
    batch = ocr.extract_text(image, regions)
    return [
        {
            "text": r.text,
            "confidence": r.confidence,
            "bbox": r.bbox,
            "language": r.language,
        }
        for r in batch.text_results
    ]


def node_integrate(detections: List[DetectionResult], ocr_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def iou(b1, b2):
        x1, y1, w1, h1 = b1
        x2, y2, w2, h2 = b2
        xl = max(x1, x2)
        yt = max(y1, y2)
        xr = min(x1 + w1, x2 + w2)
        yb = min(y1 + h1, y2 + h2)
        inter = max(0, xr - xl) * max(0, yb - yt)
        union = w1 * h1 + w2 * h2 - inter
        return inter / union if union > 0 else 0.0

    integrated = []
    for d in detections:
        matches = [o for o in ocr_results if iou(d.bbox, o["bbox"]) > 0.3]
        primary = None
        if matches:
            matches = sorted(matches, key=lambda m: m["confidence"], reverse=True)
            primary = matches[0]["text"]
        integrated.append(
            {
                "detection": {
                    "bbox": d.bbox,
                    "confidence": d.confidence,
                    "class_id": d.class_id,
                    "class_name": d.class_name,
                },
                "texts": matches,
                "primary_text": primary,
            }
        )
    return integrated

