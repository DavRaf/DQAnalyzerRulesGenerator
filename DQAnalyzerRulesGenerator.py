from RulesManager import RulesManager
from XMLFileManager import XMLFileManager
import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QFileDialog, QMainWindow, QWidget, QVBoxLayout, \
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QLabel, QFormLayout, QLineEdit
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage, QFont
import subprocess
import os

'''xml_file_manager = XMLFileManager()
profiles, profiles_in_json = xml_file_manager.read_profile('1.2 Advanced.profile.xml')
files = ['expressions.common.templates', 'expressions.usc.templates', 'regex.common.templates']
rules_templates = xml_file_manager.read_rules_expressions_advanced(files)
rules_manager = RulesManager()
for profile in profiles:
    rules_manager.generate_date_rules(profile)
    rules_manager.generate_ssn_rules(profile)
    rules_manager.generate_fiscal_code_rules(profile)
    rules_manager.generate_len_number_rules(profile)
    rules_manager.generate_email_rules(profile)
    rules_manager.generate_iban_rules(profile)
    rules_manager.generate_ipv4_rules(profile)
    rules_manager.generate_phone_rules(profile)'''

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        loadUi('dq_analyzer_rules_generator.ui', self)
        self.xml_file_manager = XMLFileManager()
        self.profiles = None
        self.action_load_profile_file.triggered.connect(self.load_profile_file)
        self.action_generate_rules.triggered.connect(self.generate_rules)

    def generate_rules(self):
        dialog = Dialog()
        dialog.setWindowTitle('DQ Analyzer Rules Generator')
        dialog.show()
        dialog.exec_()


    def open_stuff(self, filename):
        if sys.platform == "win32":
            try:
                os.startfile(filename)
            except:
                QMessageBox.critical(self, "Failed", "File not found.")
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])

    def load_profile_file(self):
        self.filename = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\', "XML files (*profile.xml)")
        if self.filename[0] is "":
            QMessageBox.critical(self, "File not selected", "You don't have selected any file.")
            return
        self.profiles, profiles_in_json = self.xml_file_manager.read_profile(self.filename[0])
        myFont = QFont()
        myFont.setBold(True)
        self.tabs = self.tabWidget
        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, self.filename[0])
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(self.profiles))
        self.tableWidget.setColumnCount(10)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderLabels(["Expression", "Type", "Domain", "Non-null", "Null", "Unique", "Distinct", "Min", "Median", "Max"])
        self.expressions = []
        self.expression_types = []
        self.expression_domains = []
        for profile in self.profiles:
            self.expressions.append(profile.expression_name)
            self.expression_types.append(profile.expression_type)
            self.expression_domains.append(profile.domain_name)
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 0, QTableWidgetItem(self.expressions[x]))
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 1, QTableWidgetItem(self.expression_types[x]))
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 2, QTableWidgetItem(self.expression_domains[x]))
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget2 = QTableWidget() #table for showing domain analysis
        self.tableWidget3 = QTableWidget() #table for showing mask analysis
        self.label1 = QLabel()
        self.label1.setText("Column Analyses")
        self.label1.setFont(myFont)
        self.label2 = QLabel()
        self.label2.setText("Domain Analysis")
        self.label2.setFont(myFont)
        self.label3 = QLabel()
        self.label3.setText("Mask Analysis")
        self.label3.setFont(myFont)
        self.tableWidget.itemClicked.connect(self.handle_item_clicked)
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.addWidget(self.label1)
        self.tab1.layout.addWidget(self.tableWidget)
        self.tab1.setLayout(self.tab1.layout)

    def handle_item_clicked(self):
        expression_name = str((self.tableWidget.item(self.tableWidget.currentItem().row(), 0)).text())
        current_profile = None
        for profile in self.profiles:
            if profile.expression_name == expression_name:
                current_profile = profile

        if current_profile.domain_analysis:
            self.tab1.layout.addWidget(self.label2)
            self.tableWidget2.setRowCount(len(current_profile.domain_analysis))
            self.tableWidget2.setColumnCount(2)
            self.tableWidget2.verticalHeader().setVisible(False)
            self.tableWidget2.setHorizontalHeaderLabels(["Num Cases", "Value"])
            self.values = []
            self.num_cases_list = []
            for d_a in current_profile.domain_analysis:
                self.num_cases_list.append(d_a.num_cases)
                if not d_a.value:
                    self.values.append("NULL")
                else:
                    self.values.append(d_a.value)
            for x in range(0, len(current_profile.domain_analysis)):
                self.tableWidget2.setItem(x, 0, QTableWidgetItem(self.num_cases_list[x]))
            for x in range(0, len(current_profile.domain_analysis)):
                self.tableWidget2.setItem(x, 1, QTableWidgetItem(self.values[x]))
            self.tableWidget2.setEditTriggers(QTableWidget.NoEditTriggers)
            self.tableWidget2.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tab1.layout.addWidget(self.tableWidget2)
            self.tab1.setLayout(self.tab1.layout)

        if current_profile.mask_analysis:
            self.tab1.layout.addWidget(self.label3)
            self.tableWidget3.setRowCount(len(current_profile.mask_analysis))
            self.tableWidget3.setColumnCount(3)
            self.tableWidget3.verticalHeader().setVisible(False)
            self.tableWidget3.setHorizontalHeaderLabels(["Count", "Percent", "Value"])
            self.values = []
            self.counts = []
            self.percents = []
            for m_a in current_profile.mask_analysis:
                if not m_a.value:
                    self.values.append("NULL")
                else:
                    self.values.append(m_a.value)
                self.counts.append(m_a.count)
                self.percents.append(m_a.percent)
            for x in range(0, len(current_profile.mask_analysis)):
                self.tableWidget3.setItem(x, 0, QTableWidgetItem(self.counts[x]))
            for x in range(0, len(current_profile.mask_analysis)):
                self.tableWidget3.setItem(x, 1, QTableWidgetItem(self.percents[x]))
            for x in range(0, len(current_profile.mask_analysis)):
                self.tableWidget3.setItem(x, 2, QTableWidgetItem(self.values[x]))
            self.tableWidget3.setEditTriggers(QTableWidget.NoEditTriggers)
            self.tableWidget3.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.tab1.layout.addWidget(self.tableWidget3)
            self.tab1.setLayout(self.tab1.layout)

