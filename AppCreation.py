import sqlite3
import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QDoubleValidator

class AppForm(QDialog):
    # Create a dictionary to hold or the customer detail widgets
    AppCusts = dict()

    def __init__(self, UserID):
        super(AppForm, self).__init__()
        self.title = 'Application Form'
        self.setWindowTitle(self.title)

        # This is the BAM User ID passed from the main app to log staff submitting apps and
        # check what products they have access to
        self.UserID = str(UserID)

        # AppForm.AppCust is a dictionary contain the customer detail widgets
        AppForm.AppCusts.clear()
        # When first opening, default is new app this flag is used to create app IDs,
        # if not new app then App ID is already known so new ID isnt' required
        self.isNewApp = True

        # Create the App Details header layout
        self.AppDetailslayoutGroupBox = QGroupBox("Application Details")
        self.AppDetailslayout = QGridLayout()
        self.AppNumberLabel = QLabel('Application #')
        self.AppLastSubLabel = QLabel('Submission #')
        self.AppLastDateLabel = QLabel('Submission Date #')
        self.AppDAReqLabel = QLabel('DA Required')
        self.AppLastDecLabel = QLabel('Decision')
        self.AppLastDecByLabel = QLabel('Decision By')
        self.AppDetailslayout.addWidget(self.AppNumberLabel, 0, 0)
        self.AppDetailslayout.addWidget(self.AppLastSubLabel, 0, 1)
        self.AppDetailslayout.addWidget(self.AppLastDateLabel, 0, 2)
        self.AppDetailslayout.addWidget(self.AppDAReqLabel, 1, 0)
        self.AppDetailslayout.addWidget(self.AppLastDecLabel, 1, 1)
        self.AppDetailslayout.addWidget(self.AppLastDecByLabel, 1, 2)
        self.AppDetailslayoutGroupBox.setLayout(self.AppDetailslayout)

        # Create the top layout - Product Selection
        self.ProductComboBox = QComboBox()
        self.ProductComboBox.addItem("--- Select Product ---")
        self.PurposeComboBox = QComboBox()
        self.PurposeComboBox.addItem("--- Select Purpose ---")
        self.LoanAmount = QLineEdit("Loan Amount or Limit")
        self.InterestRate = QLineEdit("Product Interest Rate")
        self.TermComboBox = QComboBox()

        # Pull back a list of products the User has access to via their Delegated Authority
        con = sqlite3.connect("/Users/karinacobb/PycharmProjects/BAM.db")
        c = con.cursor()
        c.execute("SELECT {fn} FROM {t1n} left join {t2n} on {t1n}.{key} = {t2n}.{key} WHERE {cn}='{my_id}'"
                  .format(fn='Products.*', t1n='UserDAs', t2n='Products', key='ProductID', cn='UserID', my_id=UserID))
        self.ProductList = c.fetchall()
        con.commit()
        con.close()

        # Create a list of products which the user has access to sell
        for ProductList in self.ProductList:
            self.ProductComboBox.addItem(str(ProductList[5]))

        # Create the top layout - Loan Details
        self.toplayoutGroupBox = QGroupBox("Product Selection")
        self.toplayout = QGridLayout()
        self.toplayout.addWidget(self.ProductComboBox, 0, 0, 1, 2)
        self.toplayout.addWidget(self.PurposeComboBox, 0, 2, 1, 2)
        self.toplayout.addWidget(self.LoanAmount,   1, 0, 1, 2)
        self.toplayout.addWidget(self.InterestRate, 1, 2)
        self.toplayoutGroupBox.setLayout(self.toplayout)

        # Create the middle layout - Customer Selection
        self.AddCustButton = QPushButton("Add Customer")
        self.RemoveCustButton = QPushButton("Remove Customer")
        self.SubmitAppButton = QPushButton("Submit Application")
        self.OpenAppButton = QPushButton("Open Application")

        self.midlayoutGroupBox = QGroupBox("Customer Selection")
        self.midlayout = QGridLayout()
        self.midlayout.addWidget(self.AddCustButton, 0, 0)
        self.midlayout.addWidget(self.RemoveCustButton, 0, 1)
        self.midlayout.addWidget(self.OpenAppButton, 0, 2)
        self.midlayout.addWidget(self.SubmitAppButton, 0, 3)
        self.midlayoutGroupBox.setLayout(self.midlayout)

        # Create the bottom layout - Product Application Form
        self.bottomlayoutGroupBox = QGroupBox("Application Form")
        self.bottomlayout = QGridLayout()
        self.bottomlayoutGroupBox.setLayout(self.bottomlayout)

        # Create the labels for the bottom layout - Product Application Form
        self.CreateAppFormLabels()

        # Bring the App Form Top, Mid and Bottom Layouts together and add a submit button
        self.AppFormLayout = QVBoxLayout()
        self.AppFormLayout.addWidget(self.AppDetailslayoutGroupBox)
        self.AppFormLayout.addWidget(self.toplayoutGroupBox)
        self.AppFormLayout.addWidget(self.midlayoutGroupBox)
        self.AppFormLayout.addWidget(self.bottomlayoutGroupBox)
        self.setLayout(self.AppFormLayout)

        # Add the first Customer
        self.AddCust()
        # adding default but this needs to be removed
        AppForm.AppCusts['Customer 1'][2].setText("stevan.cobb@gmail.com")

        # Give the App Form Functionality
        self.ProductComboBox.currentIndexChanged.connect(self.ProductChange)
        self.AddCustButton.clicked.connect(self.AddCust)
        self.RemoveCustButton.clicked.connect(self.RemoveCust)
        self.OpenAppButton.clicked.connect(self.FindApp)
        self.SubmitAppButton.clicked.connect(self.SubmitApp)


    def ProductChange(self, i):
        # Clean the App Form of widgets created from previous product
        self.PurposeComboBox.clear()
        self.TermComboBox.setParent(None)
        self.TermComboBox.clear()

        # Remove the app form widgets
        for widgets in reversed(range(self.bottomlayout.count())):
            self.bottomlayout.itemAt(widgets).widget().setParent(None)

        # Clear out the customer lever combo boxes
        for cust in AppForm.AppCusts:
            AppForm.AppCusts[cust][3].clear()
            AppForm.AppCusts[cust][12].clear()

        # Call the App Form for the selected product which will add the required widgets
        if i != 0:
            getattr(self, "AppForm_" + str(self.ProductList[i - 1][0]))()

    def AddCust(self):
        # This is the customer number for the customer being added
        CustNo = len(AppForm.AppCusts.keys()) + 1

        # Create the widgets for the mid layer customer box
        self.CustLabel = QLabel('Customer {}:'.format(CustNo))
        self.CustLabel2 = QLabel('Customer {}:'.format(CustNo))
        self.CustIDLineEdit = QLineEdit()
        self.CustTypeComboBox = QComboBox()

        # Add them to the layer
        self.midlayout.addWidget(self.CustLabel, CustNo, 0)
        self.midlayout.addWidget(self.CustIDLineEdit, CustNo, 1, 1, 3)
        self.midlayout.addWidget(self.CustTypeComboBox, CustNo, 4)

        # Create the customer widgets for the customer level Product App Form Fields
        self.IncomePAYG = QLineEdit()
        self.IncomeRent = QLineEdit()
        self.IncomeOther = QLineEdit()
        self.IncomeTotal = QLineEdit()
        self.ExpenseRent = QLineEdit()
        self.ExpenseFood = QLineEdit()
        self.ExpenseOther = QLineEdit()
        self.ExpenseTotal = QLineEdit()
        self.EmploymentStatus = QComboBox()

        #Set validation rules
        self.IncomePAYG.setValidator(QDoubleValidator(0.99, 99.99, 2))
        self.IncomeRent.setValidator(QDoubleValidator(0.99, 99.99, 2))
        self.IncomeOther.setValidator(QDoubleValidator(0.99, 99.99, 2))
        self.IncomeTotal.setValidator(QDoubleValidator(0.99, 99.99, 2))
        self.ExpenseRent.setValidator(QDoubleValidator(0.99, 99.99, 2))
        self.ExpenseFood.setValidator(QDoubleValidator(0.99, 99.99, 2))
        self.ExpenseOther.setValidator(QDoubleValidator(0.99, 99.99, 2))
        self.ExpenseTotal.setValidator(QDoubleValidator(0.99, 99.99, 2))

        # Create a list of Widgets and add them to the dictionary for use elsewhere
        self.CustWidgetList = [self.CustLabel,
                               self.CustLabel2, #The app form has 2 customer so need 2 widgets
                               self.CustIDLineEdit,
                               self.CustTypeComboBox,
                               self.IncomePAYG,
                               self.IncomeRent,
                               self.IncomeOther,
                               self.IncomeTotal,
                               self.ExpenseRent,
                               self.ExpenseFood,
                               self.ExpenseOther,
                               self.ExpenseTotal,
                               self.EmploymentStatus]

        AppForm.AppCusts['Customer {}'.format(CustNo)] = self.CustWidgetList

        # Call the App Form for the selected product which will add the required widgets
        index = self.ProductComboBox.currentIndex()
        if index != 0:
            getattr(self, "AppForm_" + str(self.ProductList[index - 1][0]))()

    def RemoveCust(self):

        # Remove the last customer added, with error msg box back to user
        # explaining an Application needs at least 1 customer
        if len(AppForm.AppCusts.keys()) == 1:
            self.NeedCustMsgBox = QMessageBox()
            self.NeedCustMsgBox.setText("Need at least 1 customer")
            self.NeedCustMsgBox.setIcon(QMessageBox.Information)
            self.NeedCustMsgBox.exec_()
        else:
            Cust = 'Customer {}'.format(len(AppForm.AppCusts.keys()))
            # Remove widgets from Customer Selection Layer
            AppForm.AppCusts[Cust][0].setParent(None)
            AppForm.AppCusts[Cust][2].setParent(None)
            AppForm.AppCusts[Cust][3].setParent(None)

            # Remove customer widgets from the AppCusts dictionary
            AppForm.AppCusts.pop(Cust)

            # Clear all widgets from Product App Form
            for widgets in reversed(range(self.bottomlayout.count())):
                self.bottomlayout.itemAt(widgets).widget().setParent(None)

            # Call the App Form for the selected product which will add the required widgets
            index = self.ProductComboBox.currentIndex()
            if index != 0:
                getattr(self, "AppForm_" + str(self.ProductList[index - 1][0]))()

        self.AppForm_Total_Calcs()

    def FindApp(self):
        #Create Pop Up to enter AppNo & Submission No (Will need to check user authority one day)
        self.OpenAppobj = OpenApp()
        self.OpenAppobj.exec_()

        #Load in the App Data
        self.OpenApp(self.OpenAppobj.AppNoBoxVal, self.OpenAppobj.SubmissionBoxVal)

    def OpenApp(self, AppNo, SubNo):
        #Sql to pull back Application data from BAM.db
        con = sqlite3.connect('/Users/karinacobb/PycharmProjects/BAM.db')
        c = con.cursor()
        # Pull back App Details
        c.execute("SELECT * FROM {tn} WHERE {cn1}='{AppNumber}' and {cn2}='{SubmissionNo}'"
                  .format(tn='Applications', cn1='AppNo', cn2='Submission',
                          AppNumber=AppNo, SubmissionNo=SubNo))
        self.AppDetails = c.fetchone()

        # Pull back customer application details
        c.execute("SELECT * FROM {tn} WHERE {cn1}='{AppNumber}' and {cn2}='{SubmissionNo}'"
                  .format(tn='CustApplRel', cn1='AppNo', cn2='Submission',
                          AppNumber=AppNo, SubmissionNo=SubNo))
        self.CustAppDetails = c.fetchall()
        con.close()

        #if the query has  a results (which it always should) load the values into the form
        if self.AppDetails is not None:
            self.isNewApp = False

            #Load in app details
            self.AppNumberLabel.setText('Application # ' + str(self.AppDetails[1]))
            self.AppLastSubLabel.setText('Submission # ' + str(self.AppDetails[15]))
            self.AppLastDateLabel.setText('Submission Date: ' + str(self.AppDetails[17]))
            self.AppDAReqLabel.setText('DA Required: ' + str(self.AppDetails[18]))
            self.AppLastDecLabel.setText('Decision: ' + str(self.AppDetails[19]))
            self.AppLastDecByLabel.setText('Decision By: ' + str(self.AppDetails[20]))

            self.ProductComboBox.setCurrentText(str(self.AppDetails[2]))
            self.PurposeComboBox.setCurrentText(str(self.AppDetails[3]))
            self.LoanAmount.setText(str(self.AppDetails[4]))
            self.InterestRate.setText(str(self.AppDetails[5]))
            self.TermComboBox.setCurrentText(str(self.AppDetails[6]))

            # Remove any existing custome widgets and load in customer application details
            for i in range(len(AppForm.AppCusts.keys()) - 1):
                self.RemoveCust()

            # Load the Customer Application details into the widgets
            for count, cust in enumerate(self.CustAppDetails):
                if self.CustAppDetails[count][4] != 1: self.AddCust()

                custload = 'Customer '+ str(self.CustAppDetails[count][4])
                AppForm.AppCusts[custload][0].setText(custload)
                AppForm.AppCusts[custload][1].setText(custload)
                AppForm.AppCusts[custload][2].setText(str(self.CustAppDetails[count][1]))
                AppForm.AppCusts[custload][3].setCurrentText(str(self.CustAppDetails[count][5]))
                AppForm.AppCusts[custload][4].setText(str(self.CustAppDetails[count][6]))
                AppForm.AppCusts[custload][5].setText(str(self.CustAppDetails[count][7]))
                AppForm.AppCusts[custload][6].setText(str(self.CustAppDetails[count][8]))
                AppForm.AppCusts[custload][7].setText(str(self.CustAppDetails[count][9]))
                AppForm.AppCusts[custload][8].setText(str(self.CustAppDetails[count][10]))
                AppForm.AppCusts[custload][9].setText(str(self.CustAppDetails[count][11]))
                AppForm.AppCusts[custload][10].setText(str(self.CustAppDetails[count][12]))
                AppForm.AppCusts[custload][11].setText(str(self.CustAppDetails[count][13]))
                AppForm.AppCusts[custload][12].setCurrentText(str(self.CustAppDetails[count][14]))

                #Lock the product combo box
                self.ProductComboBox.setEnabled(False)

    def SubmitApp(self):
        CustNotFound = 0
        BAMIDList = []

        # Check all customers exists
        for cust in AppForm.AppCusts:
            # Import customer profile data for the Customer Profile Tab
            con = sqlite3.connect("/Users/karinacobb/PycharmProjects/BAM.db")
            c = con.cursor()
            c.execute("SELECT * FROM {tn} WHERE {cn}='{my_id}'".format(tn='CustomerProfiles', cn='Email',
                                                                       my_id=AppForm.AppCusts[cust][2].text()))
            CustProfile = c.fetchone()
            con.close()

            # Create a list of BAM IDs to pass when submitting to the Customer Application table
            # return error message if customer not found
            if CustProfile == None:
                msgBox = QMessageBox()
                msgBox.setText(str(cust) + ' not found please check email or perform KYC')
                msgBox.setIcon(QMessageBox.Information)
                msgBox.exec_()
                CustNotFound += 1
                BAMIDList.append("")
            else:
                BAMIDList.append(CustProfile[0])

        # If all customers exists submit the app data to the database
        if CustNotFound == 0:
            con = None
            con = sqlite3.connect('/Users/karinacobb/PycharmProjects/BAM.db')
            #Insert new app details
            AppInsert = con.cursor()
            AppInsert.execute('INSERT INTO {AppTable} VALUES ({SubmissionKey},   {AppNo},  \
                              "{ProductID}",          "{Purpose}",           "{LoanAmount}",  \
                              "{InterestRate}",       "{Term}",              "{IncomePAYGAppTot}",  \
                              "{IncomeRentAppTot}",   "{IncomeOtherAppTot}", "{IncomeTotalAppTot}",  \
                              "{ExpenseRentAppTot}",  "{ExpenseFoodAppTot}", "{ExpenseOtherAppTot}",  \
                              "{ExpenseTotalAppTot}",  {Submission},         "{SubmissionBy}",  \
                              "{SubmissionDate}",     "{DARequired}",        "{Decision}", \
                              "{DecisionBy}")'. \
                       format(AppTable = 'APPLICATIONS', \
                              SubmissionKey='null', \
                              AppNo='null' if self.isNewApp == True else self.AppDetails[1], \
                              ProductID=self.ProductComboBox.currentText(), \
                              Purpose=self.PurposeComboBox.currentText(), \
                              LoanAmount=self.LoanAmount.text(), \
                              InterestRate=self.InterestRate.text(), \
                              Term=self.TermComboBox.currentText(), \
                              IncomePAYGAppTot=self.IncomePAYGAppTotLabel.text(), \
                              IncomeRentAppTot=self.IncomeRentAppTotLabel.text(), \
                              IncomeOtherAppTot=self.IncomeOtherAppTotLabel.text(), \
                              IncomeTotalAppTot=self.IncomeTotalAppTotLabel.text(), \
                              ExpenseRentAppTot=self.ExpenseRentAppTotLabel.text(), \
                              ExpenseFoodAppTot=self.ExpenseFoodAppTotLabel.text(), \
                              ExpenseOtherAppTot=self.ExpenseOtherAppTotLabel.text(), \
                              ExpenseTotalAppTot= self.ExpenseTotalAppTotLabel.text(), \
                              Submission='null', \
                              SubmissionBy=self.UserID, \
                              SubmissionDate=str(datetime.datetime.now()), \
                              DARequired="null", \
                              Decision="null", \
                              DecisionBy="null"))

            #would be good to update to SQL 3.35 and use returning
            #create table users(id integer primary key, first_name text, last_name text);
            #insert into users(first_name, last_name) values('Jane', 'Doe') returning id;

            #Pull back the submitted App Details
            InsertedAppCur = con.cursor()
            InsertedAppCur.execute('select * from {AppTable} where {SK} = {SubKey}'. \
                              format(AppTable='APPLICATIONS', SK='SubmissionKey', SubKey=AppInsert.lastrowid))
            InsertedApp = InsertedAppCur.fetchone()
            con.commit()
            con.close()

            # Insert the Customer level application details in the BAM database
            for count, cust in enumerate(AppForm.AppCusts):
                con = None
                con = sqlite3.connect('/Users/karinacobb/PycharmProjects/BAM.db')
                CustAppInsert = con.cursor()
                CustAppInsert.execute('INSERT INTO {CustAppTable} VALUES ("{BAMID}",   "{Email}",   {AppNo}, \
                                      "{Submission}",     "{CustNo}",         "{CustType}", \
                                      "{IncomePAYG}",     "{IncomeRent}",     "{IncomeOther}", \
                                      "{IncomeTotal}",    "{ExpenseRent}",    "{ExpenseFood}", \
                                      "{ExpenseOther}",   "{ExpenseTotal}",   "{EmploymentStatus}")'. \
                                      format(CustAppTable='CUSTAPPLREL', \
                                             BAMID=BAMIDList[count], \
                                             Email=AppForm.AppCusts[cust][2].text(), \
                                             AppNo=InsertedApp[1], \
                                             Submission=InsertedApp[15], \
                                             CustNo=count + 1, \
                                             CustType=AppForm.AppCusts[cust][3].currentText(), \
                                             IncomePAYG=AppForm.AppCusts[cust][4].text(), \
                                             IncomeRent=AppForm.AppCusts[cust][5].text(), \
                                             IncomeOther=AppForm.AppCusts[cust][6].text(), \
                                             IncomeTotal=AppForm.AppCusts[cust][7].text(), \
                                             ExpenseRent=AppForm.AppCusts[cust][8].text(), \
                                             ExpenseFood=AppForm.AppCusts[cust][9].text(), \
                                             ExpenseOther=AppForm.AppCusts[cust][10].text(), \
                                             ExpenseTotal=AppForm.AppCusts[cust][11].text(), \
                                             EmploymentStatus=AppForm.AppCusts[cust][12].currentText()))
                con.commit()
                con.close()

            #Let user know the app was submitted
            msgBox = QMessageBox()
            msgBox.setText('Application Created')
            msgBox.setIcon(QMessageBox.Information)
            msgBox.exec_()

            #Lock the product combo box
            self.ProductComboBox.setEnabled(False)

            # Refresh the app data by using the open function to load the submitted app into the form
            self.OpenApp(InsertedApp[1], InsertedApp[15])

    def CreateAppFormLabels(self):
        # Create App Form Variable Labels
        self.DDLabel = QLabel("Direct Debt Account No Further Info Required")
        self.IncomePAYGLabel = QLabel("IncomePAYG:")
        self.IncomeRentLabel = QLabel("IncomeRent:")
        self.IncomeOtherLabel = QLabel("IncomeOther:")
        self.IncomeTotalLabel = QLabel("IncomeTotal:")
        self.ExpenseRentLabel = QLabel("ExpenseRent:")
        self.ExpenseFoodLabel = QLabel("ExpenseFood:")
        self.ExpenseOtherLabel = QLabel("ExpenseOther:")
        self.ExpenseTotalLabel = QLabel("ExpenseTotal:")
        self.EmploymentStatusLabel = QLabel("Employment Status:")

        #Create label place holders for App Totals
        self.AppTotLabel = QLabel("App Total")
        self.IncomePAYGAppTotLabel = QLabel("0.00")
        self.IncomeRentAppTotLabel = QLabel("0.00")
        self.IncomeOtherAppTotLabel = QLabel("0.00")
        self.IncomeTotalAppTotLabel = QLabel("0.00")
        self.ExpenseRentAppTotLabel = QLabel("0.00")
        self.ExpenseFoodAppTotLabel = QLabel("0.00")
        self.ExpenseOtherAppTotLabel = QLabel("0.00")
        self.ExpenseTotalAppTotLabel = QLabel("0.00")

    def AppForm_1(self): #ANZ Access Advantage
        self.AppForm1PurposeList = ["--- Select Purpose ---", "Transacting"]
        self.AppForm1CustTypeList = ["--- Select Customer Type ---", "Primary", "Secondary"]

        # Set the Product combo box list items
        if self.PurposeComboBox.count() == 0:
            self.PurposeComboBox.addItems(self.AppForm1PurposeList)

        # Set the Customer combo box list items
        for i in AppForm.AppCusts:
            if AppForm.AppCusts[i][3].count() == 0:
                AppForm.AppCusts[i][3].addItems(self.AppForm1CustTypeList)

        self.bottomlayout.addWidget(self.DDLabel, 0, 0)

    def AppForm_6(self): #ANZ Online Saver
        self.AppForm6PurposeList = ["--- Select Purpose ---", "Transacting"]
        self.AppForm6CustTypeList = ["--- Select Customer Type ---", "Primary", "Secondary"]

        # Set the Product combo box list items
        if self.PurposeComboBox.count() == 0:
            self.PurposeComboBox.addItems(self.AppForm6PurposeList)

        # Set the Customer combo box list items
        for i in AppForm.AppCusts:
            if AppForm.AppCusts[i][3].count() == 0:
                AppForm.AppCusts[i][3].addItems(self.AppForm6CustTypeList)

        self.bottomlayout.addWidget(self.DDLabel, 0, 0)

    def AppForm_13(self): #ANZ Rewards
        # Create Combo Box lists for the form
        self.AppForm13PurposeList = ["--- Select Purpose ---", "Transacting"]
        self.AppForm13CustTypeList = ["--- Select Customer Type ---", "Primary", "Secondary"]
        self.AppForm13EmploymentStatus = ["--- Select Employment Status ---", "Full Time", "Part Time"]

        # Set the Product combo box list items
        if self.PurposeComboBox.count() == 0:
            self.PurposeComboBox.addItems(self.AppForm13PurposeList)

        # Add bottom layout labels
        self.bottomlayout.addWidget(self.IncomeTotalLabel, 1, 0)
        self.bottomlayout.addWidget(self.ExpenseTotalLabel, 2, 0)
        self.bottomlayout.addWidget(self.EmploymentStatusLabel, 3, 0)

        # Add bottom layout App Total labels
        self.bottomlayout.addWidget(self.AppTotLabel, 0, 1)
        self.bottomlayout.addWidget(self.IncomeTotalAppTotLabel, 1, 1)
        self.bottomlayout.addWidget(self.ExpenseTotalAppTotLabel, 2, 1)


        # Add customer widgets
        for count, cust in enumerate(AppForm.AppCusts):

            # Set the Customer combo box list items
            if AppForm.AppCusts[cust][3].count() == 0:
                AppForm.AppCusts[cust][3].addItems(self.AppForm13CustTypeList)
            if AppForm.AppCusts[cust][12].count() == 0:
                AppForm.AppCusts[cust][12].addItems(self.AppForm13EmploymentStatus)

            # Add the customer number title, income total, expense total and employment status and
            # signal connections to refresh totals when these are changed
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][1],  0, count + 2)
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][7],  1, count + 2)
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][11], 2, count + 2)
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][12], 3, count + 2)
            AppForm.AppCusts[cust][7].textChanged.connect(self.AppForm_Total_Calcs)
            AppForm.AppCusts[cust][11].textChanged.connect(self.AppForm_Total_Calcs)

    def AppForm_20(self): #ANZ Standard Variable
        self.AppForm20PurposeList = ["--- Select Purpose ---", "Owner Occupied", "Investment"]
        self.AppForm20TermList = ["--- Select Term ---", "20 Year", "30 Year"]
        self.AppForm20CustTypeList = ["--- Select Customer Type ---", "Sole Borrower", "Co Borrower"]
        self.AppForm20EmploymentStatus = ["--- Select Employment Status ---", "Full Time", "Part Time"]

        # Set the Product combo box list items
        if self.PurposeComboBox.count() == 0:
            self.PurposeComboBox.addItems(self.AppForm20PurposeList)
            self.toplayout.addWidget(self.TermComboBox, 1, 3)
            self.TermComboBox.addItems(self.AppForm20TermList)

        # Add bottom layout data labels
        self.bottomlayout.addWidget(self.IncomePAYGLabel, 1, 0)
        self.bottomlayout.addWidget(self.IncomeRentLabel, 2, 0)
        self.bottomlayout.addWidget(self.IncomeOtherLabel, 3, 0)

        self.bottomlayout.addWidget(self.ExpenseRentLabel, 4, 0)
        self.bottomlayout.addWidget(self.ExpenseFoodLabel, 5, 0)
        self.bottomlayout.addWidget(self.ExpenseOtherLabel, 6, 0)

        self.bottomlayout.addWidget(self.EmploymentStatusLabel, 7, 0)

        # Add bottom layout App Total labels
        self.bottomlayout.addWidget(self.AppTotLabel, 0, 1)
        self.bottomlayout.addWidget(self.IncomePAYGAppTotLabel, 1, 1)
        self.bottomlayout.addWidget(self.IncomeRentAppTotLabel, 2, 1)
        self.bottomlayout.addWidget(self.IncomeOtherAppTotLabel, 3, 1)
        self.bottomlayout.addWidget(self.ExpenseRentAppTotLabel, 4, 1)
        self.bottomlayout.addWidget(self.ExpenseFoodAppTotLabel, 5, 1)
        self.bottomlayout.addWidget(self.ExpenseOtherAppTotLabel, 6, 1)

        # Add customer widgets
        for count, cust in enumerate(AppForm.AppCusts):
            # Set the Customer combo box list items
            if AppForm.AppCusts[cust][3].count() == 0:
                AppForm.AppCusts[cust][3].addItems(self.AppForm20CustTypeList)
            if AppForm.AppCusts[cust][12].count() == 0:
                AppForm.AppCusts[cust][12].addItems(self.AppForm20EmploymentStatus)

            #Add the customer number title
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][1], 0, count + 2)
            #Income Fields and signal connections to refresh totals when these are changed
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][4], 1, count + 2)
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][5], 2, count + 2)
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][6], 3, count + 2)
            AppForm.AppCusts[cust][4].textChanged.connect(self.AppForm_Total_Calcs)
            AppForm.AppCusts[cust][5].textChanged.connect(self.AppForm_Total_Calcs)
            AppForm.AppCusts[cust][6].textChanged.connect(self.AppForm_Total_Calcs)

            #Expense Fields and signal connections to refresh totals when these are changed
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][8], 4, count + 2)
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][9], 5, count + 2)
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][10], 6, count + 2)
            AppForm.AppCusts[cust][8].textChanged.connect(self.AppForm_Total_Calcs)
            AppForm.AppCusts[cust][9].textChanged.connect(self.AppForm_Total_Calcs)
            AppForm.AppCusts[cust][10].textChanged.connect(self.AppForm_Total_Calcs)

            #Employment Status Field
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][12], 7, count + 2)

    def AppForm_27(self): #ANZ Variable Rate Loan

        self.AppForm27PurposeList = ["--- Select Purpose ---", "Car/Vehicle Purchase", "Debt Consolidation", "Travel", "Renovation", "Other"]
        self.AppForm27TermList = ["--- Select Term ---", "5 Year", "7 Year"]
        self.AppForm27CustTypeList = ["--- Select Customer Type ---", "Sole Borrower", "Co Borrower"]
        self.AppForm27EmploymentStatus = ["--- Select Employment Status ---", "Full Time", "Part Time"]

        # Set the Product combo box list items
        if self.PurposeComboBox.count() == 0:
            self.PurposeComboBox.addItems(self.AppForm27PurposeList)
            self.toplayout.addWidget(self.TermComboBox, 1, 3)
            self.TermComboBox.addItems(self.AppForm27TermList)

        # Add bottom layout data labels
        self.bottomlayout.addWidget(self.IncomeTotalLabel, 1, 0)
        self.bottomlayout.addWidget(self.ExpenseTotalLabel, 2, 0)
        self.bottomlayout.addWidget(self.EmploymentStatusLabel, 3, 0)

        # Add bottom layout App Total labels
        self.bottomlayout.addWidget(self.AppTotLabel, 0, 1)
        self.bottomlayout.addWidget(self.IncomeTotalAppTotLabel, 1, 1)
        self.bottomlayout.addWidget(self.ExpenseTotalAppTotLabel, 2, 1)

        # Add customer widgets
        for count, cust in enumerate(AppForm.AppCusts):
            # Set the Customer combo box list items
            if AppForm.AppCusts[cust][3].count() == 0:
                AppForm.AppCusts[cust][3].addItems(self.AppForm27CustTypeList)
            if AppForm.AppCusts[cust][12].count() == 0:
                AppForm.AppCusts[cust][12].addItems(self.AppForm27EmploymentStatus)

            # Add the customer number title, income total, expense total and employment status and
            # signal connections to refresh totals when these are changed
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][1],  0, count + 2)
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][7],  1, count + 2)
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][11], 2, count + 2)
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][12], 3, count + 2)
            AppForm.AppCusts[cust][7].textChanged.connect(self.AppForm_Total_Calcs)
            AppForm.AppCusts[cust][11].textChanged.connect(self.AppForm_Total_Calcs)

    def AppForm_28(self): #ANZ Fixed Rate Loan
        self.AppForm28PurposeList = ["--- Select Purpose ---", "Car/Vehicle Purchase", "Debt Consolidation", "Travel", "Renovation", "Other"]
        self.AppForm28TermList = ["--- Select Term ---", "5 Year", "7 Year"]
        self.AppForm28CustTypeList = ["--- Select Customer Type ---", "Sole Borrower", "Co Borrower"]
        self.AppForm28EmploymentStatus = ["--- Select Employment Status ---", "Full Time", "Part Time"]

        # Set the Product combo box list items
        if self.PurposeComboBox.count() == 0:
            self.PurposeComboBox.addItems(self.AppForm28PurposeList)
            self.toplayout.addWidget(self.TermComboBox, 1, 3)
            self.TermComboBox.addItems(self.AppForm28TermList)

        # Add bottom layout data labels
        self.bottomlayout.addWidget(self.IncomeTotalLabel, 1, 0)
        self.bottomlayout.addWidget(self.ExpenseTotalLabel, 2, 0)
        self.bottomlayout.addWidget(self.EmploymentStatusLabel, 3, 0)

        # Add bottom layout App Total labels
        self.bottomlayout.addWidget(self.AppTotLabel, 0, 1)
        self.bottomlayout.addWidget(self.IncomeTotalAppTotLabel, 1, 1)
        self.bottomlayout.addWidget(self.ExpenseTotalAppTotLabel, 2, 1)


        # Add customer widgets
        for count, cust in enumerate(AppForm.AppCusts):
            # Set the Customer combo box list items
            if AppForm.AppCusts[cust][3].count() == 0:
                AppForm.AppCusts[cust][3].addItems(self.AppForm28CustTypeList)
            if AppForm.AppCusts[cust][12].count() == 0:
                AppForm.AppCusts[cust][12].addItems(self.AppForm28EmploymentStatus)

            # Add the customer number title, income total, expense total and employment status and
            # signal connections to refresh totals when these are changed
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][1],  0, count + 2)
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][7],  1, count + 2)
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][11], 2, count + 2)
            self.bottomlayout.addWidget(AppForm.AppCusts[cust][12], 3, count + 2)
            AppForm.AppCusts[cust][7].textChanged.connect(self.AppForm_Total_Calcs)
            AppForm.AppCusts[cust][11].textChanged.connect(self.AppForm_Total_Calcs)

    def AppForm_Total_Calcs(self):

        #Set the app total values to 0.00, the loop below will sum up the values
        self.IncomePAYGAppTot = 0.00
        self.IncomeRentAppTot = 0.00
        self.IncomeOtherAppTot = 0.00
        self.IncomeTotalAppTot = 0.00
        self.ExpenseRentAppTot = 0.00
        self.ExpenseFoodAppTot = 0.00
        self.ExpenseOtherAppTot = 0.00
        self.ExpenseTotalAppTot = 0.00

        #Loop through for each customer converting the text values to float and then add them to the running total
        for cust in AppForm.AppCusts:
            # If text box value null set it to 0.00 so the addition works
            IncomePAYG = 0.00 if AppForm.AppCusts[cust][4].text() == "" else float(str(AppForm.AppCusts[cust][4].text()))
            IncomeRent = 0.00 if AppForm.AppCusts[cust][5].text() == "" else float(str(AppForm.AppCusts[cust][5].text()))
            IncomeOther = 0.00 if AppForm.AppCusts[cust][6].text() == "" else float(str(AppForm.AppCusts[cust][6].text()))
            IncomeTotal = 0.00 if AppForm.AppCusts[cust][7].text() == "" else float(str(AppForm.AppCusts[cust][7].text()))
            ExpenseRent = 0.00 if AppForm.AppCusts[cust][8].text() == "" else float(str(AppForm.AppCusts[cust][8].text()))
            ExpenseFood = 0.00 if AppForm.AppCusts[cust][9].text() == "" else float(str(AppForm.AppCusts[cust][9].text()))
            ExpenseOther = 0.00 if AppForm.AppCusts[cust][10].text() == "" else float(str(AppForm.AppCusts[cust][10].text()))
            ExpenseTotal = 0.00 if AppForm.AppCusts[cust][11].text() == "" else float(str(AppForm.AppCusts[cust][11].text()))

            # Update running total with the values from the loop
            self.IncomePAYGAppTot = self.IncomePAYGAppTot + IncomePAYG
            self.IncomeRentAppTot = self.IncomeRentAppTot + IncomeRent
            self.IncomeOtherAppTot = self.IncomeOtherAppTot + IncomeOther
            self.IncomeTotalAppTot = self.IncomeTotalAppTot + IncomeTotal
            self.ExpenseRentAppTot = self.ExpenseRentAppTot + ExpenseRent
            self.ExpenseFoodAppTot = self.ExpenseFoodAppTot + ExpenseFood
            self.ExpenseOtherAppTot = self.ExpenseOtherAppTot + ExpenseOther
            self.ExpenseTotalAppTot = self.ExpenseTotalAppTot + ExpenseTotal

        # Set the AppTot Labels to the totals calculated above
        self.IncomePAYGAppTotLabel.setText(str(self.IncomePAYGAppTot))
        self.IncomeRentAppTotLabel.setText(str(self.IncomeRentAppTot))
        self.IncomeOtherAppTotLabel.setText(str(self.IncomeOtherAppTot))
        self.IncomeTotalAppTotLabel.setText(str(self.IncomeTotalAppTot))
        self.ExpenseRentAppTotLabel.setText(str(self.ExpenseRentAppTot))
        self.ExpenseFoodAppTotLabel.setText(str(self.ExpenseFoodAppTot))
        self.ExpenseOtherAppTotLabel.setText(str(self.ExpenseOtherAppTot))
        self.ExpenseTotalAppTotLabel.setText(str(self.ExpenseTotalAppTot))

