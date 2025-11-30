import os

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer

class InfoWindow(QDialog):
    def __init__(self, pet):
        super().__init__()

        self.pet = pet
        self.setWindowTitle(f"{pet.name.capitalize()} — Info")
        self.setMinimumWidth(250)
        self.setStyleSheet(self.info_style())

        self.build_ui()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(100)
    
    def build_ui(self):
        layout = QVBoxLayout()

        self.name_label = QLabel()
        self.level_label = QLabel()
        self.evo_label = QLabel()

        layout.addWidget(self.name_label)
        layout.addWidget(self.level_label)
        layout.addWidget(self.evo_label)

        self.setLayout(layout)

        self.update_info()

    def info_style(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_dir, "../stylesheets/info_window.qss"), "r") as f:
            style = f.read()

        return style

    def update_info(self):
        self.name_label.setText(f"Nome: {self.pet.name.capitalize()}")
        self.level_label.setText(f"Nível: {self.pet.level}")
        self.evo_label.setText(f"Evolução: {self.pet.evolution_stage}")