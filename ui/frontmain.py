import csv
import sys
from pathlib import Path

from PyQt5 import QtGui
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QStandardItemModel
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QGridLayout, QFileDialog, QTextEdit, \
    QTableView

from rdflib import Graph, Literal, RDF, URIRef, Namespace # basic RDF handling


class RdfApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(1250, 500))
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
        layout.addWidget(self.fileLine, 0, 0, 1, 2)

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

        # Left Table
        self.model = QStandardItemModel(self)
        self.tableView = QTableView(self)
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tableView, 1, 0)

        # Right Table
        self.RightTextEdit = QTextEdit()
        layout.addWidget(self.RightTextEdit, 1, 1)

        self.setLayout(layout)

    def clickMethod(self):
        self.model.clear()
        home_dir = str(Path.home())
        fileName = QFileDialog.getOpenFileName(self, 'Open file', home_dir, filter="csv(*.csv)")
        self.fileLine.setStyleSheet("color: black;font-size:12pt")
        self.fileLine.setText(fileName[0])
        with open(fileName[0], "r") as fileInput:
            for row in csv.reader(fileInput):
                items = [
                    QtGui.QStandardItem(field)
                    for field in row
                ]
                self.model.appendRow(items)

    def closeIt(self):
        self.close()


# Main
if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = RdfApp()
    window.show()

    sys.exit(app.exec())
