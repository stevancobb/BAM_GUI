import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QPushButton, QGroupBox, QDialog, QVBoxLayout, \
     QGridLayout, QLineEdit, QLabel, QDesktopWidget, QMessageBox
from PyQt5.QtCore import pyqtSlot
from BAM import BAM

class UserLogIn(QDialog):

    def __init__(self):
        super().__init__()
        self.title = 'BAM Log In'
        self.setWindowTitle(self.title)
        self.resize(320, 100)
        self.center()

        UserLabel = QLabel("User ID:")
        UserBox = QLineEdit()
        PassLabel = QLabel("Password:")
        PassBox = QLineEdit()
        LoginButton = QPushButton("Log In", self)
        UserBox.setText("ANZStaff")
        PassBox.setText("ANZPW")


        self.horizontalGroupBox = QGroupBox("BAM Log In")
        layout = QGridLayout()
        layout.addWidget(UserLabel, 0, 0)
        layout.addWidget(UserBox, 0, 1)
        layout.addWidget(PassLabel, 1, 0)
        layout.addWidget(PassBox, 1, 1)
        layout.addWidget(LoginButton, 2, 0)
        self.horizontalGroupBox.setLayout(layout)

        LoginButton.clicked.connect(lambda: self.LoginButton_click(UserBox.text(),PassBox.text()))

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        self.show()


    @pyqtSlot()
    def LoginButton_click(self, user, pw):
        con = sqlite3.connect('/Users/karinacobb/PycharmProjects/BAM.db')
        c = con.cursor()
        c.execute("SELECT * FROM {tn} WHERE {cn}='{my_id}'".format(tn='UserProfiles',  cn='UserID', my_id=user))
        UserProfile = c.fetchone()
        con.close()

        if UserProfile == None:
             msgBox = QMessageBox()
             msgBox.setText("User Not Found")
             msgBox.setIcon(QMessageBox.Information)
             msgBox.exec_()
        elif pw != UserProfile[1]:
             QMessageBox.about(self, "Bank Account Manager", "Wrong Password")
        else:
             BAMobj = BAM(UserProfile[0], UserProfile[2])
             BAMobj.show()
             self.close()


    def center(self):
        # geometry of the main window
        qr = self.frameGeometry()
        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()
        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)
        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UserLogIn()
    sys.exit(app.exec_())
