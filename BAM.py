import sqlite3
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtSql import QSqlQueryModel,QSqlDatabase
from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from AppCreation import AppForm
import datetime

#Create the main window - need to change from QDialog to QMainwindow
class BAM(QMainWindow):
    def __init__(self, UserID, UserOrg, parent=None):
        super(BAM, self).__init__(parent)
        self.originalPalette = QApplication.palette()

        #create the window dimensions
        self.title = 'Bank Account Manager'
        self.left = 0
        self.top = 0
        self.width = 1200
        self.height = 1000
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #Create customer lookup box
        custLookUpLabel = QLabel("Cust Search:")
        custLookUpBox = QLineEdit()
        custLookUpBox.setText("stevan.cobb@gmail.com")
        custLookUpButton = QPushButton("Look Up Customer", self)
        createAppButton = QPushButton("Create an Application", self)
        createProfileButton = QPushButton("Create Customer Profile", self)


        #Create a top layer in for the layout with the customer lookup box
        topLayout = QHBoxLayout()
        topLayout.addWidget(custLookUpLabel)
        topLayout.addWidget(custLookUpBox)
        topLayout.addWidget(custLookUpButton)
        topLayout.addWidget(createAppButton)
        topLayout.addWidget(createProfileButton)

        self.createTabWidget()

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0)
        mainLayout.addWidget(self.TabWidget, 1, 0)
        mainLayout.setRowStretch(1, 1)
        mainLayout.setColumnStretch(0, 1)

        mainwidget = QWidget()
        mainwidget.setLayout(mainLayout)
        self.setCentralWidget(mainwidget)

        #Pull in all data when Look Up Customer clicked
        custLookUpButton.clicked.connect(lambda: self.on_click_cust_lookup(custLookUpBox.text(),UserOrg))
        #Pull in trasaction when Acct Table view clicked
        self.acctsTv.clicked.connect(self.pull_transaction)
        #Update Inccome Expense and Debt chart when slider moved
        self.IncExpDebtChartSlider.valueChanged.connect(self.UpdateIncExpDebtChart)

        #Open window to create an Application
        createAppButton.clicked.connect(lambda: self.on_click_createApp(custLookUpBox.text(), UserID, UserOrg))

        # Switch Create Customer Profile
        createProfileButton.clicked.connect(lambda: self.on_click_createProfileButton())


    #Create an app when clicking button
    @pyqtSlot()
    def on_click_createApp(self, custEmail, UserID, UserOrg):
        self.FORMobj = QDialog()
        self.FORMobj = AppForm(UserID)
        self.FORMobj.show()

    #Pull data when clicking 'Look Up Customer'
    @pyqtSlot()
    def on_click_cust_lookup(self, custEmail, UserOrg):
        #Import customer profile data for the Customer Profile Tab
        con = sqlite3.connect("/Users/karinacobb/PycharmProjects/BAM.db")
        c = con.cursor()
        c.execute("SELECT * FROM {tn} WHERE {cn}='{my_id}'".format(tn='CustomerProfiles',  cn='Email', my_id=custEmail))
        CustProfile = c.fetchone()
        con.close()

        #return error message if customer not found
        if CustProfile == None:
            msgBox = QMessageBox()
            msgBox.setText("Customer Not Found.")
            msgBox.setIcon(QMessageBox.Information)
            msgBox.exec_()
        else:
            #Store BAMID to use in SQL queries
            BAMID = str(CustProfile[0])

            #Connect to BAM.db
            db = QSqlDatabase.addDatabase("QSQLITE")
            db.setDatabaseName("/Users/karinacobb/PycharmProjects/BAM.db")
            db.open()

            #Update the Accts Table View with Accts data where Consent = Y
            AcctsModel = QSqlQueryModel()
            sqlacct = "select AcctNumber, Product, CurrentBalance, AvailableFunds, LoanAmtLimit from \"" \
                      + str(BAMID) + " - Accts\" where " + UserOrg + "Consent = 'Y';"
            AcctsModel.setQuery(sqlacct, db)
            self.acctsTv.setModel(AcctsModel)

            # Update the Customer Comms Table View with data
            #IMPORTANT: Need to find way to filter comms for staff to their institution
            CommsModel = QSqlQueryModel()
            sqlcomms = "select Date, Action, Context, User from \"" \
                      + str(BAMID) + " - Contact\";"
            CommsModel.setQuery(sqlcomms, db)
            self.custcommsTv.setModel(CommsModel)
            self.custcommsTv.resizeColumnsToContents()

            # Get data for Credit Profile Tab
            # Need 2 tables as consented will have more account info from tab 2,
            # Update the Credit Profile Table View with Credit Accts data where Consent = N
            CBNCModel = QSqlQueryModel()
            sqlCBNC = "select AcctNumber, Bank, Product, LoanAmtLimit, RHI from \"" + str(BAMID) + " - Accts\" where ("\
                      + UserOrg + "Consent = 'N' and ProductType = 'C');"
            CBNCModel.setQuery(sqlCBNC, db)
            self.cbncTv.setModel(CBNCModel)
            # Update the Credit Profile Table View with Credit Accts data where Consent = Y
            CBYCModel = QSqlQueryModel()
            sqlCBYC = "select AcctNumber, Bank, Product, CurrentBalance, AvailableFunds, LoanAmtLimit, RHI from \"" \
                      + str(BAMID) + " - Accts\" where (" + UserOrg + "Consent = 'Y' and ProductType = 'C');"
            CBYCModel.setQuery(sqlCBYC, db)
            self.cbycTv.setModel(CBYCModel)

            db.close()

            #Add Chart for Income, Expense and Debt Payments on Credit Profile Tab
            #First remove whatever data that maybe on the barseries, the initial barsets are blank then it would be the sets for the last customer looked up
            self.series.remove(self.Income)
            self.series.remove(self.Expense)
            self.series.remove(self.Debt)

            #create new dataset for the customer being looked up and add them to the BarChart series
            self.Income = QBarSet("Money In")
            self.Expense = QBarSet("Money Out")
            self.Debt = QBarSet("Debt Payments")
            self.series.append(self.Income)
            self.series.append(self.Expense)
            self.series.append(self.Debt)

            #Pull in the data for the BarChart
            con = sqlite3.connect("/Users/karinacobb/PycharmProjects/BAM.db")
            c = con.cursor()
            #Create a list of Deposit Acct Transaction Tables from the acct table that consent has been provided for
            sqlaccttables = "select group_concat('select * from \"" + str(BAMID) + " - TRANSACTIONS - '|| AcctNumber || '\"', '  UNION ALL ')\
                        FROM '" + str(BAMID) + " - Accts' where (" + UserOrg + "Consent = 'Y' and ProductType = \"D\")"
            c.execute(sqlaccttables)
            sqlaccttablesresults = c.fetchone()

            # Check to see if there are any tables, if not set data to blank also summarise Transaction data
            if sqlaccttablesresults[0] == None:
                self.IncExpDebtProfile = []
                self.categories = ["No Results"]
            else:
                sqlIncExpDebt = 'SELECT  \"Transaction Month\", \
                                   sum(CASE WHEN \"Category 1\" = \"Income\" THEN Credit ELSE 0 END) AS Income, \
                                   sum(CASE WHEN \"Category 1\" = \"Expense\" THEN -Debit ELSE 0 END) AS Expense, \
                                   sum(CASE WHEN \"Category 1\" = \"Debt\" THEN -DebIt ELSE 0 END) AS Debt FROM (' + \
                           sqlaccttablesresults[0] + ") GROUP BY  \"Transaction Month\" ORDER BY  \"Transaction Month\""
                c.execute(sqlIncExpDebt)

                self.IncExpDebtProfile = c.fetchall()
                con.close()
                self.categories = []

                if self.IncExpDebtProfile != None:
                    for x in range(0, len(self.IncExpDebtProfile)):
                        self.categories.append(datetime.datetime. \
                                            strptime(str(self.IncExpDebtProfile[x][0]), '%Y-%m-%d').strftime('%b-%y'))

                        if self.IncExpDebtProfile[x][1] == None: self.Income << 0
                        else: self.Income << self.IncExpDebtProfile[x][1]

                        if self.IncExpDebtProfile[x][2] == None: self.Expense << 0
                        else: self.Expense << self.IncExpDebtProfile[x][2]

                        if self.IncExpDebtProfile[x][3] == None: self.Debt << 0
                        else: self.Debt << self.IncExpDebtProfile[x][3]

            self.axis = QBarCategoryAxis()
            self.axis.setCategories(self.categories)
            self.axis.setTitleText("Months")
            self.chart.setAxisX(self.axis, self.series)

            self.IncExpDebtChartSlider.setMaximum(len(self.IncExpDebtProfile))
            self.IncExpDebtChartSlider.setValue(len(self.IncExpDebtProfile))

            self.TabWidget.setCurrentIndex(0)

            #Returning values for the Customer Tab
            return (self.custBAMIDval.setText(str(CustProfile[0])),
                    self.custEmailval.setText(CustProfile[1]),
                    self.custNameval.setText(CustProfile[3] + ' ' + CustProfile[4] + ' ' + CustProfile[5]),
                    self.custMobval.setText(CustProfile[6]),
                    self.custHomeval.setText(CustProfile[7]),
                    self.custWorkval.setText(CustProfile[8]),
                    self.custResiAddval.setText(CustProfile[11] + ' ' + CustProfile[12] + ' ' + \
                                                CustProfile[13] + ' ' + CustProfile[10]),
                    self.custPostAddval.setText(CustProfile[18] + ' ' + CustProfile[19] + ' ' + \
                                                CustProfile[20] + ' ' + CustProfile[17]))


    # Create the tab widget to flick through different screens
    def createTabWidget(self):
        self.TabWidget = QTabWidget()
        self.TabWidget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Ignored)

        # ----------------------------------------------------------
        # Create tab with Customer Details and Communication History
        # ----------------------------------------------------------
        tabCust = QWidget()
        custgrid = QGridLayout()

        self.custBAMIDlbl = QLabel("BAM ID:")
        self.custEmaillbl = QLabel("Email:")
        self.custNamelbl = QLabel("Name:")
        self.custMoblbl = QLabel("Mobile Phone:")
        self.custHomelbl = QLabel("Home Phone:")
        self.custWorklbl = QLabel("Work Phone:")
        self.custResiAddlbl = QLabel("Residential\nAddress:")
        self.custPostAddlbl = QLabel("Postal\nAddress:")

        self.custBAMIDlbl.setMaximumWidth(85)
        self.custEmaillbl.setMaximumWidth(85)
        self.custNamelbl.setMaximumWidth(85)
        self.custMoblbl.setMaximumWidth(85)
        self.custHomelbl.setMaximumWidth(85)
        self.custWorklbl.setMaximumWidth(85)
        self.custResiAddlbl.setMaximumWidth(85)
        self.custPostAddlbl.setMaximumWidth(85)

        self.custBAMIDval = QLabel()
        self.custEmailval = QLabel()
        self.custNameval = QLabel()
        self.custMobval = QLabel()
        self.custHomeval = QLabel()
        self.custWorkval = QLabel()
        self.custResiAddval = QLabel()
        self.custPostAddval = QLabel()

        custgrid.addWidget(self.custBAMIDlbl, 1, 1)
        custgrid.addWidget(self.custEmaillbl, 2, 1)
        custgrid.addWidget(self.custNamelbl, 3, 1)
        custgrid.addWidget(self.custMoblbl, 4, 1)
        custgrid.addWidget(self.custHomelbl, 5, 1)
        custgrid.addWidget(self.custWorklbl, 6, 1)
        custgrid.addWidget(self.custResiAddlbl, 7, 1)
        custgrid.addWidget(self.custPostAddlbl, 8, 1)

        custgrid.addWidget(self.custBAMIDval, 1, 2)
        custgrid.addWidget(self.custEmailval, 2, 2)
        custgrid.addWidget(self.custNameval, 3, 2)
        custgrid.addWidget(self.custMobval, 4, 2)
        custgrid.addWidget(self.custHomeval, 5, 2)
        custgrid.addWidget(self.custWorkval, 6, 2)
        custgrid.addWidget(self.custResiAddval, 7, 2)
        custgrid.addWidget(self.custPostAddval, 8, 2)

        # Add customer communication details
        self.custcommsTv = QtWidgets.QTableView(self)
        self.custcommsTv.setSortingEnabled(True)
        self.custcommsTv.verticalHeader().setVisible(False)
        self.custcommsTv.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        custgrid.addWidget(self.custcommsTv,1,3,8,1)

        # custcomms = QTextEdit()
        # custcomms.setText("Record of all cust comms to be stated here\nincluding Letters, SMS, email staff notes etc.")
        # custgrid.addWidget(custcomms,1,3,8,1)

        tabCust.setLayout(custgrid)

        # ----------------------------------------------------------
        # Create tab to list all customer accounts
        # ----------------------------------------------------------
        tabAcct = QWidget()
        accthbox = QHBoxLayout()
        accthbox.setContentsMargins(5, 5, 5, 5)

        #Create list of accounts in a table
        self.acctsTv = QtWidgets.QTableView(self)
        self.acctsTv.verticalHeader().setVisible(False)
        self.acctsTv.setSortingEnabled(True)

        #Create a box for account details for active row in the acct table
        self.acctDetails = QGroupBox(self)
        self.acctDetails.setTitle("Account Details, eg. rate, term, statement dates and RHI")

        #Create a box for transaction details for active row in the acct table
        self.acctTransactions = QGroupBox(self)
        self.acctTransactions.setTitle("Account Transactions")
        self.transTv = QtWidgets.QTableView(self)
        self.transTv.verticalHeader().setVisible(False)
        self.transTv.setSortingEnabled(True)
        self.transvbox = QVBoxLayout()
        self.transvbox.addWidget(self.transTv)
        self.acctTransactions.setLayout(self.transvbox)

        #Create a split between Acct Details and Transactions
        #self.DetTraSplitter = QtWidgets.QSplitter(self)
        #self.DetTraSplitter.setOrientation(QtCore.Qt.Vertical)
        #self.DetTraSplitter.addWidget(self.acctDetails)
        #self.DetTraSplitter.addWidget(self.acctTransactions)

        #Now create a split between Acct Table and the Acct Details and Transactions split
        #self.AcctsSplitter = QtWidgets.QSplitter(self)
        #self.AcctsSplitter.setOrientation(QtCore.Qt.Horizontal)
        #self.AcctsSplitter.addWidget(self.acctsTv)
        #self.AcctsSplitter.addWidget(self.DetTraSplitter)

        # Create a split between List of Accts and Acct Details
        self.DetTraSplitter = QtWidgets.QSplitter(self)
        self.DetTraSplitter.setOrientation(QtCore.Qt.Vertical)
        self.DetTraSplitter.addWidget(self.acctsTv)
        self.DetTraSplitter.addWidget(self.acctDetails)

        # Now create a split between Acct Table and Details Split and Transactions Table
        self.AcctsSplitter = QtWidgets.QSplitter(self)
        self.AcctsSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.AcctsSplitter.addWidget(self.DetTraSplitter)
        self.AcctsSplitter.addWidget(self.acctTransactions)

        #Add the Acct Split to the Hbox
        accthbox.addWidget(self.AcctsSplitter)
        #set the Hbox as tab layout
        tabAcct.setLayout(accthbox)

        # ----------------------------------------------------------
        # Create tab to list Credit Profile
        # ----------------------------------------------------------
        tabCP = QWidget()
        cpvbox = QVBoxLayout()
        cpvbox.setContentsMargins(5, 5, 5, 5)

        # Create a box for concent credit bureau accounts
        self.ConcentCB = QGroupBox(self)
        self.ConcentCB.setTitle("Credit Performance of accounts with Open Banking data consent")
        self.cbycTv = QtWidgets.QTableView(self)
        self.cbycTv.setSortingEnabled(True)
        self.cbycTv.verticalHeader().setVisible(False)
        self.ConcentCBvbox = QVBoxLayout()
        self.ConcentCBvbox.addWidget(self.cbycTv)
        self.ConcentCB.setLayout(self.ConcentCBvbox)

        #Create a box for non concent credit bureau accounts
        self.NonConCB = QGroupBox(self)
        self.NonConCB.setTitle("Credit Performance of accounts without Open Banking data consent")
        self.cbncTv = QtWidgets.QTableView(self)
        self.cbncTv.setSortingEnabled(True)
        self.cbncTv.verticalHeader().setVisible(False)
        self.NonConCBvbox = QVBoxLayout()
        self.NonConCBvbox.addWidget(self.cbncTv)
        self.NonConCB.setLayout(self.NonConCBvbox)



        #Create a split between NonConcent Vbox and the concent Vbox
        self.CPSplitter = QtWidgets.QSplitter(self)
        self.CPSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.CPSplitter.addWidget(self.ConcentCB)
        self.CPSplitter.addWidget(self.NonConCB)

        cpvbox.addWidget(self.CPSplitter)

        #Create a slider between the Credit Beaurx tables and the Income, Expense & Debt Bar Chart
        self.IncExpDebtChartSlider = QSlider(Qt.Horizontal)
        self.IncExpDebtChartSlider.setFocusPolicy(Qt.NoFocus)
        self.IncExpDebtChartSlider.setMinimum(0)
        self.IncExpDebtChartSlider.setMaximum(0)

        #Create the Income, Expense & Debt Bar Chart
        self.series = QBarSeries()
        self.Income = QBarSet("Money In")
        self.Expense = QBarSet("Money Out")
        self.Debt = QBarSet("Debt Payments")

        self.series.append(self.Income)
        self.series.append(self.Expense)
        self.series.append(self.Debt)

        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle("Customer Income, Expense and Debt Payments")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.axis = QBarCategoryAxis()

        self.chart.createDefaultAxes()
        self.chart.setAxisX(self.axis, self.series)
        self.chart.axisY(self.series).setRange(0, 60000)
        self.chart.axisY(self.series).setTitleText("Dollars")

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        self.chartView = QChartView(self.chart)
        self.chartView.setRenderHint(QPainter.Antialiasing)

        cpvbox.addWidget(self.chartView)
        cpvbox.addWidget(self.IncExpDebtChartSlider)

        #Assign box to tabCP
        tabCP.setLayout(cpvbox)

        # ----------------------------------------------------------
        # Create place holder tabs for future development
        # ----------------------------------------------------------
        tabNewAcctApp = QWidget()
        tabProcessQueue = QWidget()

        # ----------------------------------------------------------
        # Create tab with to create new customer BAMIDs and KYC
        # ----------------------------------------------------------
        tabNewBAMID = QWidget()
        NewBAMIDgrid = QGridLayout()

        self.newcustDetailsHeaderlbl = QLabel("Customer Details:")
        self.newcustKYCVerifyHeaderlbl = QLabel("KYC Verification:")

        self.newcustEmaillbl = QLabel("Email:")
        self.newcustFirstNamelbl = QLabel("First Name:")
        self.newcustMiddleNamelbl = QLabel("Middle Name:")
        self.newcustSurnamelbl = QLabel("Surname:")
        self.newcustMobilePhonelbl = QLabel("Mobile Phone:")
        self.newcustHomePhonelbl = QLabel("Home Phone:")
        self.newcustWorkPhonelbl = QLabel("Work Phone:")
        self.newcustAddressCountrylbl = QLabel("Address Country:")
        self.newcustAddressStatelbl = QLabel("Address State:")
        self.newcustAddressStreet1lbl = QLabel("Address Street1:")
        self.newcustAddressStreet2lbl = QLabel("Address Street2:")
        self.newcustAddressSuburblbl = QLabel("Address Suburb:")
        self.newcustAddressPostCodelbl = QLabel("Address Post Code:")
        self.newcustPostSameAddresslbl = QLabel("Postal Address:")
        self.newcustPostCountrylbl = QLabel("Post Country:")
        self.newcustPostStatelbl = QLabel("Post State:")
        self.newcustPostStreet1lbl = QLabel("Post Street1:")
        self.newcustPostStreet2lbl = QLabel("Post Street2:")
        self.newcustPostSuburblbl = QLabel("Post Suburb:")
        self.newcustPostPostcodelbl = QLabel("Post Postcode:")

        self.newcustEmaillbl.setMaximumWidth(125)
        self.newcustFirstNamelbl.setMaximumWidth(125)
        self.newcustMiddleNamelbl.setMaximumWidth(125)
        self.newcustSurnamelbl.setMaximumWidth(125)
        self.newcustMobilePhonelbl.setMaximumWidth(125)
        self.newcustHomePhonelbl.setMaximumWidth(125)
        self.newcustWorkPhonelbl.setMaximumWidth(125)
        self.newcustAddressCountrylbl.setMaximumWidth(125)
        self.newcustAddressStatelbl.setMaximumWidth(125)
        self.newcustAddressStreet1lbl.setMaximumWidth(125)
        self.newcustAddressStreet2lbl.setMaximumWidth(125)
        self.newcustAddressSuburblbl.setMaximumWidth(125)
        self.newcustAddressPostCodelbl.setMaximumWidth(125)
        self.newcustPostSameAddresslbl.setMaximumWidth(125)
        self.newcustPostCountrylbl.setMaximumWidth(125)
        self.newcustPostStatelbl.setMaximumWidth(125)
        self.newcustPostStreet1lbl.setMaximumWidth(125)
        self.newcustPostStreet2lbl.setMaximumWidth(125)
        self.newcustPostSuburblbl.setMaximumWidth(125)
        self.newcustPostPostcodelbl.setMaximumWidth(125)

        self.newcustEmailval = QLineEdit()
        self.newcustFirstNameval = QLineEdit()
        self.newcustMiddleNameval = QLineEdit()
        self.newcustSurnameval = QLineEdit()
        self.newcustMobilePhoneval = QLineEdit()
        self.newcustHomePhoneval = QLineEdit()
        self.newcustWorkPhoneval = QLineEdit()
        self.newcustAddressCountryval = QLineEdit()
        self.newcustAddressStateval = QLineEdit()
        self.newcustAddressStreet1val = QLineEdit()
        self.newcustAddressStreet2val = QLineEdit()
        self.newcustAddressSuburbval = QLineEdit()
        self.newcustAddressPostCodeval = QLineEdit()
        self.newcustPostSameAddressval = QLineEdit()
        self.newcustPostCountryval = QLineEdit()
        self.newcustPostStateval = QLineEdit()
        self.newcustPostStreet1val = QLineEdit()
        self.newcustPostStreet2val = QLineEdit()
        self.newcustPostSuburbval = QLineEdit()
        self.newcustPostPostcodeval = QLineEdit()

        NewBAMIDgrid.addWidget(self.newcustDetailsHeaderlbl, 1, 1)
        NewBAMIDgrid.addWidget(self.newcustKYCVerifyHeaderlbl, 1, 3)
        NewBAMIDgrid.addWidget(self.newcustEmaillbl, 2, 1)
        NewBAMIDgrid.addWidget(self.newcustFirstNamelbl, 3, 1)
        NewBAMIDgrid.addWidget(self.newcustMiddleNamelbl, 4, 1)
        NewBAMIDgrid.addWidget(self.newcustSurnamelbl, 5, 1)
        NewBAMIDgrid.addWidget(self.newcustMobilePhonelbl, 6, 1)
        NewBAMIDgrid.addWidget(self.newcustHomePhonelbl, 7, 1)
        NewBAMIDgrid.addWidget(self.newcustWorkPhonelbl, 8, 1)
        NewBAMIDgrid.addWidget(self.newcustAddressCountrylbl, 9, 1)
        NewBAMIDgrid.addWidget(self.newcustAddressStatelbl, 10, 1)
        NewBAMIDgrid.addWidget(self.newcustAddressStreet1lbl, 11, 1)
        NewBAMIDgrid.addWidget(self.newcustAddressStreet2lbl, 12, 1)
        NewBAMIDgrid.addWidget(self.newcustAddressSuburblbl, 13, 1)
        NewBAMIDgrid.addWidget(self.newcustAddressPostCodelbl, 14, 1)
        NewBAMIDgrid.addWidget(self.newcustPostSameAddresslbl, 15, 1)
        NewBAMIDgrid.addWidget(self.newcustPostCountrylbl, 16, 1)
        NewBAMIDgrid.addWidget(self.newcustPostStatelbl, 17, 1)
        NewBAMIDgrid.addWidget(self.newcustPostStreet1lbl, 18, 1)
        NewBAMIDgrid.addWidget(self.newcustPostStreet2lbl, 19, 1)
        NewBAMIDgrid.addWidget(self.newcustPostSuburblbl, 20, 1)
        NewBAMIDgrid.addWidget(self.newcustPostPostcodelbl, 21, 1)

        NewBAMIDgrid.addWidget(self.newcustEmailval, 2, 2)
        NewBAMIDgrid.addWidget(self.newcustFirstNameval, 3, 2)
        NewBAMIDgrid.addWidget(self.newcustMiddleNameval, 4, 2)
        NewBAMIDgrid.addWidget(self.newcustSurnameval, 5, 2)
        NewBAMIDgrid.addWidget(self.newcustMobilePhoneval, 6, 2)
        NewBAMIDgrid.addWidget(self.newcustHomePhoneval, 7, 2)
        NewBAMIDgrid.addWidget(self.newcustWorkPhoneval, 8, 2)
        NewBAMIDgrid.addWidget(self.newcustAddressCountryval, 9, 2)
        NewBAMIDgrid.addWidget(self.newcustAddressStateval, 10, 2)
        NewBAMIDgrid.addWidget(self.newcustAddressStreet1val, 11, 2)
        NewBAMIDgrid.addWidget(self.newcustAddressStreet2val, 12, 2)
        NewBAMIDgrid.addWidget(self.newcustAddressSuburbval, 13, 2)
        NewBAMIDgrid.addWidget(self.newcustAddressPostCodeval, 14, 2)
        NewBAMIDgrid.addWidget(self.newcustPostSameAddressval, 15, 2)
        NewBAMIDgrid.addWidget(self.newcustPostCountryval, 16, 2)
        NewBAMIDgrid.addWidget(self.newcustPostStateval, 17, 2)
        NewBAMIDgrid.addWidget(self.newcustPostStreet1val, 18, 2)
        NewBAMIDgrid.addWidget(self.newcustPostStreet2val, 19, 2)
        NewBAMIDgrid.addWidget(self.newcustPostSuburbval, 20, 2)
        NewBAMIDgrid.addWidget(self.newcustPostPostcodeval, 21, 2)

        #Add create and add check boxes for KYC
        self.KYCDL = QCheckBox("Drivers License", self)
        self.KYCPP = QCheckBox("Passport", self)
        self.KYCMC = QCheckBox("Medicare Card", self)
        self.KYCBS = QCheckBox("Bank Statement", self)

        NewBAMIDgrid.addWidget(self.KYCDL, 2, 3)
        NewBAMIDgrid.addWidget(self.KYCPP, 3, 3)
        NewBAMIDgrid.addWidget(self.KYCMC, 4, 3)
        NewBAMIDgrid.addWidget(self.KYCBS, 5, 3)

        CreateBAMIDButton = QPushButton("Create BAM ID")
        NewBAMIDgrid.addWidget(CreateBAMIDButton, 22, 1)

        tabNewBAMID.setLayout(NewBAMIDgrid)

        # Pull in trasaction when Acct Table view clicked
        CreateBAMIDButton.clicked.connect(self.create_BAMID)

        # ----------------------------------------------------------
        # Add the tabs to the TabWidget
        # ----------------------------------------------------------
        self.TabWidget.addTab(tabCust, "Customer Profile")
        self.TabWidget.addTab(tabAcct, "Accounts")
        self.TabWidget.addTab(tabCP, "Credit Profile")
        self.TabWidget.addTab(tabNewAcctApp, "Open a New Account")
        self.TabWidget.addTab(tabProcessQueue, "Process Queues")
        self.TabWidget.addTab(tabNewBAMID, "Create BAM ID and KYC")

    # -------------------------------------------------------------------
    # Function to pull in the transaction data when an acct is clicked
    # -------------------------------------------------------------------
    def pull_transaction(self, item):
        cellContent = item.data()
        #If an Acct Number clicked i.e. column clicked == 0
        if item.column() == 0:
            #Connect to BAM.db
            db = QSqlDatabase.addDatabase("QSQLITE")
            db.setDatabaseName("/Users/karinacobb/PycharmProjects/BAM.db")
            db.open()

            #Update the Transaction Table View with Transaction based on the Acct clicked
            TransModel = QSqlQueryModel()
            sqlacct = "select * from \"" + self.custBAMIDval.text() + " - Transactions - " + str(cellContent) + "\";"
            TransModel.setQuery(sqlacct, db)
            db.close()
            self.transTv.setModel(TransModel)


    # --------------------------------------------------------------------
    # Function to create new BAMID and associated Acct and Contact Tables
    # --------------------------------------------------------------------
    def create_BAMID(self, item):
        KYCDLState = str(self.KYCDL.checkState())
        KYCPPState = str(self.KYCPP.checkState())
        KYCMCState = str(self.KYCMC.checkState())
        KYCBSState = str(self.KYCBS.checkState())

        #Connect to BAM.db
        con = sqlite3.connect("/Users/karinacobb/PycharmProjects/BAM.db")
        c = con.cursor()
        c.execute("SELECT * FROM {tn} WHERE {cn}='{my_id}'".\
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
                               newcustPostPostcode=self.newcustPostPostcodeval.text(),\
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

    # --------------------------------------------------------------------
    # Function to shift x-axis on the Income, Expense & Debt bar Chart
    # --------------------------------------------------------------------
    def UpdateIncExpDebtChart(self):
        self.chart.axisX(self.series).setRange(self.categories[max(0, self.IncExpDebtChartSlider.value() - 13)], \
                                               self.categories[self.IncExpDebtChartSlider.value()-1])
        self.chartView.setRenderHint(QPainter.Antialiasing)


    @pyqtSlot()
    def on_click_createProfileButton(self):
        self.TabWidget.setCurrentIndex(5)



# if __name__ == '__main__':
#
#     import sys
#
#     app = QApplication(sys.argv)
#     gallery = BAM()
#     gallery.show()
#     sys.exit(app.exec_())
