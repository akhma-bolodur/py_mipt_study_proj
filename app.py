#!/usr/bin/python3

import sys
import sqlite3 as db

from PyQt5.QtWidgets import (
	QApplication, QLabel, QListWidgetItem, QFileDialog, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5 import uic

DB_PATH = 'my_db.s3db'
FormUI, Form = uic.loadUiType('mataid.ui')

class my_widget(QWidget):
	def __init__(self, parent=None):
		print("constructor")
		super().__init__()
		self.ui = ui = FormUI()
		ui.setupUi(self)
		self.ui.button_show.clicked.connect(self.__show)
		self.ui.button_appoint_aid.clicked.connect(self.__appoint_aid)
		self.ui.aid_summ.setMaximum(100000.00)
		self.dbc = db.connect('my_db.s3db')

	def __del__(self):
		print("destructor")
		self.ui = None

	def __show(self):
		print("show")
		# Initial query
		query_text = 'SELECT * FROM students'
		# Query expansion
		group_number = self.ui.group_number.text().strip()
		department = self.ui.department.text().strip()
		course_number = self.ui.course_number.text().strip()
		full_name = self.ui.full_name.text().strip()
		if group_number + department + course_number + full_name != '':
			query_text += ' WHERE'
			if group_number != '':
				query_text += f' group_num = {group_number} and'
			if department != '':
				query_text += f' department = {department} and'
			if course_number != '':
				query_text += f' course_num = {course_number} and'
			if full_name != '':
				last_name, first_name, second_name = full_name.split(' ')
				query_text += f' lastname = "{last_name}" and first_name = "{first_name}" and second_name = "{second_name}" and'
			query_text = query_text[:-4]
			print(query_text)
		# Try to execute query
		try:
			cur = self.dbc.cursor()
			cur.execute(query_text)
			self.dbc.commit()
			result = cur.fetchall()
			error = None
		except Exception as exc:
			result = None
			error = str(exc)
		# Display result or error
		if error is None:
			if cur.description is not None:
				result_text = '<table border=1>'
				result_text += '<tr>'
				for column_name, *_ in cur.description:
					result_text += f'<td><b>{column_name}</b></td>'
				result_text += '</tr>'
				for row in result:
					result_text += '<tr>'
					result_text += ''.join('<td>%s</td>' % cell for cell in row)
					result_text += '</tr>'
				result_text += '</table>'
		else:
			result_text = f'<span style="color: red;"><b>{error}</b></span>'
		# Create widgets for a new list item
		label = QLabel(result_text)
		list_item = QListWidgetItem()
		# Set correct sizes of widget
		label_size_hint = label.sizeHint()
		label.resize(label_size_hint)
		list_item.setSizeHint(label_size_hint)
		# Add item to output
		query_result = self.ui.query_result
		query_result.addItem(list_item)
		query_result.setItemWidget(list_item, label)

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
