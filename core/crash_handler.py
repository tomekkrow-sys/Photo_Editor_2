import platform
import sys
import traceback

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
)


class CrashDialog(QDialog):
    def __init__(self, report: str):
        super().__init__()

        self.setWindowTitle("Photo Editor 2 - Nieoczekiwany błąd")
        self.resize(900, 650)

        self.editor = QPlainTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setPlainText(report)
        self.editor.setTextInteractionFlags(
            Qt.TextSelectableByMouse |
            Qt.TextSelectableByKeyboard
        )

        copy_button = QPushButton("Kopiuj raport")
        close_button = QPushButton("Zamknij")

        copy_button.clicked.connect(
            lambda: QGuiApplication.clipboard().setText(
                self.editor.toPlainText()
            )
        )
        close_button.clicked.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(copy_button)
        buttons.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.editor)
        layout.addLayout(buttons)


def install_exception_handler(version: str = "unknown") -> None:
    def handle(exc_type, exc_value, exc_tb):
        report = (
            f"Photo Editor 2 {version}\n"
            f"Python: {platform.python_version()}\n"
            f"System: {platform.platform()}\n\n"
            + "".join(
                traceback.format_exception(
                    exc_type,
                    exc_value,
                    exc_tb,
                )
            )
        )

        print(report, file=sys.stderr)

        app = QApplication.instance()
        if app is not None:
            CrashDialog(report).exec()

    sys.excepthook = handle
