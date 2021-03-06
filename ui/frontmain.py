import sys

import PyQt6
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon  # For import of ico file
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QGridLayout, QFileDialog, QTextEdit
from pathlib import Path


class RdfApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(800, 500))
        self.setWindowTitle('CECS 571 - Project 2')
        self.setWindowIcon(QIcon("CSULB.ico"))

        # Create a QHBoxLayout instance
        layout = QGridLayout()

        # File Input LineEdit
        self.fileLine = QLineEdit(self)
        self.fileLine.resize(254, 32)
        self.fileLine.setText('Enter csv file...')
        self.fileLine.setStyleSheet("color: gray;font-size:12pt")
        self.fileLine.setReadOnly(True)
        layout.addWidget(self.fileLine, 0, 0)

        # File Input Button
        self.uploadButton = QPushButton('Upload', self)
        self.uploadButton.setStyleSheet("font-size:12pt")
        self.uploadButton.resize(100, 32)
        self.uploadButton.move(50, 50)
        self.uploadButton.clicked.connect(self.clickMethod)
        layout.addWidget(self.uploadButton, 0, 2)

        # Close Button
        self.uploadButton = QPushButton('Close', self)
        self.uploadButton.setStyleSheet("font-size:12pt")
        self.uploadButton.resize(100, 32)
        self.uploadButton.move(50, 50)
        self.uploadButton.clicked.connect(self.closeIt)
        layout.addWidget(self.uploadButton, 2, 2)

        self.LeftTextEdit = QTextEdit()
        self.RightTextEdit = QTextEdit()
        layout.addWidget(self.LeftTextEdit, 1, 0)
        layout.addWidget(self.RightTextEdit, 1, 1)

        self.setLayout(layout)

    def clickMethod(self):
        print('Clicked Pyqt button.')
        home_dir = str(Path.home())
        fname = QFileDialog.getOpenFileName(self, 'Open file', home_dir, filter="csv(*.csv)")
        if fname[0]:
            f = open(fname[0], 'r')
            with f:
                data = f.read()
                self.LeftTextEdit.setText(data)

    def closeIt(self):
        self.close()

    @staticmethod
    def centerWidgetOnScreen(self, widget):
        centerPoint = PyQt6.QtGui.QScreen.availableGeometry(QtWidgets.QApplication.primaryScreen()).center()
        fg = widget.frameGeometry()
        fg.moveCenter(centerPoint)
        widget.move(fg.topLeft())


# Main
if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = RdfApp()
    window.show()

    sys.exit(app.exec())
