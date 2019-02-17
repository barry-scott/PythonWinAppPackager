#!/usr/bin/env python
import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget
from PyQt5.QtCore import QSize

class HelloWindow(QMainWindow):
    def __init__( self ):
        super().__init__()

        self.setMinimumSize( QSize(100, 50) )
        self.setWindowTitle( 'GUI test' )

        self.setCentralWidget( QLabel( ' GUI test ' , self ) )

if __name__ == "__main__":
    app = QtWidgets.QApplication( sys.argv )
    main_win = HelloWindow()
    main_win.show()
    sys.exit( app.exec_() )
