#!/usr/bin/python3

import sys
import sqlite3 as db

from PyQt5.QtWidgets import (
	QApplication, QLabel, QListWidgetItem, QFileDialog, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5 import uic

FormUI, Form = uic.loadUiType('mataid.ui')

class my_widget(QWidget):
	def __init__(self, parent=None):
		print("constructor")
		super().__init__()
		self.ui = ui = FormUI()
		ui.setupUi(self)
		self.dbc = db.connect(':memory:')

	def __del__(self):
		print("destructor")
		self.ui = None

	def __show(self):
		print("show")
		return

	def __appoint_aid(self):
		print("appoint")
		return

def main():
	app = QApplication(sys.argv)
	wid = my_widget()
	window = uic.loadUi("mataid.ui", wid)
	window.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
