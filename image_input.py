"""
modules/image_input.py
──────────────────────
Handles all image input for the Gemini Coding Agent.

Supports:
  - Local image files (PNG, JPEG, WEBP, GIF, BMP)
  - Remote image URLs (auto-downloaded)
  - Base64-encoded image strings

The module returns a `google.genai.types.Part` object ready to be included
in a Gemini API request.
"""

import os
import io
import base64
import logging
import mimetypes
import urllib.request
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Supported image MIME types
IMAGE_MIME_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
}

MAX_IMAGE_SIZE_MB = 20  # Gemini's limit per image


def load_image_part(source: str):
    """
    Load an image from a local file path or URL and return a Gemini Part object.

    Args:
        source: Local file path or HTTP/HTTPS URL to the image.

    Returns:
        A google.genai.types.Part with inline_data containing the image.
    """
    from google.genai import types

    if source.startswith("http://") or source.startswith("https://"):
        image_bytes, mime_type = _load_from_url(source)
    else:
        image_bytes, mime_type = _load_from_file(source)

    # Check size
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > MAX_IMAGE_SIZE_MB:
        raise ValueError(
            f"Image is too large ({size_mb:.1f} MB). "
            f"Maximum allowed size is {MAX_IMAGE_SIZE_MB} MB."
        )

    logger.info(f"Image loaded: {size_mb:.2f} MB, type: {mime_type}")

    return types.Part(
        inline_data=types.Blob(
            mime_type=mime_type,
            data=image_bytes,
        )
    )


def _load_from_file(file_path: str):
    """Load image bytes and MIME type from a local file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {file_path}")

    suffix = path.suffix.lower()
    mime_type = IMAGE_MIME_TYPES.get(suffix)
    if not mime_type:
        # Try to guess from content
        guessed, _ = mimetypes.guess_type(file_path)
        if guessed and guessed.startswith("image/"):
            mime_type = guessed
        else:
            raise ValueError(
                f"Unsupported image format: {suffix}. "
                f"Supported: {', '.join(IMAGE_MIME_TYPES.keys())}"
            )

    with open(file_path, "rb") as f:
        image_bytes = f.read()

    return image_bytes, mime_type


def _load_from_url(url: str):
    """Download image bytes and MIME type from a URL."""
    logger.info(f"Downloading image from URL: {url}")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "GeminiCodingAgent/1.0"},
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            content_type = response.headers.get("Content-Type", "image/jpeg")
            # Strip parameters (e.g., "image/jpeg; charset=utf-8")
            mime_type = content_type.split(";")[0].strip()
            image_bytes = response.read()
    except Exception as e:
        raise RuntimeError(f"Failed to download image from {url}: {e}")

    return image_bytes, mime_type


def describe_image(source: str, context: Optional[str] = None) -> str:
    """
    Ask Gemini to describe an image in detail for use as context.
    Useful for pre-processing UI mockups before code generation.

    Args:
        source: Local file path or URL to the image.
        context: Optional additional context about what to focus on.

    Returns:
        A detailed text description of the image.
    """
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    image_part = load_image_part(source)
    focus = context or (
        "Describe this image in detail, focusing on: "
        "UI layout and components, color scheme, typography, "
        "navigation structure, data displayed, and any text visible. "
        "Be specific and technical."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(
                role="user",
                parts=[image_part, types.Part(text=focus)],
            )
        ],
    )

    return response.text.strip()
