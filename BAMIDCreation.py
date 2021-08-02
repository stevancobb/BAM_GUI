import sqlite3
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QDoubleValidator

class BAMIDForm(QDialog):

    def __init__(self, UserID):
        super(BAMIDForm, self).__init__()
        self.title = "Create BAM ID"
        self.setWindowTitle(self.title)

        # This is the BAM User ID passed from the main app log staff submitting apps and
        # check what products they have access to
        self.UserID = str(UserID)

        # Create the New Customer Details header layout
        self.NewCustDetailslayoutGroupBox = QGroupBox("New Customer Details")
        self.NewCustDetailslayout = QGridLayout()

        # Create the labels and text boxes
        self.NewCustFirstNameLabel = QLabel("First Name: ")
        self.NewCustMiddleNameLabel = QLabel("Middle Name: ")
        self.NewCustSurnameLabel = QLabel("Surname: ")
        self.NewCustMobilePhoneLabel = QLabel("Mobile Phone: ")
        self.NewCustHomePhoneLabel = QLabel("Home Phone: ")
        self.NewCustWorkPhoneLabel = QLabel("Work Phone: ")
        self.NewCustEmailLabel = QLabel("Email: ")
        self.NewCustHomeAddressLabel = QLabel("Home Address: ")
        self.NewCustPostAddressLabel = QLabel("Postal Address: ")

        self.NewCustFirstName = QLineEdit()
        self.NewCustMiddleName = QLineEdit()
        self.NewCustSurname = QLineEdit()
        self.NewCustMobilePhone = QLineEdit()
        self.NewCustHomePhone = QLineEdit()
        self.NewCustWorkPhone = QLineEdit()
        self.NewCustEmail = QLineEdit()
        self.NewCustHomeAddress = QLineEdit()
        self.NewCustPostAddress = QLineEdit()

        # Add the labels and boxes to the layouts
        self.NewCustDetailslayout.addWidget(self.NewCustFirstNameLabel, 0, 0)
        self.NewCustDetailslayout.addWidget(self.NewCustMiddleNameLabel, 0, 2)
        self.NewCustDetailslayout.addWidget(self.NewCustSurnameLabel, 0, 4)
        self.NewCustDetailslayout.addWidget(self.NewCustMobilePhoneLabel, 1, 0)
        self.NewCustDetailslayout.addWidget(self.NewCustHomePhoneLabel, 1, 2)
        self.NewCustDetailslayout.addWidget(self.NewCustWorkPhoneLabel, 1, 4)
        self.NewCustDetailslayout.addWidget(self.NewCustEmailLabel, 2, 0)
        self.NewCustDetailslayout.addWidget(self.NewCustHomeAddressLabel, 3, 0)
        self.NewCustDetailslayout.addWidget(self.NewCustPostAddressLabel, 4, 0)

        self.NewCustDetailslayout.addWidget(self.NewCustFirstName, 0, 1)
        self.NewCustDetailslayout.addWidget(self.NewCustMiddleName, 0, 3)
        self.NewCustDetailslayout.addWidget(self.NewCustSurname, 0, 5)
        self.NewCustDetailslayout.addWidget(self.NewCustMobilePhone, 1, 1)
        self.NewCustDetailslayout.addWidget(self.NewCustHomePhone, 1, 3)
        self.NewCustDetailslayout.addWidget(self.NewCustWorkPhone, 1, 5)
        self.NewCustDetailslayout.addWidget(self.NewCustEmail, 2, 1, 1, -1)
        self.NewCustDetailslayout.addWidget(self.NewCustHomeAddress, 3, 1, 1, -1)
        self.NewCustDetailslayout.addWidget(self.NewCustPostAddress, 4, 1, 1, -1)

        self.NewCustDetailslayoutGroupBox.setLayout(self.NewCustDetailslayout)

        # Create the KYC Verification layout
        self.KYCVerificationGroupBox = QGroupBox("KYC Verification")
        self.KYCVerificationLayout = QGridLayout()
        # Create and add check boxes for KYC
        self.KYCDL = QCheckBox("Drivers License", self)
        self.KYCPP = QCheckBox("Passport", self)
        self.KYCMC = QCheckBox("Medicare Card", self)
        self.KYCBS = QCheckBox("Bank Statement", self)

        self.KYCVerificationLayout.addWidget(self.KYCDL, 2, 3)
        self.KYCVerificationLayout.addWidget(self.KYCPP, 3, 3)
        self.KYCVerificationLayout.addWidget(self.KYCMC, 4, 3)
        self.KYCVerificationLayout.addWidget(self.KYCBS, 5, 3)

        self.KYCVerificationGroupBox.setLayout(self.KYCVerificationLayout)

        self.CreateBAMIDButton = QPushButton("Create BAM ID")
        self.ButtonHBox = QHBoxLayout()
        self.ButtonHBox.addStretch(1)
        self.ButtonHBox.addWidget(self.CreateBAMIDButton)


        # Bring the App Form Top, Mid and Bottom Layouts together and add a submit button
        self.NewCustFormLayout = QVBoxLayout()
        self.NewCustFormLayout.addWidget(self.NewCustDetailslayoutGroupBox)
        self.NewCustFormLayout.addWidget(self.KYCVerificationGroupBox)
        self.setLayout(self.NewCustFormLayout)
        self.NewCustFormLayout.addLayout(self.ButtonHBox)



    def create_BAMID(self, item):
        KYCDLState = str(self.KYCDL.checkState())
        KYCPPState = str(self.KYCPP.checkState())
        KYCMCState = str(self.KYCMC.checkState())
        KYCBSState = str(self.KYCBS.checkState())

        #Connect to BAM.db
        con = sqlite3.connect("/Users/karinacobb/PycharmProjects/BAM.db")
        c = con.cursor()
        c.execute("SELECT * FROM {tn} WHERE {cn}='{my_id}'". \
                  format(tn='CustomerProfiles', cn='Email', my_id=self.newcustEmailval.text()))
        CustProfile = c.fetchone()
        con.close()

        # return error message if customer not found
        if CustProfile == None:

            con = None
            con = sqlite3.connect('/Users/karinacobb/PycharmProjects/BAM.db')
            # Deduct transfer amount from from acct
            BAMIDInsert = con.cursor()
            BAMIDInsert.execute('INSERT INTO CustomerProfiles VALUES (null , "{newcustEmail}", "", \
                                    "{newcustFirstName}",  \
                                    "{newcustMiddleName}",    "{newcustSurname}",         "{newcustMobilePhone}",  \
                                    "{newcustHomePhone}",     "{newcustWorkPhone}",       "{newcustAddressCountry}",  \
                                    "{newcustAddressState}",  "{newcustAddressStreet1}",  "{newcustAddressStreet2}",  \
                                    "{newcustAddressSuburb}", "{newcustAddressPostCode}", "{newcustPostSameAddress}",  \
                                    "{newcustPostCountry}",   "{newcustPostState}",       "{newcustPostStreet1}",  \
                                    "{newcustPostStreet2}",   "{newcustPostSuburb}",      "{newcustPostPostcode}", \
                                            "{newcustKYCDL}", "{newcustKYCPP}", "{newcustKYCMC}", "{newcustKYCBS}")'. \
                                format(newcustEmail=self.newcustEmailval.text(), \
                                       newcustFirstName=self.newcustFirstNameval.text(), \
                                       newcustMiddleName=self.newcustMiddleNameval.text(), \
                                       newcustSurname=self.newcustSurnameval.text(), \
                                       newcustMobilePhone=self.newcustMobilePhoneval.text(), \
                                       newcustHomePhone=self.newcustHomePhoneval.text(), \
                                       newcustWorkPhone=self.newcustWorkPhoneval.text(), \
                                       newcustAddressCountry=self.newcustAddressCountryval.text(), \
                                       newcustAddressState=self.newcustAddressStateval.text(), \
                                       newcustAddressStreet1=self.newcustAddressStreet1val.text(), \
                                       newcustAddressStreet2=self.newcustAddressStreet2val.text(), \
                                       newcustAddressSuburb=self.newcustAddressSuburbval.text(), \
                                       newcustAddressPostCode=self.newcustAddressPostCodeval.text(), \
                                       newcustPostSameAddress=self.newcustPostSameAddressval.text(), \
                                       newcustPostCountry=self.newcustPostCountryval.text(), \
                                       newcustPostState=self.newcustPostStateval.text(), \
                                       newcustPostStreet1=self.newcustPostStreet1val.text(), \
                                       newcustPostStreet2=self.newcustPostStreet2val.text(), \
                                       newcustPostSuburb=self.newcustPostSuburbval.text(), \
                                       newcustPostPostcode=self.newcustPostPostcodeval.text(), \
                                       newcustKYCDL=KYCDLState, \
                                       newcustKYCPP=KYCPPState, \
                                       newcustKYCMC=KYCMCState, \
                                       newcustKYCBS=KYCBSState))
            con.commit()

            c = con.cursor()
            c.execute("SELECT * FROM {tn} WHERE {cn}='{my_id}'" \
                      .format(tn='CustomerProfiles', cn='Email', my_id=self.newcustEmailval.text()))
            CustProfile = c.fetchone()
            BAMID = str(CustProfile[0])

            c.execute('CREATE TABLE {tn} ("AcctNumber" INTEGER,"Bank"TEXT, "Product" TEXT, \
                          "CurrentBalance" NUMERIC,"AvailableFunds" NUMERIC, "LoanAmtLimit" NUMERIC, \
                          "StatementType" TEXT, "ANZConsent" TEXT, "CBAConsent" TEXT, "NABConsent" TEXT, \
                          "WBCConsent" TEXT, "ProductType" INTEGER, "RHI" INTEGER)' \
                      .format(tn=str("'" + BAMID + " - Accts'")))

            c.execute('CREATE TABLE {tn} ("BAMID" INTEGER, "Date" TEXT, "Action" TEXT, "Context" TEXT, "User" TEXT)' \
                      .format(tn=str("'" + BAMID + " - Contact'")))

            c.execute('INSERT INTO {tn} VALUES ("{BAMID}", "{Date}", "KYCed", "First time KYCed", "User")' \
                      .format(tn=str("'" + BAMID + " - Contact'"), BAMID=BAMID, Date=str(datetime.datetime.now())))
            con.commit()
            c.execute('INSERT INTO {tn} VALUES ("{BAMID}", "{Date}", "BAMID Created", "BAMID Created", "User")' \
                      .format(tn=str("'" + BAMID + " - Contact'"), BAMID=BAMID, Date=str(datetime.datetime.now())))
            con.commit()
            con.close()

            BAMIDCreatedmsgBox = QMessageBox()
            BAMIDCreatedmsgBox.setText("Created BAMID: " + BAMID)
            BAMIDCreatedmsgBox.exec_()
        else:
            msgBox = QMessageBox()
            msgBox.setText("Customer Already Exists")
            msgBox.setIcon(QMessageBox.Information)
            msgBox.exec_()



if __name__ == "__main__":
   import sys
   app = QApplication(sys.argv)
   form = BAMIDForm('ad')
   form.show()
   sys.exit(app.exec_())