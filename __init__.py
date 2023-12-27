import os
import requests
import subprocess
import sys
from PyQt5.QtWidgets import QAction, QProgressBar, QApplication, QWidget
from PyQt5.QtWidgets import QInputDialog
from pathlib import Path


def classFactory(iface):
    return MinimalPlugin(iface)


class MinimalPlugin:

    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        self.action = QAction('Natural Earth', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action

    def run(self):
        message = """
        Quale dei seguenti pacchetti desidera scaricare?
        1. SHP (576 MB)
        2. SQLite (414 MB)
        3. Geopackage (426 MB)
        4. Grayscale shading based on Prisma artistic filtering (17.16 MB)
        """
        scelta = QInputDialog.getText(None, "Quale dei seguenti pacchetti desidera scaricare?", message)
        if scelta[1]:
            Access(scelta[0])


class Access(QWidget):
    urls = {"1": ["https://naciscdn.org/naturalearth/packages/natural_earth_vector.zip", "EARTH VECTOR"],
            "2": ["https://naciscdn.org/naturalearth/packages/natural_earth_vector.sqlite.zip", "EARTH VECTOR SQLITE"],
            "3": ["https://naciscdn.org/naturalearth/packages/natural_earth_vector.gpkg.zip", "EARTH VECTOR GPKG"],
            "4": ["https://naciscdn.org/naturalearth/50m/raster/PRISMA_SR_50M.zip", "PRISMA"]
            }

    def __init__(self, scelta: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = self.urls[scelta][0]
        self.qgis_filename = self.urls[scelta][1]
        self.response = requests.get(self.url, stream=True)
        self.dimensione_totale = int(self.response.headers.get('content-length', 0))
        self.download_folder = str(Path.home() / "Downloads")
        self.download_filename = os.path.join(str(Path.home() / "Downloads"), f"{self.qgis_filename}.zip")
        # Grafica..
        self.init_progress_bar()

        # Apro la cartella download
        if sys.platform == 'linux':
            subprocess.run(['xdg-open', self.download_folder])
        elif sys.platform == 'win32':
            subprocess.run(['explorer', self.download_folder])

    def init_progress_bar(self):
        # Nuovo widget
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(25, 45, 225, 30)
        self.setGeometry(310, 310, 300, 115)
        self.setWindowTitle(self.qgis_filename)
        self.show()
        # Start il download
        self.Download()

    def Download(self):
        if self.dimensione_totale > 0:
            chunk = 0
            with open(self.download_filename, 'wb') as file:
                for data in self.response.iter_content(chunk_size=1024):
                    size = file.write(data)
                    chunk = chunk + size
                    download_percentage = (chunk / self.dimensione_totale) * 100
                    self.progressBar.setValue(int(download_percentage))
                    QApplication.processEvents()
