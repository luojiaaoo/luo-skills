#!/usr/bin/env python3
"""Captcha recognition script using vision LLM."""

import argparse
import base64
import json
import os
import sys
from pathlib import Path

from PIL import Image


def compress_image(
    image_path: str, max_size_mb: float = 0.5, max_dim: int = 1024
) -> str:
    """Compress image to specified size using PIL."""
    img = Image.open(image_path)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    compressed_path = image_path
    quality = 85
    while True:
        img.save(compressed_path, "JPEG", quality=quality)
        file_size = os.path.getsize(compressed_path)
        if file_size < max_size_mb * 1024 * 1024 or quality <= 30:
            break
        quality -= 5

    return compressed_path


def encode_image(image_path: str) -> str:
    """Encode image to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def recognize_captcha(
    image_path: str, llm_url: str, api_key: str, model_name: str
) -> str:
    """Recognize captcha using vision LLM API."""
    compressed_path = compress_image(image_path)
    base64_image = encode_image(compressed_path)

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "识别图片中的验证码，只输出验证码内容，不要任何其他文字。",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": 50,
    }

    import urllib.request

    req = urllib.request.Request(
        llm_url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["choices"][0]["message"]["content"].strip()


def main():
    parser = argparse.ArgumentParser(description="Recognize captcha using vision LLM")
    parser.add_argument("image_path", help="Path to captcha image file")
    parser.add_argument("llm_url", help="Vision LLM API endpoint URL")
    parser.add_argument("api_key", help="API key for authentication")
    parser.add_argument("model_name", help="Model name for vision recognition")
    args = parser.parse_args()

    captcha = recognize_captcha(
        args.image_path, args.llm_url, args.api_key, args.model_name
    )
    print(captcha)


if __name__ == "__main__":
    main()
