"""Менеджер плагинов: находит все .py в папке plugins/, загружает их и вызывает хуки.

Плагин — обычный Python-файл с функциями meta() и хуками on_page_loaded(page).
Загрузка динамическая: положил файл в папку — он подхватился.
"""

import importlib.util
from dataclasses import dataclass
from pathlib import Path

PLUGINS_DIR = Path(__file__).parent.parent / "plugins"


@dataclass
class Page:
    """То, что видит плагин про текущую страницу."""
    url: str
    title: str
    html: str


class PluginManager:
    def __init__(self):
        self.plugins: list = []      # [(путь, модуль, meta), ...]
        self.errors: list[str] = []

    def load_all(self):
        """Загрузить/перезагрузить все плагины из папки plugins/."""
        self.plugins.clear()
        self.errors.clear()
        if not PLUGINS_DIR.exists():
            return
        for path in sorted(PLUGINS_DIR.glob("*.py")):
            try:
                spec = importlib.util.spec_from_file_location(path.stem, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                meta = module.meta() if hasattr(module, "meta") else {"name": path.stem}
                # храним имя файла строкой — не путаем с полями модуля
                self.plugins.append((path.name, module, meta))
            except Exception as e:
                self.errors.append(f"{path.name}: {e}")

    def names(self) -> list[str]:
        return [m.get("name", fname) for fname, _, m in self.plugins]

    def run_on_browser_start(self) -> list[str]:
        """Хук при старте. Возвращает список js-строк для внедрения."""
        js_list = []
        for _, module, _ in self.plugins:
            hook = getattr(module, "on_browser_start", None)
            if callable(hook):
                try:
                    res = hook() or {}
                    if "js" in res:
                        js_list.append(res["js"])
                except Exception as e:
                    self.errors.append(f"on_browser_start: {e}")
        return js_list

    def run_on_page_loaded(self, page: Page) -> list[tuple[str, dict]]:
        """Хук после загрузки страницы. Возвращает [(имя_плагина, результат)]."""
        results = []
        for fname, module, meta in self.plugins:
            hook = getattr(module, "on_page_loaded", None)
            if callable(hook):
                try:
                    results.append((meta.get("name", fname), hook(page) or {}))
                except Exception as e:
                    self.errors.append(f"{fname}.on_page_loaded: {e}")
        return results
