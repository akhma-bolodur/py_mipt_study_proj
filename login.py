#!/usr/bin/python3

import sys
import sqlite3 as db

import hashlib
from app import my_widget

from PyQt5.QtWidgets import (
    QApplication, QLabel, QListWidgetItem, QFileDialog, QWidget, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5 import uic
from PyQt5 import QtCore 

DB_PATH = 'my_db.s3db'
FormUI, Form = uic.loadUiType('login.ui')

class Login(Form):
    
    switch_to_app = QtCore.pyqtSignal (int, int)

    def __init__(self, parent=None):
        print("login constructor")
        super().__init__()
        
        self.ui = ui = FormUI()
        ui.setupUi(self)
        ui.password.setEchoMode (QLineEdit.Password)
        ui.pushButton.clicked.connect (self.__authentificate)
        self.setWindowTitle ('Authentification')

        self.dbc = db.connect('my_db.s3db')

    def __del__(self):
        print("login destructor")
        self.ui = None
        if self.dbc is not None:
            self.dbc.close ()

    def __authentificate (self):
        login = self.ui.login
        passw = self.ui.password
        login_text = login.text().strip()
        passw_text = passw.text().strip()
        status = self.ui.status_label
        if login_text == '' or passw_text == '':
            status.setText ('<span style="color: red;">' + 
                    'Error: login or password is empty</span>')
            return
        
        query_text = 'SELECT * FROM auth WHERE login = ?;'
        # Try to execute query
        try:
            cur = self.dbc.cursor ()
            cur.execute (query_text, (login_text, ))
            self.dbc.commit ()
            result = cur.fetchall ()
            error = None
        except Exception as exc:
            result = None
            error = str (exc)
        if error is not None:
            print (error)
            status.setText ('<span style="color: red;">' + 
                   f'Error: {error}</span>')
            return  
        else:
            if cur.description is None:
                status.setText ('<span style="color: red;">' + 
                    f'Failed authentification: unknown login {login_text}</span>')
                return
            else:
                if len (result) > 1:
                    status.setText ('<span style="color: red;">' + 
                           f'Error: dublicated login {login_text}</span>')
                    return
                elif len (result) == 0:
                    status.setText ('<span style="color: red;">' + 
                           f'Failed auth: unknown login {login_text}</span>')
                    
                    return

                else:
                    salt = result[0][2]
                    dk = hashlib.pbkdf2_hmac ('sha512', 
                            bytes (passw_text, 'utf-8'), salt, 100000)
                    if (dk  == result[0][1]):
                        print ('Success auth')
                        status.setText ('<span style="color: green;">' + 
                               'Successfully auth</span>')
                    
                        self.switch_to_app.emit (result[0][3], result[0][4])
                        return
                    else:
                        status.setText ('<span style="color: red;">' + 
                               'Failed auth: wrong password</span>')
                        return
        return

    def keyPressEvent (self, event):
        key = event.key ()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            self.__authentificate ()

class Control:
    def _login (self):
        self.login = Login ()
        self.login.switch_to_app.connect (self.__app)
        self.login.show ()

    def __app (self, c_num, s_num):
        self.app = my_widget (course_num = c_num, school_num = s_num)
        self.app.switch_to_login.connect (self.__login)
        self.login.close ()
        self.app.show ()

    def __login (self):
        self.app.close ()
        self._login ()

def main():
    app = QApplication(sys.argv)
    control = Control ()
    control._login ()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
