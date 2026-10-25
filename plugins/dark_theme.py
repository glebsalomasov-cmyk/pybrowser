"""Пример плагина. Лежит в plugins/ — браузер подхватит его автоматически.

Чтобы отключить — удали файл или переименуй в dark_theme.py.off
"""


def meta():
    return {"name": "Тёмный фон", "description": "Делает страницу тёмной для глаз"}


def on_page_loaded(page):
    js = (
        "document.documentElement.style.filter='invert(1) hue-rotate(180deg)';"
        "document.querySelectorAll('img,video').forEach("
        "e=>e.style.filter='invert(1) hue-rotate(180deg)');"
    )
    return {"js": js}
