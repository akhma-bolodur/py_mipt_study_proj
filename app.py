#!/usr/bin/python3

import sys
import sqlite3 as db
import functools

from PyQt5.QtWidgets import (
	QApplication, QLabel, QListWidgetItem, QFileDialog, QWidget, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5 import uic

DB_PATH = 'my_db.s3db'
TABLENAME = 'students'
TAXES = 0.13

FormUI, Form = uic.loadUiType('mataid.ui')

class my_widget(Form):
	
	def __init__(self, course_num, school_num, parent=None):
		print("constructor")
		super().__init__()

		self.ui = ui = FormUI()
		ui.setupUi(self)
		self.ui.button_show.clicked.connect(self.__show)
		self.ui.button_appoint_aid.clicked.connect(self.__appoint_aid)
		self.ui.aid_summ.setMaximum(100000.00)
		self.ui.aid_summ.setMinimum(-100000.00)
		self.setWindowTitle ('App')

		self.max_persons1 = int(self.ui.persons_1.text())
		self.max_persons2 = int(self.ui.persons_2.text())
		self.dbc = db.connect('my_db.s3db')
		self.course_num = course_num
		self.school_num = school_num
		self.access_err = ''

	def __del__(self):
		print("destructor")
		self.ui = None
		if self.dbc is not None:
			self.dbc.close ()

	def __params_to_where(self):
		group_number = self.ui.group_number.text().strip()
		department = self.ui.department.text().strip()
		course_number = self.ui.course_number.text().strip()
		school_number = self.ui.school_number.text().strip()
		full_name = self.ui.full_name.text().strip()
		names = full_name.split(' ')

		# print (course_number, school_number)
		if self.course_num > 0 or self.school_num > 0:
			if self.course_num != int(course_number if course_number is not '' else '0'):
				self.access_err = ('<span style="color: red;"><b>' + 
					f'Access denied: your course number is {self.course_num}' + 
					'</b></span>')
				# print (self.access_err)
				return ''
			elif self.school_num != int(school_number if school_number is not '' else '0'):
				# print (self.school_num, school_number if school_number is not '' else '0')
				self.access_err = ('<span style="color: red;"><b>' + 
					f'Access denied: your school number is {self.school_num}' + 
					'</b></span>')
				# print (self.access_err)
				return ''
		

		last_name, first_name, second_name = [names[i] if i < len(names) else '' for i in range(3)]
		query_parameters = [
			['group_num', group_number], 
			['department', department],
			['course_num', course_number],
			['school_num', school_number],
			['lastname', last_name],
			['first_name', first_name],
			['second_name', second_name]]

		if functools.reduce(lambda a, b: a + b, query_parameters) != '':
			text = ' WHERE'
			for column_name, value in query_parameters:
				if value != '':
					c = ''
					if column_name == 'lastname' or column_name == 'first_name' or column_name == 'second_name':
						c = '"'
					text += ' ' + column_name + ' = ' + c + f'{value}' + c + '  and'
			text = text[:-len(' and')]
		else:
			text = ''
		return text

	def __make_list_widget_table(self, cur, result, error):
		if error is None:
			if not result and cur.description is not None:
				result_text = f'<span style="color: green;"><b>No students</b></span>'
			elif cur.description is not None:
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
				return
		else:
			result_text = f'<span style="color: red;"><b>{error}</b></span>'
		cur.close()
		self.__print_res (result_text)

	def __print_res (self, result_text):	
		# Create widgets for a new list item
		label = QLabel(result_text)
		list_item = QListWidgetItem()
		# Set correct sizes of widget
		label_size_hint = label.sizeHint()
		label.resize(label_size_hint)
		list_item.setSizeHint(label_size_hint)
		# Add item to output
		query_result_list = self.ui.query_result_list
		query_result_list.addItem(list_item)
		query_result_list.setItemWidget(list_item, label)
		query_result_list.scrollToItem(list_item)

	def __show(self):
		print("show")
		# Initial query
		query_text = 'SELECT * FROM ' + TABLENAME
		# Query expansion
		query_text += self.__params_to_where() + ' ORDER BY lastname ASC'
		if self.access_err is not '':
			self.__print_res (self.access_err)
			self.access_err = ''
			return

		# Try to execute query
		try:
			if self.ui.persons_1.isChecked():
				query_text += f' LIMIT {self.max_persons1}'
			elif self.ui.persons_2.isChecked():
				query_text += f' LIMIT {self.max_persons2}'

			cur = self.dbc.cursor()
			cur.execute(query_text)
			self.dbc.commit()
			result = cur.fetchall()
			max_persons = 100
			if (len(result) > max_persons):
				dialog = QDialog()
				DialogFormUI, _ = uic.loadUiType('dialog.ui')
				dialog.ui = DialogFormUI()
				dialog.ui.setupUi(dialog)
				dialog.setWindowTitle('Warning')
				dialog.ui.button_all.clicked.connect(dialog.accept)
				dialog.ui.button_not_all.clicked.connect(dialog.reject)
				if dialog.exec() == 0:
					result = result[:max_persons]
			error = None
		except Exception as exc:
			result = None
			error = str(exc)
		# Display result or error
		self.__make_list_widget_table(cur, result, error)

	def __appoint_aid(self):
		print("appoint")
		# Getting summ of material aid
		aid_summ = float(self.ui.aid_summ.text().replace(',', '.'))
		# Making queries
		query_text = 'UPDATE ' + TABLENAME + ' SET current_full_sum = current_full_sum + ' + str(aid_summ) + ', tax_sum = tax_sum + ' + str(aid_summ * TAXES) + ', pay_sum = pay_sum + ' + str(aid_summ * (1 - TAXES)) + self.__params_to_where()
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
		self.__show()
		#self.__make_list_widget_table(cur, result, error)

	def __show_all(self):
		print("show all")
		self.close()

	def __show_not_all(self):
		print("show not all")


def main():
	app = QApplication(sys.argv)
	wid = my_widget(0, 0)
	wid.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
