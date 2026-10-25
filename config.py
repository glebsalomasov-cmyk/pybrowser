"""Настройки браузера. Меняй значения здесь — всё применится после перезапуска."""

APP_NAME = "PyBrowser"
HOME_URL = "https://duckduckgo.com"   # стартовая страница

# --- ИИ (генератор плагинов) ---
# Можно использовать бесплатный локальный Ollama (без ключа и без интернета):
#   1) установи ollama.com  2) в терминале: ollama pull qwen2.5-coder:3b
USE_OLLAMA = True
OLLAMA_MODEL = "qwen2.5-coder:3b"

# Или облачной моделью (OpenAI-совместимый API, например DeepSeek):
USE_CLOUD = False
CLOUD_API_KEY = ""          # вставь сюда ключ, e.g. "sk-..."
CLOUD_BASE_URL = "https://api.deepseek.com"
CLOUD_MODEL = "deepseek-coder"

MAX_PLUGIN_LINES = 120      # ограничение на размер сгенерированного плагина
