"""Клиент для ИИ. Работает с локальным Ollama или облачным DeepSeek/OpenAI.

Никаких библиотек не просит — использует только стандартный urllib из Python.
"""

import json
import urllib.request

import config


def ask_ai(prompt: str, system: str = "Ты — полезный помощник.") -> str:
    """Задать вопрос ИИ и вернуть ответ текстом."""
    if config.USE_OLLAMA:
        return _ask_ollama(prompt, system)
    if config.USE_CLOUD and config.CLOUD_API_KEY:
        return _ask_cloud(prompt, system)
    return "ИИ не настроен: включи Ollama или впиши ключ в config.py"


def _ask_ollama(prompt: str, system: str) -> str:
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }
    return _post("http://localhost:11434/api/chat", payload,
                 lambda d: d["message"]["content"])


def _ask_cloud(prompt: str, system: str) -> str:
    url = config.CLOUD_BASE_URL.rstrip("/") + "/chat/completions"
    payload = {
        "model": config.CLOUD_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }
    headers = {"Authorization": f"Bearer {config.CLOUD_API_KEY}"}
    return _post(url, payload, lambda d: d["choices"][0]["message"]["content"], headers)


def _post(url: str, payload: dict, extract, headers: dict | None = None) -> str:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return extract(json.loads(resp.read().decode("utf-8"))).strip()
    except Exception as e:  # сеть недоступна, Ollama не запущен и т.п.
        return f"[Ошибка связи с ИИ] {e}"
