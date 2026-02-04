---
name: captcha-recognition
description: Recognize captcha codes from images using vision LLM. Use when need to identify verification codes for automated login or form submission.
---

# Captcha Recognition

## Usage

```bash
# python -m pip install Pillow
python scripts/recognize.py <image_path> <llm_url> <api_key> <model_name>
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| image_path | Path to captcha image file |
| llm_url | Vision LLM API endpoint URL |
| api_key | API key for authentication |
| model_name | Model name for vision recognition |

## Example

```bash
python scripts/recognize.py "captcha.png" "https://api.siliconflow.cn/v1/chat/completions" "sk-xxx" "Pro/moonshotai/Kimi-K2.5"
```

## Notes

- Image will be compressed to <0.5MB using PIL before sending to LLM
- Only outputs the recognized captcha code to console
- Compatible with OpenAI-compatible API endpoints
