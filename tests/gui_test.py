#!/usr/bin/env python
import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtCore import QSize

class HelloWindow(QMainWindow):
    def __init__( self ):
        super().__init__()

        py_ver = '%d.%d' % (sys.version_info.major, sys.version_info.minor)

        self.setMinimumSize( QSize(350, 100) )
        self.setWindowTitle( 'GUI test - python %s' % (py_ver,) )

        self.setCentralWidget( QLabel( ' GUI test - python %s ' % (py_ver,), self ) )

if __name__ == "__main__":
    app = QtWidgets.QApplication( sys.argv )
    main_win = HelloWindow()
    main_win.show()
    sys.exit( app.exec_() )
