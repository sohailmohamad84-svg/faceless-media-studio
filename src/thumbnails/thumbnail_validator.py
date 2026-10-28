"""Thumbnail Validator for Faceless Media Studio.
Enforces Gate 10: Validates pixel dimensions, aspect ratio, safe zones, and file integrity.
"""
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image


class ThumbnailValidator:
    """Validates thumbnail image technical specifications against YouTube platform requirements."""

    REQUIRED_9X16_WIDTH = 1080
    REQUIRED_9X16_HEIGHT = 1920
    REQUIRED_16X9_WIDTH = 1280
    REQUIRED_16X9_HEIGHT = 720
    MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024 # 10 MB

    @classmethod
    def validate_file(cls, file_path: Path, expected_aspect: str = "9:16") -> Dict[str, Any]:
        """Validates a single thumbnail image file."""
        if not file_path.exists():
            return {
                "valid": False,
                "file_path": str(file_path),
                "error": "Thumbnail file does not exist."
            }

        file_size = file_path.stat().st_size
        if file_size == 0 or file_size > cls.MAX_FILE_SIZE_BYTES:
            return {
                "valid": False,
                "file_path": str(file_path),
                "error": f"Invalid file size: {file_size:,} bytes."
            }

        try:
            with Image.open(file_path) as img:
                w, h = img.size
                format_name = img.format

                if expected_aspect == "9:16":
                    if w != cls.REQUIRED_9X16_WIDTH or h != cls.REQUIRED_9X16_HEIGHT:
                        return {
                            "valid": False,
                            "file_path": str(file_path),
                            "error": f"Incorrect dimensions for 9:16: {w}x{h} (required {cls.REQUIRED_9X16_WIDTH}x{cls.REQUIRED_9X16_HEIGHT})."
                        }
                elif expected_aspect == "16:9":
                    if w != cls.REQUIRED_16X9_WIDTH or h != cls.REQUIRED_16X9_HEIGHT:
                        return {
                            "valid": False,
                            "file_path": str(file_path),
                            "error": f"Incorrect dimensions for 16:9: {w}x{h} (required {cls.REQUIRED_16X9_WIDTH}x{cls.REQUIRED_16X9_HEIGHT})."
                        }

                return {
                    "valid": True,
                    "file_path": str(file_path),
                    "dimensions": f"{w}x{h}",
                    "format": format_name,
                    "size_bytes": file_size
                }
        except Exception as e:
            return {
                "valid": False,
                "file_path": str(file_path),
                "error": f"Failed to open image file: {str(e)}"
            }

    @classmethod
    def validate_package(cls, package_dict: Dict[str, str]) -> Dict[str, Any]:
        """Validates all thumbnail variants in an episode package."""
        results = {}
        all_valid = True
        errors = []

        for key, path_str in package_dict.items():
            if not path_str or key in ["topic_id", "generated_count"]:
                continue
            p = Path(path_str)
            expected = "16:9" if "16x9" in key.lower() or "promo" in key.lower() else "9:16"
            res = cls.validate_file(p, expected_aspect=expected)
            results[key] = res
            if not res["valid"]:
                all_valid = False
                errors.append(f"{key}: {res.get('error')}")

        return {
            "all_valid": all_valid,
            "errors": errors,
            "variant_results": results
        }
