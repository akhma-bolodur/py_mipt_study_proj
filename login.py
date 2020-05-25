#!/usr/bin/python3

import sys
import sqlite3 as db

import hashlib

from PyQt5.QtWidgets import (
    QApplication, QLabel, QListWidgetItem, QFileDialog, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5 import uic

DB_PATH = 'my_db.s3db'
FormUI, Form = uic.loadUiType('login.ui')

class Login(Form):
    def __init__(self, parent=None):
        print("login constructor")
        super().__init__()

        self.ui = ui = FormUI()
        ui.setupUi(self)
        ui.pushButton.clicked.connect (self.__authentificate)

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
        passw_text = login.text().strip()
        status = self.ui.status_label
        if (login_text is '') or (passw_text is ''):
            status.setText ('<span style="color: red;">' + 
                    'Error: login or password is empty</span>')
            return
        
        query_text = f'SELECT * FROM auth WHERE login = {login}'
        # Try to execute query
        try:
            cur = self.dbc.cursor ()
            cur.execute (query_text)
            self.dbc.commit ()
            result = cur.fetchall ()
            error = None
        except Exception as exc:
            result = None
            error = str (exc)
        if error is not None:
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
                else:
                    print (result[0])
                    salt = result[0][2]
                    dk = hashlib.pbkdf2_hmac ('sha512', 
                            bytes (login_text, 'utf-8'), salt, 100000)
                    if (dk.hex () != result[0][1]):
                        print ('Success auth')
                        status.setText ('<span style="color: green;">' + 
                               'Successfully auth</span>')
                        return
                    else:
                        status.setText ('<span style="color: red;">' + 
                               'Failed auth: wrong password</span>')
                        return

        return   

def main():
    app = QApplication(sys.argv)
    login = Login()
    login.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()