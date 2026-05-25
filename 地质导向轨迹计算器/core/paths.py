import pathlib

_current_file = pathlib.Path(__file__).resolve()
PROJECT_ROOT = _current_file.parent.parent

UI_DIR = PROJECT_ROOT / "ui"
VIEWS_DIR = UI_DIR / "views"
# 新增：UI设计文件存放目录
FORMS_DIR = UI_DIR / "forms"