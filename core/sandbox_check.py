"""Проверка безопасности сгенерированного кода плагина.

Мы НЕ исполняем код сразу. Сначала читаем его как текст и разбираем
модулем `ast` (дерево кода). Если внутри есть опасные конструкции —
плагин не сохраняется. Это защита от галлюцинаций ИИ и случайной дыры.
"""

import ast

# что плагину нельзя в принципе
FORBIDDEN_IMPORTS = {"os", "sys", "subprocess", "socket", "shutil", "pathlib", "requests", "urllib"}
FORBIDDEN_NAMES = {"open", "exec", "eval", "compile", "__import__", "globals", "locals", "input"}


def check_code(code: str) -> tuple[bool, str]:
    """Вернуть (ok, причина_отказа). ok=True — код безопасен."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"синтаксическая ошибка ({e})"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in FORBIDDEN_IMPORTS:
                    return False, f"запрещённый импорт: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root in FORBIDDEN_IMPORTS:
                return False, f"запрещённый импорт: {node.module}"
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id in FORBIDDEN_NAMES:
                return False, f"запрещённая функция: {fn.id}"
        elif isinstance(node, ast.Attribute):
            # защита от трюков вида getattr(os, "sys") ... __subclasses__
            if node.attr.startswith("__") and node.attr.endswith("__"):
                return False, f"магический атрибут: {node.attr}"

    if len(code.splitlines()) > 120:
        return False, "код слишком длинный (>120 строк)"

    return True, ""
