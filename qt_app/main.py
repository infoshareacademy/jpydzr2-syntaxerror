from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QDialog, QListWidgetItem

from qt_app.ui.main import Ui_mainWindow
import covid_main


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        self.ui.actionPobierz_dane.triggered.connect(self.download_data)
        self.ui.actionWyswietl_dane.triggered.connect(self.data_show)

    def download_data(self):
        covid_main.data_download()
        print("Pobrano dane")

    def data_show(self):
        pass
