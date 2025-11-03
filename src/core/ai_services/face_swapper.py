"""
Face swapping service using InsightFace.

Swaps faces between images to maintain character consistency.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional

import insightface
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model

from src.core.logging import get_logger

logger = get_logger(__name__)


class FaceSwapper:
    """
    Face swapping service using InsightFace INSwapper model.

    Swaps the face from a source image to a target image while maintaining
    the target's pose, lighting, and background.
    """

    def __init__(self, model_name: str = "inswapper_128.onnx"):
        """
        Initialize face swapper.

        Args:
            model_name: Name of the face swapping model
        """
        self.logger = get_logger(__name__)

        # Initialize face analysis (for detection)
        self.logger.info("Initializing FaceAnalysis...")
        self.app = FaceAnalysis(name='buffalo_l')
        self.app.prepare(ctx_id=0, det_size=(640, 640))

        # Initialize face swapper model
        self.logger.info(f"Loading face swap model: {model_name}")
        # Use simple model name without path for auto-download
        self.swapper = insightface.model_zoo.get_model(
            model_name,
            download=True,
            download_zip=True
        )

        self.logger.info("FaceSwapper initialized successfully")

    def _get_model_path(self, model_name: str) -> str:
        """
        Get path to InsightFace model.

        Args:
            model_name: Name of the model

        Returns:
            Path to model file
        """
        # InsightFace models are stored in ~/.insightface/models/
        home = Path.home()
        model_dir = home / ".insightface" / "models" / "buffalo_l"
        model_dir.mkdir(parents=True, exist_ok=True)

        model_path = model_dir / model_name
        return str(model_path)

    def swap_face(
        self,
        source_image_path: str,
        target_image_path: str,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Swap face from source image to target image.

        Args:
            source_image_path: Path to image containing the face to copy
            target_image_path: Path to image where face will be replaced
            output_path: Path to save the result (if None, will auto-generate)

        Returns:
            Path to the output image
        """
        self.logger.info(f"Swapping face: {source_image_path} -> {target_image_path}")

        # Read images
        source_img = cv2.imread(source_image_path)
        target_img = cv2.imread(target_image_path)

        if source_img is None:
            raise ValueError(f"Failed to read source image: {source_image_path}")
        if target_img is None:
            raise ValueError(f"Failed to read target image: {target_image_path}")

        # Detect faces
        source_faces = self.app.get(source_img)
        target_faces = self.app.get(target_img)

        if len(source_faces) == 0:
            raise ValueError(f"No face detected in source image: {source_image_path}")
        if len(target_faces) == 0:
            raise ValueError(f"No face detected in target image: {target_image_path}")

        # Use the first detected face
        source_face = source_faces[0]
        target_face = target_faces[0]

        self.logger.info(f"Detected {len(source_faces)} face(s) in source, {len(target_faces)} face(s) in target")

        # Swap face
        result = self.swapper.get(target_img, target_face, source_face, paste_back=True)

        # Generate output path if not provided
        if output_path is None:
            target_path = Path(target_image_path)
            output_path = str(
                target_path.parent / f"{target_path.stem}_swapped{target_path.suffix}"
            )

        # Save result
        cv2.imwrite(output_path, result)

        self.logger.info(f"Face swap complete: {output_path}")

        return output_path

    def swap_face_batch(
        self,
        source_image_path: str,
        target_image_paths: list[str],
        output_dir: Optional[str] = None,
    ) -> list[str]:
        """
        Swap face from source to multiple target images.

        Args:
            source_image_path: Path to image containing the face to copy
            target_image_paths: List of paths to images where face will be replaced
            output_dir: Directory to save results (if None, will use target dirs)

        Returns:
            List of paths to output images
        """
        self.logger.info(f"Batch face swap: {len(target_image_paths)} targets")

        output_paths = []

        for target_path in target_image_paths:
            try:
                if output_dir:
                    target_name = Path(target_path).name
                    output_path = str(Path(output_dir) / target_name)
                else:
                    output_path = None

                result_path = self.swap_face(
                    source_image_path,
                    target_path,
                    output_path
                )
                output_paths.append(result_path)

            except Exception as e:
                self.logger.error(f"Failed to swap face for {target_path}: {e}")
                # Continue with remaining images

        self.logger.info(f"Batch complete: {len(output_paths)}/{len(target_image_paths)} successful")

        return output_paths


# Convenience function
def swap_anchor_faces(
    reference_image: str,
    target_images: list[str],
    output_dir: Optional[str] = None,
) -> list[str]:
    """
    Swap anchor face from reference to multiple target images.

    Args:
        reference_image: Path to reference image (e.g., intro image)
        target_images: List of target image paths to swap face into
        output_dir: Directory to save results

    Returns:
        List of output image paths
    """
    swapper = FaceSwapper()
    return swapper.swap_face_batch(reference_image, target_images, output_dir)
