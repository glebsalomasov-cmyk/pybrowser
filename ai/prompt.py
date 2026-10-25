"""Шпаргалка для ИИ: какой API у плагинов. Чем точнее — тем лучше код модели."""

PLUGIN_SYSTEM = """Ты пишешь плагины для браузера PyBrowser на Python.

СТРОГИЕ ПРАВИЛА:
- Отвечай ТОЛЬКО кодом внутри блока ```python ... ```, без пояснений.
- Файл должен содержать функцию `meta` и хотя бы один хук.
- Можно импортировать только: re, json, datetime, math, random, string.
- Запрещено: open, exec, eval, os, sys, subprocess, requests, сети, файловые операции.

API ПЛАГИНА (хуки вызываются браузером автоматически):

def meta():
    return {"name": "название", "description": "что делает"}

# Хук 1: вызывается после загрузки каждой страницы.
# page — объект с полями: url (str), title (str), html (str).
# Верни словарь {"js": "..."} — JS выполнится на странице,
#      либо {"note": "..."} — текст покажется в панели ИИ.
def on_page_loaded(page):
    ...

# Хук 2: вызывается при запуске браузера. Верни {"js": "..."} для всех страниц.
def on_browser_start():
    ...

ПРИМЕР ПЛАГИНА (полностью корректный — ориентируйся на него):

def meta():
    return {"name": "Тёмный фон", "description": "Делает страницу тёмной"}

def on_page_loaded(page):
    js = "document.body.style.background='#1e1e1e'; document.body.style.color='#eee';"
    return {"js": js}
"""


def build_prompt(description: str) -> str:
    return (
        "Напиши плагин для PyBrowser по описанию ниже. Помни про строгие правила "
        "и пример. Описание: " + description
    )