class Dialog(QDialog):
    def __init__(self):
        super(Dialog, self).__init__()
        loadUi('dialog.ui', self)
        #self.profile_file_line_edit.setText(UI.filename)
        #self.plan_file_line_edit.clicked.connect(self.open_file)
        #self.generate_rules_button.clicked.connect(self.generate_rules)

    def open_file(self):
        self.filename = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\', "PLAN files (*plan)")
        self.plan_file_line_edit.setText(self.filename[0])

    def generate_rules(self):
        if not UI.profiles:
            QMessageBox.critical(self, "File not selected", "You don't have selected any profile file.")
            return
        files = ['expressions.common.templates', 'expressions.usc.templates', 'regex.common.templates']
        rules_templates = UI.xml_file_manager.read_rules_expressions_advanced(files)
        rules_manager = RulesManager()
        for profile in UI.profiles:
            rules_manager.generate_date_rules(profile, self.filename[0])
            rules_manager.generate_ssn_rules(profile, self.filename[0])
            rules_manager.generate_fiscal_code_rules(profile, self.filename[0])
            rules_manager.generate_len_number_rules(profile, self.filename[0])
            rules_manager.generate_email_rules(profile, self.filename[0])
            rules_manager.generate_iban_rules(profile, self.filename[0])
            rules_manager.generate_ipv4_rules(profile, self.filename[0])
            rules_manager.generate_phone_rules(profile, self.filename[0])
        UI.open_stuff(self.filename[0])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UI()
    window.setWindowTitle('DQ Analyzer Rules Generator')
    window.show()
    sys.exit(app.exec_())
