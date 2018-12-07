from RulesManager import RulesManager
from XMLFileManager import XMLFileManager
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QFileDialog, QMainWindow, QWidget, QVBoxLayout, \
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QLabel, QFormLayout, QLineEdit
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage, QFont
from MongoDBManager import MongoDBManager
import sys
import subprocess
import os

class ManageRulesUI(QDialog):
    def __init__(self):
        super(ManageRulesUI, self).__init__()
        loadUi('manage_rules.ui', self)
        self.mongo_db_manager = MongoDBManager()
        self.rules_collection = self.mongo_db_manager.find_all_docs()

    def create_table(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(self.rules_collection.count())
        self.tableWidget.setColumnCount(4)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderLabels(["Rule Name", "Rule Description", "Rule Pattern", "Rule Expression Template"])
        self.rule_names = []
        self.rule_descriptions = []
        self.rule_patterns = []
        self.rule_expression_templates = []
        for rule in self.rules_collection:
            self.rule_names.append(rule['name'])
            self.rule_descriptions.append(rule['description'])
            self.rule_patterns.append(rule['pattern'])
            self.rule_expression_templates.append(rule['expression'])
        for x in range(0, self.rules_collection.count()):
            self.tableWidget.setItem(x, 0, QTableWidgetItem(self.rule_names[x]))
        for x in range(0, self.rules_collection.count()):
            self.tableWidget.setItem(x, 1, QTableWidgetItem(self.rule_descriptions[x]))
        for x in range(0, self.rules_collection.count()):
            self.tableWidget.setItem(x, 2, QTableWidgetItem(self.rule_patterns[x]))
        for x in range(0, self.rules_collection.count()):
            self.tableWidget.setItem(x, 3, QTableWidgetItem(self.rule_expression_templates[x]))
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.label = QLabel()
        self.label.setText("Business Rules Repository")
        myFont = QFont()
        myFont.setBold(True)
        self.label.setFont(myFont)


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        loadUi('dq_analyzer_rules_generator.ui', self)
        self.xml_file_manager = XMLFileManager()
        self.profiles = None
        self.tabs = self.tabWidget
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.action_load_profile_file.triggered.connect(self.load_profile_file)
        self.action_generate_rules.setEnabled(False)
        self.action_generate_rules.triggered.connect(self.generate_rules)
        self.action_manage_rules_repository.triggered.connect(self.manage_rules)

    def manage_rules(self):
        manage_rules_ui = ManageRulesUI()
        manage_rules_ui.setWindowTitle('DQ Analyzer Rules Generator')
        manage_rules_ui.create_table()
        manage_rules_ui.layout = QVBoxLayout()
        manage_rules_ui.layout.addWidget(manage_rules_ui.label)
        manage_rules_ui.layout.addWidget(manage_rules_ui.tableWidget)
        manage_rules_ui.setLayout(manage_rules_ui.layout)
        manage_rules_ui.show()
        manage_rules_ui.exec_()

    def generate_rules(self):
        index = self.tabs.currentIndex()
        currentTabText = self.tabs.tabText(index)
        dialog = Dialog(self.profiles, self.xml_file_manager, currentTabText)
        dialog.setWindowTitle('DQ Analyzer Rules Generator')
        dialog.show()
        dialog.exec_()

    def load_profile_file(self):
        self.filename = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\', "XML files (*profile.xml)")
        if self.filename[0] is "":
            QMessageBox.critical(self, "File not selected", "You don't have selected any file.")
            return
        self.action_generate_rules.setEnabled(True)
        self.profiles, profiles_in_json = self.xml_file_manager.read_profile(self.filename[0])
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
        myFont = QFont()
        myFont.setBold(True)
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

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        if widget is not None:
            widget.deleteLater()
        self.tabs.removeTab(index)
        #self.tabs.widget(tab).deleteLater()
        if self.tabs.count() == 0:
            self.action_generate_rules.setEnabled(False)

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
    def __init__(self, profiles, xml_file_manager, profile_file):
        super(Dialog, self).__init__()
        loadUi('dialog.ui', self)
        self.profiles = profiles
        self.xml_file_manager = xml_file_manager
        self.profile_file = profile_file
        self.profile_file_text_edit.setPlainText(self.profile_file)
        self.choose_plan_file_button.clicked.connect(self.open_file)
        self.finish_button.clicked.connect(self.create_rules)

    def open_file(self):
        self.plan_file = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\', "PLAN files (*plan)")
        self.plan_file_text_edit.setPlainText(self.plan_file[0])

    def create_rules(self):
        if not self.profiles:
            QMessageBox.critical(self, "File not selected", "You don't have selected any profile file.")
            return
        if self.plan_file_text_edit.toPlainText().lower().endswith(('.plan')):
            self.rules_manager = RulesManager()
            for profile in self.profiles:
                self.rules_manager.generate_rules(profile)
            self.close()
            self.read_rules_in_table()
        else:
            QMessageBox.critical(self, "Plan file not selected", "You don't have selected any plan file.")
            return

    def read_rules_in_table(self):
        table_review = TableReview(self.rules_manager, self.plan_file_text_edit.toPlainText())
        table_review.setWindowTitle('DQ Analyzer Rules Generator')
        table_review.create_table()
        table_review.layout = QVBoxLayout()
        table_review.layout.addWidget(table_review.label)
        table_review.layout.addWidget(table_review.tableWidget)
        table_review.layout.addWidget(table_review.button)
        table_review.setLayout(table_review.layout)
        table_review.show()
        table_review.exec_()

    def open_stuff(self, filename):
        if sys.platform == "win32":
            try:
                os.startfile(filename)
            except:
                QMessageBox.critical(self, "Failed", "File not found.")
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])

class TableReview(QDialog):
    def __init__(self, rules_manager, plan_file):
        super(TableReview, self).__init__()
        loadUi('table_review.ui', self)
        self.rules_manager = rules_manager
        self.plan_file = plan_file

    def create_table(self):
        myFont = QFont()
        myFont.setBold(True)
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(self.rules_manager.generated_rules))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderLabels(["Rule Name", "Rule Description", "Rule Expression"])
        self.rule_names = []
        self.rule_descriptions = []
        self.rule_expressions = []
        for rule in self.rules_manager.generated_rules:
            self.rule_names.append(rule.rule_name)
            self.rule_descriptions.append(rule.rule_description)
            self.rule_expressions.append(rule.rule_expression)
        for x in range(0, len(self.rules_manager.generated_rules)):
            self.tableWidget.setItem(x, 0, QTableWidgetItem(self.rule_names[x]))
        for x in range(0, len(self.rules_manager.generated_rules)):
            self.tableWidget.setItem(x, 1, QTableWidgetItem(self.rule_descriptions[x]))
        for x in range(0, len(self.rules_manager.generated_rules)):
            self.tableWidget.setItem(x, 2, QTableWidgetItem(self.rule_expressions[x]))
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.label = QLabel()
        self.label.setText("Business Rules")
        self.label.setFont(myFont)
        self.button = QPushButton()
        self.button.setText("Write on plan file")
        self.button.clicked.connect(self.write_rules_on_file)

    def write_rules_on_file(self):
        for rule in self.rules_manager.generated_rules:
            self.rules_manager.write_rule(self.plan_file, rule.rule_name, rule.rule_expression)


if __name__ == '__main__':
    xml_file_manager = XMLFileManager()
    rules_templates = xml_file_manager.read_rules_expressions_advanced('dictionary.templates')
    app = QApplication(sys.argv)
    window = UI()
    window.setWindowTitle('DQ Analyzer Rules Generator')
    window.show()
    sys.exit(app.exec_())
