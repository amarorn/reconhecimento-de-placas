#!/usr/bin/env python3
from kedro.pipeline import Pipeline, node
from .nodes import node_preprocess, node_detect, node_ocr, node_integrate


def create_pipeline() -> Pipeline:
    return Pipeline(
        [
            node(
                func=node_preprocess,
                inputs=["raw_image", "params:preprocessor"],
                outputs="preprocessed_image",
                name="preprocess_image",
            ),
            node(
                func=node_detect,
                inputs=["preprocessed_image", "params:detector"],
                outputs="detections",
                name="detect_objects",
            ),
            node(
                func=node_ocr,
                inputs=["preprocessed_image", "detections", "params:ocr"],
                outputs="ocr_results",
                name="extract_text",
            ),
            node(
                func=node_integrate,
                inputs=["detections", "ocr_results"],
                outputs="integrated_results",
                name="integrate_results",
            ),
        ]
    )

