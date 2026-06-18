import os

HF_BASE = os.environ.get("HF_ENDPOINT", "https://huggingface.co")


def hf_url(path: str) -> str:
    base = HF_BASE.rstrip("/")
    return base + path
