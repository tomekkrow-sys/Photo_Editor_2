from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget


class LayersPanel(QListWidget):
    """Panel wyświetlający listę warstw."""

    layer_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.currentRowChanged.connect(
            self.layer_selected.emit
        )

    def set_layers(self, names: list[str]) -> None:
        """Wyświetla listę nazw warstw."""

        current = self.currentRow()

        self.blockSignals(True)
        self.clear()
        self.addItems(names)

        if names:
            if current < 0 or current >= len(names):
                current = len(names) - 1

            self.setCurrentRow(current)

        self.blockSignals(False)
