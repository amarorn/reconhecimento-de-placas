#!/usr/bin/env python3
import sys
from pathlib import Path
import cv2
import numpy as np

from kedro.framework.session import KedroSession
from kedro.framework.startup import bootstrap_project


def main(image_path: str):
    project_path = Path(__file__).resolve().parents[1]
    bootstrap_project(project_path)

    with KedroSession.create("reconhecimento-de-placas", project_path=project_path) as session:
        context = session.load_context()
        pipeline = context.pipelines.get("__default__") or context.pipelines.get("pipeline")
        if pipeline is None:
            # build pipeline programaticamente
            from vision.kedro_pipeline.pipeline import create_pipeline

            context.pipelines.register("__default__", create_pipeline())
            pipeline = context.pipelines["__default__"]

        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Imagem não encontrada: {image_path}")

        # Carregar datasets em memória
        context.catalog.save("raw_image", image)

        # Executar
        session.run(pipeline_name="__default__")

        # Coletar resultados
        integrated = context.catalog.load("integrated_results")
        print({"integrated_results": integrated})


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: scripts/run_kedro_pipeline.py <caminho_da_imagem>")
        sys.exit(1)
    main(sys.argv[1])

