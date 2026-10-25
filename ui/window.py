"""Главное окно браузера: тулбар, вкладки, страница, панель ИИ-ассистента."""

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QLineEdit,
    QPushButton, QTabWidget, QLabel, QTextEdit, QSplitter, QMenu,
)
# ВАЖНО: QtWebEngineWidgets импортируется ДО создания QApplication — иначе краш
from PyQt6.QtWebEngineCore import QWebEngineScript
from PyQt6.QtWebEngineWidgets import QWebEngineView  # noqa: F401

import config
from core.tabs import Tab
from core.storage import add_history, add_bookmark
from core.plugin_manager import PluginManager, Page
from ai.generator import generate_plugin


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.APP_NAME)
        self.resize(1200, 800)

        self.plugins = PluginManager()
        self.plugins.load_all()

        # --- верхняя панель ---
        tb = QToolBar()
        self.addToolBar(tb)
        btn_back = QPushButton("←")
        btn_fwd = QPushButton("→")
        btn_reload = QPushButton("⟳")
        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("Адрес или запрос в поиск…")
        self.urlbar.returnPressed.connect(self.navigate)
        btn_star = QPushButton("☆ В закладки")
        btn_plugins = QPushButton("Плагины ⟳")
        for b in (btn_back, btn_fwd, btn_reload, self.urlbar, btn_star, btn_plugins):
            tb.addWidget(b)
        btn_back.clicked.connect(lambda: self.tab().back())
        btn_fwd.clicked.connect(lambda: self.tab().forward())
        btn_reload.clicked.connect(lambda: self.tab().reload())
        btn_star.clicked.connect(self.bookmark_current)
        btn_plugins.clicked.connect(self.reload_plugins)

        # --- вкладки + страница ---
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # --- панель ИИ внизу ---
        self.ai_log = QTextEdit()
        self.ai_log.setReadOnly(True)
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Попроси ИИ написать плагин, напр.: «скрывай рекламные баннеры»")
        self.ai_input.returnPressed.connect(self.ask_ai)
        ask_btn = QPushButton("Создать плагин 🤖")
        ask_btn.clicked.connect(self.ask_ai)
        ai_row = QHBoxLayout()
        ai_row.addWidget(self.ai_input)
        ai_row.addWidget(ask_btn)
        ai_box = QWidget()
        ai_v = QVBoxLayout(ai_box)
        ai_v.setContentsMargins(4, 4, 4, 4)
        ai_v.addWidget(QLabel("<b>ИИ-ассистент плагинов</b>"))
        ai_v.addWidget(self.ai_log)
        ai_v.addLayout(ai_row)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.tabs)
        splitter.addWidget(ai_box)
        splitter.setSizes([650, 200])
        self.setCentralWidget(splitter)

        # меню "Файл"
        m_file = self.menuBar().addMenu("Файл")
        act_new = QAction("Новая вкладка", self)
        act_new.setShortcut("Ctrl+T")
        act_new.triggered.connect(lambda: self.new_tab(config.HOME_URL))
        act_quit = QAction("Выход", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.close)
        m_file.addAction(act_new)
        m_file.addAction(act_quit)

        self.new_tab(config.HOME_URL)
        self.ai_log.append(f"Загружено плагинов: {len(self.plugins.plugins)} — {', '.join(self.plugins.names()) or 'нет'}")

    # ---------- вкладки ----------
    def tab(self) -> Tab:
        return self.tabs.currentWidget()

    def new_tab(self, url: str = ""):
        t = Tab(url)
        idx = self.tabs.addTab(t, "+")
        t.titleChanged.connect(lambda title, w=t: self._rename(w, title))
        t.urlChanged.connect(self._on_url_changed)
        t.loadFinished.connect(lambda ok, w=t: self._page_ready(w, ok))
        self.tabs.setCurrentIndex(idx)
        return t

    def close_tab(self, idx):
        if self.tabs.count() <= 1:
            return self.close()
        w = self.tabs.widget(idx)
        self.tabs.removeTab(idx)
        w.deleteLater()

    def on_tab_changed(self, idx):
        t = self.tabs.widget(idx)
        if t:
            self.urlbar.setText(t.url().toString())

    def _rename(self, widget, title):
        idx = self.tabs.indexOf(widget)
        if idx >= 0:
            self.tabs.setTabText(idx, title[:25] or "Страница")

    # ---------- навигация ----------
    def navigate(self):
        text = self.urlbar.text().strip()
        if text:
            self.tab().go_to(text)

    def _on_url_changed(self, qurl: QUrl):
        self.urlbar.setText(qurl.toString())

    def bookmark_current(self):
        t = self.tab()
        add_bookmark(t.url().toString(), t.title())
        self.statusBar().showMessage("Добавлено в закладки", 2000)

    # ---------- плагины + ИИ ----------
    def reload_plugins(self):
        self.plugins.load_all()
        msg = f"Плагины обновлены: {', '.join(self.plugins.names()) or 'нет'}"
        if self.plugins.errors:
            msg += " | ошибки: " + "; ".join(self.plugins.errors)
        self.ai_log.append(msg)

    def _page_ready(self, webview: Tab, ok: bool):
        if not ok:
            return
        url = webview.url().toString()
        add_history(url, webview.title())

        # получаем html страницы асинхронно, потом гоняем хуки
        page = webview.page()
        def got_html(html: str):
            p = Page(url=url, title=webview.title(), html=html)
            for name, res in self.plugins.run_on_page_loaded(p):
                if "js" in res:
                    script = QWebEngineScript()
                    script.setName(f"plugin_{name}")
                    script.setSourceCode(res["js"])
                    script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
                    script.setRunsOnSubFrames(False)
                    page.userScripts().insert(script)
                if "note" in res:
                    self.ai_log.append(f"[{name}] {res['note']}")
            if self.plugins.errors:
                self.ai_log.append("[ошибки плагинов] " + "; ".join(self.plugins.errors[-3:]))
        page.toHtml(got_html)

    def ask_ai(self):
        desc = self.ai_input.text().strip()
        if not desc:
            return
        self.ai_input.clear()
        self.ai_log.append(f"<b>Ты:</b> {desc}")
        self.ai_log.append("<i>ИИ пишет код… (может занять минуту)</i>")
        ok, msg = generate_plugin(desc)
        color = "#2e7d32" if ok else "#c62828"
        self.ai_log.append(f"<span style='color:{color}'>{msg}</span>")
        if ok:
            self.reload_plugins()
