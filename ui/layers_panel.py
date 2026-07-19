from PySide6.QtWidgets import QListWidget


class LayersPanel(QListWidget):
    """Panel wyświetlający listę warstw."""

    def __init__(self, parent=None):
        super().__init__(parent)

    def set_layers(self, names: list[str]) -> None:
        """Wyświetla listę nazw warstw."""

        self.clear()
        self.addItems(names)
