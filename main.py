"""
PyBrowser — главный файл. Запускать именно его (правой кнопкой -> Run 'main').

Что происходит при запуске:
1. Открывается окно с веб-страницей (движок Chromium, встроенный в PyQt).
2. Вверху: кнопки "назад/вперёд", адресная строка, кнопка "Перевести ИИ".
3. Внизу: панель ИИ-ассистента (как DeepSeek Harness) — он умеет:
   - сам писать плагины для браузера по твоей просьбе,
   - сохранять их в папку plugins/, браузер подхватывает их автоматически.
"""

import sys
from pathlib import Path

# чтобы импорты работали из любого места
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from PyQt6.QtWidgets import QApplication
from ui.window import BrowserWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PyBrowser")
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
