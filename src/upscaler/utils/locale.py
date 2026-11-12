from pathlib import Path

from PySide6.QtCore import QLibraryInfo, QLocale, QTranslator
from PySide6.QtWidgets import QApplication

LOCALE_DIR = Path(__file__).parent.parent / "gui" / "locale"


def install_translators(app: QApplication) -> None:
    """Install the application translation and Qt's base translation."""
    locale = QLocale.system()

    # Try full locale first, then language only: de_DE -> de
    candidates = []
    name = locale.name()
    if name:
        candidates.append(name)
    if "_" in name:
        candidates.append(name.split("_")[0])

    for candidate in candidates:
        translator = QTranslator(app)
        if translator.load(f"upscale_gui_{candidate}", str(LOCALE_DIR)):
            app.installTranslator(translator)
            break

    qt_translator = QTranslator(app)
    qt_translations_dir = QLibraryInfo.path(QLibraryInfo.TranslationsPath)
    if qt_translator.load(f"qtbase_{locale.name()}", qt_translations_dir):
        app.installTranslator(qt_translator)
