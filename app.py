#!/usr/bin/python3

import sys
import sqlite3 as db
import functools

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
		self.max_persons1 = int(self.ui.persons_1.text())
		self.max_persons2 = int(self.ui.persons_2.text())
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
		school_number = self.ui.school_number.text().strip()
		full_name = self.ui.full_name.text().strip()
		names = full_name.split(' ')
		names = [names[i] if i < len(names) else '' for i in range(3)]
		last_name, first_name, second_name = names
		query_parameters = [
			['group_num', group_number], 
			['department', department],
			['course_num', course_number],
			['school_num', school_number],
			['lastname', last_name],
			['first_name', first_name],
			['second_name', second_name]]

		if functools.reduce(lambda a, b: a + b, query_parameters) != '':
			query_text += ' WHERE'
			for column_name, value in query_parameters:
				if value != '':
					c = ''
					if column_name == 'lastname' or column_name == 'first_name' or column_name == 'second_name':
						c = '"'
					query_text += ' ' + column_name + ' = ' + c + f'{value}' + c + '  and'
			query_text = query_text[:-len(' and')]
		# Try to execute query
		try:
			max_p = 'all'
			if self.ui.persons_1.isChecked():
				max_p = self.max_persons1
			elif self.ui.persons_2.isChecked():
				max_p = self.max_persons2
			cur = self.dbc.cursor()
			cur.execute(query_text)
			self.dbc.commit()
			result = cur.fetchall() if max_p == 'all' else cur.fetchmany(max_p)
			error = None
		except Exception as exc:
			result = None
			error = str(exc)
		# Display result or error
		if error is None:
			if cur.description is None:
				result_text = f'<span style="color: green;"><b>No students</b></span>'
			else:
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
