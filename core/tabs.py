"""Вкладки браузера. Каждая вкладка = своя веб-страница (движок Chromium)."""

from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView


class Tab(QWebEngineView):
    """Одна вкладка. Простая обёртка над веб-страницей."""

    def __init__(self, url: str = ""):
        super().__init__()
        if url:
            self.go_to(url)

    def go_to(self, url: str):
        # если пользователь написал "кот" вместо адреса — делаем поиск
        if "." not in url or " " in url:
            url = "https://duckduckgo.com/?q=" + url.replace(" ", "+")
        elif not url.startswith(("http://", "https://")):
            url = "https://" + url
        self.load(QUrl(url))

    @property
    def title_text(self) -> str:
        t = self.title()
        return t[:30] + "…" if len(t) > 30 else (t or "Новая вкладка")