class OpenApp(QDialog):

    def __init__(self):
        super().__init__()

        self.AppNoBoxVal = None
        self.SubmissionBoxVal = None

        self.title = 'Open Application'
        self.setWindowTitle(self.title)
        self.resize(320, 100)
        self.center()

        self.AppNoLabel = QLabel("Application Number:")
        self.AppNoBox = QLineEdit()
        self.SubmissionLabel = QLabel("Submission:")
        self.SubmissionBox = QComboBox()
        self.OpenAppButton = QPushButton("Open App", self)

        self.horizontalGroupBox = QGroupBox("Open Application")
        self.layout = QGridLayout()
        self.layout.addWidget(self.AppNoLabel, 0, 0)
        self.layout.addWidget(self.AppNoBox, 0, 1)
        self.layout.addWidget(self.SubmissionLabel, 1, 0)
        self.layout.addWidget(self.SubmissionBox, 1, 1)
        self.layout.addWidget(self.OpenAppButton, 2, 0)
        self.horizontalGroupBox.setLayout(self.layout)

        #Signals to update submission number and load in application data
        self.AppNoBox.textChanged[str].connect(lambda: self.on_AppNo_change(self.AppNoBox.text()))
        self.OpenAppButton.clicked.connect(lambda: self.on_OpenApp_click(self.AppNoBox.text(),self.SubmissionBox.currentText()))

        self.windowLayout = QVBoxLayout()
        self.windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(self.windowLayout)


    @pyqtSlot()
    def on_AppNo_change(self, AppNo):
        self.SubmissionBox.clear()

        con = sqlite3.connect('/Users/karinacobb/PycharmProjects/BAM.db')
        c = con.cursor()
        for row in c.execute("SELECT {cn2} FROM {tn} WHERE {cn1}='{AppNumber}' ORDER BY {cn2}"
                             .format(tn='Applications', cn1='AppNo', cn2='Submission', AppNumber=AppNo)):
            self.SubmissionBox.addItem(str(row[0]))
        con.close()

    @pyqtSlot()
    def on_OpenApp_click(self, AppNo, SubNo):
        con = sqlite3.connect('/Users/karinacobb/PycharmProjects/BAM.db')
        c = con.cursor()
        c.execute("SELECT * FROM {tn} WHERE {cn1}='{AppNumber}' and {cn2}='{SubmissionNo}'"
                .format(tn='Applications', cn1='AppNo', cn2='Submission', AppNumber=AppNo, SubmissionNo=SubNo))
        AppDetails = c.fetchone()
        con.close()

        if AppDetails == None:
             msgBox = QMessageBox()
             msgBox.setText("Application Not Found.")
             msgBox.setIcon(QMessageBox.Information)
             msgBox.exec_()
        else:
            #Returning values for App No and Submission No
            self.AppNoBoxVal = AppNo
            self.SubmissionBoxVal = SubNo


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

# if __name__ == "__main__":
#    import sys
#    app = QApplication(sys.argv)
#    form = FORM()
#    form.show()
#    sys.exit(app.exec_())
