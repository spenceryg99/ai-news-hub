TOPIC_RULES = [
    {
        "id": "llm",
        "name": "\u5927\u8bed\u8a00\u6a21\u578b",
        "emoji": "\U0001f9e0",
        "keywords": [
            "llm", "large language model", "gpt", "transformer", "attention",
            "llama", "mistral", "qwen", "deepseek", "gemma", "olmo",
            "pretrain", "pre-train", "language model", "foundation model",
            "reasoning", "chain-of-thought", "prompt", "in-context learning",
            "instruction tuning", "alignment", "rlhf", "dpo", "sft",
        ],
    },
    {
        "id": "agent",
        "name": "AI Agent",
        "emoji": "\U0001f916",
        "keywords": [
            "agent", "tool use", "tool calling", "function calling",
            "autonomous", "multi-agent", "agentic", "react", "planning",
            "mcp", "model context protocol", "computer use", "browser agent",
            "code agent", "assistant", "orchestration", "workflow",
        ],
    },
    {
        "id": "multimodal",
        "name": "\u591a\u6a21\u6001",
        "emoji": "\U0001f5bc\ufe0f",
        "keywords": [
            "multimodal", "vision-language", "vlm", "image generation",
            "text-to-image", "text-to-video", "diffusion", "stable diffusion",
            "dalle", "sora", "video generation", "speech", "whisper",
            "voice", "audio", "tts", "asr",
        ],
    },
    {
        "id": "vision",
        "name": "\u89c6\u89c9",
        "emoji": "\U0001f441\ufe0f",
        "keywords": [
            "computer vision", "object detection", "segmentation",
            "image recognition", "visual", "ocr", "depth estimation",
            "nerf", "3d", "point cloud", "pose estimation",
        ],
    },
    {
        "id": "code",
        "name": "\u4ee3\u7801\u4e0e\u5f00\u53d1",
        "emoji": "\U0001f4bb",
        "keywords": [
            "code generation", "coding agent", "program synthesis",
            "repository", "github", "open source", "developer tool",
            "ide", "debug", "code review", "cli", "terminal",
        ],
    },
    {
        "id": "rag",
        "name": "RAG \u4e0e\u68c0\u7d22",
        "emoji": "\U0001f50d",
        "keywords": [
            "rag", "retrieval", "search", "embedding", "vector database",
            "knowledge base", "document", "index", "semantic search",
        ],
    },
    {
        "id": "training",
        "name": "\u8bad\u7ec3\u4e0e\u4f18\u5316",
        "emoji": "\u2699\ufe0f",
        "keywords": [
            "fine-tune", "fine tuning", "quantization", "distillation",
            "pruning", "lora", "qlora", "training", "optimization",
            "efficient", "memory", "speedup", "accelerate",
        ],
    },
    {
        "id": "inference",
        "name": "\u63a8\u7406\u4e0e\u90e8\u7f72",
        "emoji": "\U0001f680",
        "keywords": [
            "inference", "deploy", "serving", "vllm", "tensorrt",
            "onnx", "openvino", "edge", "mobile", "on-device",
            "gguf", "llama.cpp", "ollama", "container",
        ],
    },
    {
        "id": "security",
        "name": "\u5b89\u5168\u4e0e\u6cbb\u7406",
        "emoji": "\U0001f6e1\ufe0f",
        "keywords": [
            "safety", "alignment", "jailbreak", "red team", "bias",
            "fairness", "governance", "regulation", "policy",
            "responsible ai", "ethics", "privacy", "hallucination",
        ],
    },
    {
        "id": "science",
        "name": "\u79d1\u5b66\u4e0e\u533b\u7597",
        "emoji": "\U0001f52c",
        "keywords": [
            "drug discovery", "protein", "biology", "genomics",
            "molecule", "material", "scientific", "medical",
            "healthcare", "clinical", "chemistry",
        ],
    },
    {
        "id": "robotics",
        "name": "\u673a\u5668\u4eba",
        "emoji": "\U0001f916",
        "keywords": [
            "robot", "robotics", "embodied", "manipulation",
            "navigation", "control", "simulation", "sim-to-real",
        ],
    },
]


def classify_item(item: dict) -> list[str]:
    text = (
        (item.get("title") or "")
        + " " + (item.get("description") or "")
        + " " + (item.get("summary") or "")
        + " " + (item.get("abstract") or "")
        + " " + " ".join(item.get("categories", []))
        + " " + " ".join(item.get("topics", item.get("tags", [])))
    ).lower()

    matched = []
    for topic in TOPIC_RULES:
        for kw in topic["keywords"]:
            if kw in text:
                matched.append(topic["id"])
                break
    return matched if matched else ["general"]


def get_topic_info(topic_id: str) -> dict:
    for t in TOPIC_RULES:
        if t["id"] == topic_id:
            return t
    return {"id": "general", "name": "\u5176\u4ed6", "emoji": "\U0001f4ac", "keywords": []}
