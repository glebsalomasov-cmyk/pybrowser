"""Генератор плагинов по-типу DeepSeek Harness:

1. Ты пишешь ИИ желание: "скрывай баннеры" / "считай слова на странице".
2. prompt.py отдаёт модели точное описание API плагинов (шпаргалка) —
   так модель меньше галлюцинирует.
3. Ответ вычищается (убираются ``` и пояснения), проверяется безопасным
   анализатором (sandbox_check), и только потом сохраняется в plugins/.
"""

import re
from pathlib import Path

from ai.client import ask_ai
from ai.prompt import PLUGIN_SYSTEM, build_prompt
from core.sandbox_check import check_code

PLUGINS_DIR = Path(__file__).parent.parent / "plugins"


def generate_plugin(description: str) -> tuple[bool, str]:
    """Вернуть (успех, сообщение). Плагин попадёт в plugins/ и загрузится сам."""
    raw = ask_ai(build_prompt(description), system=PLUGIN_SYSTEM)
    code = _extract_python(raw)

    ok, msg = check_code(code)
    if not ok:
        return False, f"Плагин отклонён проверкой безопасности: {msg}"

    name = _make_name(description)
    PLUGINS_DIR.mkdir(exist_ok=True)
    path = PLUGINS_DIR / f"{name}.py"
    path.write_text(code, encoding="utf-8")
    return True, f"Плагин сохранён: plugins/{path.name} (перезапусти браузер или нажми «Обновить плагины»)"


def _extract_python(text: str) -> str:
    """Вытащить кусок python-кода из ответа модели."""
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return (m.group(1) if m else text).strip()


def _make_name(description: str) -> str:
    words = re.findall(r"[a-zA-Zа-яА-Я0-9]+", description.lower())[:3]
    base = "_".join(words) or "custom"
    n = 1
    while (PLUGINS_DIR / f"{base}.py").exists():
        base = f"{words[0] if words else 'custom'}_{n}"
        n += 1
    return base
