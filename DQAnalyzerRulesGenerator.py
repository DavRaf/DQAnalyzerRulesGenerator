from RulesManager import RulesManager
from XMLFileManager import XMLFileManager
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox, QFileDialog, QMainWindow, QWidget, QVBoxLayout, \
    QPushButton, QTableWidget, QTableWidgetItem, QAbstractItemView, QLabel, QFormLayout, QLineEdit, qApp, QTabWidget, \
    QToolButton, QMenu, QWidgetAction, QFrame, QAbstractScrollArea, QHeaderView
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon, QPalette, QColor, QBrush
from PyQt5.QtCore import Qt
from MongoDBManager import MongoDBManager
from string import Template
from xml.dom import minidom
import html
import sys
import subprocess
import os
import re

class DisplayRulesUI(QDialog):
    def __init__(self):
        super(DisplayRulesUI, self).__init__()
        loadUi('display_rules.ui', self)
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
        self.action_display_rules_repository.triggered.connect(self.manage_rules)

    def manage_rules(self):
        manage_rules_ui = DisplayRulesUI()
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
        self.tableWidget.setColumnCount(14)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderLabels(["Expression", "Type", "Domain", "Non-null", "Null", "Unique", "Non Unique", "Distinct", "Duplicate", "Min", "Median", "Max", "", ""])
        self.expressions = []
        self.expression_types = []
        self.expression_domains = []
        self.non_nulls = []
        self.nulls = []
        self.uniques = []
        self.non_uniques = []
        self.distincts = []
        self.duplicates = []
        self.mins = []
        self.medians = []
        self.maxs = []
        for profile in self.profiles:
            self.expressions.append(profile.expression_name)
            self.expression_types.append(profile.expression_type)
            self.expression_domains.append(profile.domain_name)
            for stat in profile.statistics:
                if stat.type == 'count_nulls':
                    self.nulls.append(stat.value)
                elif stat.type == 'count_not_nulls':
                    self.non_nulls.append(stat.value)
                elif stat.type == 'unique':
                    self.uniques.append(stat.value)
                elif stat.type == 'non_unique':
                    self.non_uniques.append(stat.value)
                elif stat.type == 'distinct':
                    self.distincts.append(stat.value)
                elif stat.type == 'duplicate':
                    self.duplicates.append(stat.value)
                elif stat.type == 'min':
                    self.mins.append(stat.value)
                elif stat.type == 'median':
                    self.medians.append(stat.value)
                elif stat.type == 'max':
                    self.maxs.append(stat.value)
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 0, QTableWidgetItem(self.expressions[x]))
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 1, QTableWidgetItem(self.expression_types[x]))
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 2, QTableWidgetItem(self.expression_domains[x]))
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 3, QTableWidgetItem(self.non_nulls[x]))
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 4, QTableWidgetItem(self.nulls[x]))
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 5, QTableWidgetItem(self.uniques[x]))
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 6, QTableWidgetItem(self.non_uniques[x]))
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 7, QTableWidgetItem(self.distincts[x]))
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 8, QTableWidgetItem(self.duplicates[x]))
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 9, QTableWidgetItem(self.mins[x]))
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 10, QTableWidgetItem(self.medians[x]))
        for x in range(0, len(self.profiles)):
            self.tableWidget.setItem(x, 11, QTableWidgetItem(self.maxs[x]))
        for x in range(0, len(self.profiles)):
            self.display_domain_analysis_btn = QPushButton()
            self.display_domain_analysis_btn.setText("Display Domain Analysis")
            self.display_domain_analysis_btn.clicked.connect(self.display_domain_analysis)
            self.tableWidget.setCellWidget(x, 12, self.display_domain_analysis_btn)
        for x in range(0, len(self.profiles)):
            self.display_mask_analysis_btn = QPushButton()
            self.display_mask_analysis_btn.setText("Display Mask Analysis")
            self.display_mask_analysis_btn.clicked.connect(self.display_mask_analysis)
            self.tableWidget.setCellWidget(x, 13, self.display_mask_analysis_btn)
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.resizeColumnsToContents()
        myFont = QFont()
        myFont.setBold(True)
        self.label1 = QLabel()
        self.label1.setText("Column Analyses")
        self.label1.setFont(myFont)
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.addWidget(self.label1)
        self.tab1.layout.addWidget(self.tableWidget)
        self.tab1.setLayout(self.tab1.layout)

    def display_domain_analysis(self):
        button = qApp.focusWidget()
        index = self.tableWidget.indexAt(button.pos())
        expression_name = self.tableWidget.item(index.row(), 0).text()
        current_profile = None
        for profile in self.profiles:
            if profile.expression_name == expression_name:
                current_profile = profile
        if current_profile.domain_analysis:
            domain_analysis_ui = DomainAnalysisUI()
            domain_analysis_ui.setWindowTitle('DQ Analyzer Rules Generator')
            domain_analysis_ui.create_table(current_profile)
            domain_analysis_ui.layout = QVBoxLayout()
            domain_analysis_ui.layout.addWidget(domain_analysis_ui.label)
            domain_analysis_ui.layout.addWidget(domain_analysis_ui.tableWidget)
            domain_analysis_ui.setLayout(domain_analysis_ui.layout)
            domain_analysis_ui.show()
            domain_analysis_ui.exec_()
        else:
            QMessageBox.critical(self, "No domain analysis available", "There not exist a domain analysis for the given field.")


    def display_mask_analysis(self):
        button = qApp.focusWidget()
        index = self.tableWidget.indexAt(button.pos())
        expression_name = self.tableWidget.item(index.row(), 0).text()
        current_profile = None
        for profile in self.profiles:
            if profile.expression_name == expression_name:
                current_profile = profile
        if current_profile.mask_analysis:
            mask_analysis_ui = MaskAnalysisUI()
            mask_analysis_ui.setWindowTitle('DQ Analyzer Rules Generator')
            mask_analysis_ui.create_table(current_profile)
            mask_analysis_ui.layout = QVBoxLayout()
            mask_analysis_ui.layout.addWidget(mask_analysis_ui.label)
            mask_analysis_ui.layout.addWidget(mask_analysis_ui.tableWidget)
            mask_analysis_ui.setLayout(mask_analysis_ui.layout)
            mask_analysis_ui.show()
            mask_analysis_ui.exec_()
        else:
            QMessageBox.critical(self, "No mask analysis available", "There not exist a mask analysis for the given field.")

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        if widget is not None:
            widget.deleteLater()
        self.tabs.removeTab(index)
        #self.tabs.widget(tab).deleteLater()
        if self.tabs.count() == 0:
            self.action_generate_rules.setEnabled(False)

class DomainAnalysisUI(QDialog):
    def __init__(self):
        super(DomainAnalysisUI, self).__init__()
        loadUi('domain_analysis_ui.ui', self)

    def create_table(self, current_profile):
        myFont = QFont()
        myFont.setBold(True)
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(current_profile.domain_analysis))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderLabels(["Num Cases", "Value"])
        self.values = []
        self.num_cases_list = []
        for d_a in current_profile.domain_analysis:
            self.num_cases_list.append(d_a.num_cases)
            if not d_a.value:
                self.values.append("NULL")
            else:
                self.values.append(d_a.value)
        for x in range(0, len(current_profile.domain_analysis)):
            self.tableWidget.setItem(x, 0, QTableWidgetItem(str(self.num_cases_list[x])))
        for x in range(0, len(current_profile.domain_analysis)):
            self.tableWidget.setItem(x, 1, QTableWidgetItem(self.values[x]))
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.resizeColumnsToContents()
        self.label = QLabel()
        self.label.setText("Domain Analysis")
        self.label.setFont(myFont)

class MaskAnalysisUI(QDialog):
    def __init__(self):
        super(MaskAnalysisUI, self).__init__()
        loadUi('mask_analysis_ui.ui', self)

    def create_table(self, current_profile):
        myFont = QFont()
        myFont.setBold(True)
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(current_profile.mask_analysis))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderLabels(["Count", "Percentage", "Value"])
        self.values = []
        self.counts = []
        self.percents = []
        for m_a in current_profile.mask_analysis:
            if not m_a.value:
                self.values.append("NULL")
            else:
                self.values.append(m_a.value)
            self.counts.append(m_a.count)
            self.percents.append(m_a.percentage)
        for x in range(0, len(current_profile.mask_analysis)):
            self.tableWidget.setItem(x, 0, QTableWidgetItem(str(self.counts[x])))
        for x in range(0, len(current_profile.mask_analysis)):
            self.tableWidget.setItem(x, 1, QTableWidgetItem(str(self.percents[x])))
        for x in range(0, len(current_profile.mask_analysis)):
            self.tableWidget.setItem(x, 2, QTableWidgetItem(self.values[x]))
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.tableWidget.resizeColumnsToContents()
        self.label = QLabel()
        self.label.setText("Mask Analysis")
        self.label.setFont(myFont)

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
        self.cancel_button.clicked.connect(self.close_dialog)

    def close_dialog(self):
        self.close()

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
                self.rules_manager.generate_rules(profile, self.plan_file_text_edit.toPlainText())
            self.close()
            self.read_rules_in_table()
        else:
            QMessageBox.critical(self, "Plan file not selected", "You don't have selected any plan file.")
            return

    def read_rules_in_table(self):
        table_review = TableReview(self.rules_manager, self.plan_file_text_edit.toPlainText())
        table_review.setWindowTitle('DQ Analyzer Rules Generator')
        table_review.create_table_for_generated_rules()
        table_review.create_table_for_new_detected_patterns()
        table_review.layout = QVBoxLayout()
        tabs = QTabWidget()
        tab1 = QWidget()
        tab2 = QWidget()
        tabs.addTab(tab1, "Generated Rules")
        tabs.addTab(tab2, "New Detected Patterns")
        tab1.layout = QVBoxLayout()
        if self.rules_manager.generated_rules:
            tab1.layout.addWidget(table_review.label)
            tab1.layout.addWidget(table_review.tableWidget)
        else:
            tab1.layout.addWidget(table_review.label3)
        tab1.setLayout(tab1.layout)
        tab2.layout = QVBoxLayout()
        if self.rules_manager.new_detected_patterns:
            tab2.layout.addWidget(table_review.label2)
            tab2.layout.addWidget(table_review.tableWidget2)
        else:
            tab1.layout.addWidget(table_review.label4)
        tab2.setLayout(tab2.layout)
        table_review.layout.addWidget(tabs)
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
        self.mongo_db_manager = MongoDBManager()
        self.xml_file_manager = XMLFileManager()
        self.rules_manager = rules_manager
        self.plan_file = plan_file

    def setColortoRow(self, table, rowIndex, color):
        for j in range(table.columnCount() - 1):
            table.item(rowIndex, j).setBackground(color)

    def create_table_for_generated_rules(self):
        myFont = QFont()
        myFont.setBold(True)
        if self.rules_manager.generated_rules:
            self.tableWidget = QTableWidget()
            self.tableWidget.setRowCount(len(self.rules_manager.generated_rules))
            self.tableWidget.setColumnCount(10)
            self.tableWidget.verticalHeader().setVisible(False)
            self.tableWidget.setHorizontalHeaderLabels(["Column Name", "Column Pattern", "Column Pattern Num Cases", "% Column Pattern", "Rule Name", "Rule Description", "Rule Pattern", "Rule Expression", "Is Written", ""])
            self.column_names = []
            self.column_patterns = []
            self.column_patterns_num_cases = []
            self.column_patterns_percentages = []
            self.rule_names = []
            self.rule_descriptions = []
            self.rule_patterns = []
            self.rule_expressions = []
            self.is_written = []
            for rule in self.rules_manager.generated_rules:
                self.column_names.append(rule.column_name)
                self.column_patterns.append(rule.pattern_value)
                self.column_patterns_num_cases.append(rule.pattern_num_cases)
                self.column_patterns_percentages.append(rule.pattern_percent)
                self.rule_names.append(rule.rule_name)
                self.rule_descriptions.append(rule.rule_description)
                self.rule_patterns.append(rule.rule_pattern)
                self.rule_expressions.append(rule.rule_expression)
            written_rules_names, written_rules_expressions = self.xml_file_manager.read_rules_expressions_in_plan_file(self.plan_file)
            for generated_rule in self.rules_manager.generated_rules:
                check_name = False
                for written_rule_name in written_rules_names:
                    if written_rule_name == generated_rule.rule_name:
                        check_name = True
                check_exp = False
                for written_rule_exp in written_rules_expressions:
                    if written_rule_exp == generated_rule.rule_expression:
                        check_exp = True
                if check_name is True and check_exp is True:
                    self.is_written.append(True)
                else:
                    self.is_written.append(False)
            print(self.is_written)
            for x in range(0, len(self.rules_manager.generated_rules)):
                self.tableWidget.setItem(x, 0, QTableWidgetItem(self.column_names[x]))
            for x in range(0, len(self.rules_manager.generated_rules)):
                self.tableWidget.setItem(x, 1, QTableWidgetItem(self.column_patterns[x]))
            for x in range(0, len(self.rules_manager.generated_rules)):
                self.tableWidget.setItem(x, 2, QTableWidgetItem(str(self.column_patterns_num_cases[x])))
            for x in range(0, len(self.rules_manager.generated_rules)):
                self.tableWidget.setItem(x, 3, QTableWidgetItem(str(round(self.column_patterns_percentages[x], 2)) + "%"))
            for x in range(0, len(self.rules_manager.generated_rules)):
                self.tableWidget.setItem(x, 4, QTableWidgetItem(self.rule_names[x]))
            for x in range(0, len(self.rules_manager.generated_rules)):
                self.tableWidget.setItem(x, 5, QTableWidgetItem(self.rule_descriptions[x]))
            for x in range(0, len(self.rules_manager.generated_rules)):
                self.tableWidget.setItem(x, 6, QTableWidgetItem(self.rule_patterns[x]))
            for x in range(0, len(self.rules_manager.generated_rules)):
                self.tableWidget.setItem(x, 7, QTableWidgetItem(self.rule_expressions[x]))
            for x in range(0, len(self.rules_manager.generated_rules)):
                self.tableWidget.setItem(x, 8, QTableWidgetItem(str(self.is_written[x])))
            for x in range(0, len(self.rules_manager.generated_rules)):
                self.btn_write_to_plan_file = QPushButton()
                self.btn_write_to_plan_file.setText("Write to Plan file")
                self.btn_write_to_plan_file.clicked.connect(self.write_rule_on_file)
                self.tableWidget.setCellWidget(x, 9, self.btn_write_to_plan_file)
            self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
            self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.label = QLabel()
            self.label.setText("Generated Rules")
            self.label.setFont(myFont)
            allRows = self.tableWidget.rowCount()
            for row in range(0, allRows):
                is_written = self.tableWidget.item(row, 8).text()
                if is_written == "True":
                    self.setColortoRow(self.tableWidget, row, QColor(125,125,125))
        else:
            self.label3 = QLabel()
            self.label3.setText("No rule has been generated")
            self.label3.setFont(myFont)
            self.label3.setAlignment(Qt.AlignCenter)

    def create_table_for_new_detected_patterns(self):
        myFont = QFont()
        myFont.setBold(True)
        if self.rules_manager.new_detected_patterns:
            self.tableWidget2 = QTableWidget()
            self.tableWidget2.setRowCount(len(self.rules_manager.new_detected_patterns))
            self.tableWidget2.setColumnCount(5)
            self.tableWidget2.verticalHeader().setVisible(False)
            self.tableWidget2.setHorizontalHeaderLabels(["Column Name", "Column Pattern", "Column Pattern Num Cases", "% Column Pattern", ""])
            self.column_names2 = []
            self.column_patterns2 = []
            self.column_patterns_num_cases2 = []
            self.column_patterns_percentages2 = []
            for pattern in self.rules_manager.new_detected_patterns:
                self.column_names2.append(pattern.column_name)
                self.column_patterns2.append(pattern.pattern_value)
                self.column_patterns_num_cases2.append(pattern.pattern_num_cases)
                self.column_patterns_percentages2.append(pattern.pattern_percent)
            for x in range(0, len(self.rules_manager.new_detected_patterns)):
                self.tableWidget2.setItem(x, 0, QTableWidgetItem(self.column_names2[x]))
            for x in range(0, len(self.rules_manager.new_detected_patterns)):
                self.tableWidget2.setItem(x, 1, QTableWidgetItem(self.column_patterns2[x]))
            for x in range(0, len(self.rules_manager.new_detected_patterns)):
                self.tableWidget2.setItem(x, 2, QTableWidgetItem(str(self.column_patterns_num_cases2[x])))
            for x in range(0, len(self.rules_manager.new_detected_patterns)):
                self.tableWidget2.setItem(x, 3, QTableWidgetItem(str(round(self.column_patterns_percentages2[x], 2)) + "%"))
            for x in range(0, len(self.rules_manager.new_detected_patterns)):
                self.add_to_dict = QPushButton()
                self.add_to_dict.setText("Add to dictionary")
                self.add_to_dict.clicked.connect(self.add_to_dictionary)
                self.tableWidget2.setCellWidget(x, 4, self.add_to_dict)
            self.tableWidget2.setEditTriggers(QTableWidget.NoEditTriggers)
            self.tableWidget2.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.label2 = QLabel()
            self.label2.setText("New Detected Patterns")
            self.label2.setFont(myFont)
        else:
            self.label4 = QLabel()
            self.label4.setText("No new pattern has been detected")
            self.label4.setFont(myFont)
            self.label4.setAlignment(Qt.AlignCenter)

    def write_rule_on_file(self):
        button = qApp.focusWidget()
        index = self.tableWidget.indexAt(button.pos())
        if self.tableWidget.item(index.row(), 8).text() == "True":
            QMessageBox.critical(self, "Rule already present", "The rule you have selected is already present in the plan file.")
            return
        rule_name = self.tableWidget.item(index.row(), 4).text()
        rule_expression = self.tableWidget.item(index.row(), 7).text()
        self.rules_manager.write_rule(self.plan_file, rule_name, rule_expression)
        self.tableWidget.item(index.row(), 8).setText("True")
        self.setColortoRow(self.tableWidget, index.row(), QColor(125, 125, 125))
        #button.setIcon(QIcon('normal.png'))

    def add_to_dictionary(self):
        button = qApp.focusWidget()
        index = self.tableWidget2.indexAt(button.pos())
        name = self.tableWidget2.item(index.row(), 0).text()
        pattern = self.tableWidget2.item(index.row(), 1).text()
        table_review = NewRuleUI(name, pattern, self.rules_manager, self.plan_file)
        table_review.setWindowTitle('DQ Analyzer Rules Generator')
        table_review.show()
        table_review.exec_()

class NewRuleUI(QDialog):
    def __init__(self, name, pattern, rule_manager, plan_file):
        super(NewRuleUI, self).__init__()
        loadUi('new_rule_ui.ui', self)
        self.rule_names = list()
        self.mongo_db_manager = MongoDBManager()
        self.rule_manager = rule_manager
        self.plan_file = plan_file
        self.name = name
        self.pattern = pattern
        rules = self.mongo_db_manager.find_all_docs()
        for rule in rules:
            self.rule_names.append(rule['name'])
        self.rule_names_combo_box.addItems([""] + self.rule_names)
        self.rule_names_combo_box.view().pressed.connect(self.handle_item_pressed)
        #self.rule_names_combo_box.lineEdit().setPlaceholderText("New Rule Name")
        self.pattern_plain_text_edit.setPlainText("^(" + self.pattern + ")$")
        self.pattern_plain_text_edit.setReadOnly(True)
        self.auto_radio_button.setChecked(True)
        self.auto_radio_button.toggled.connect(lambda: self.radio_btn_state(self.auto_radio_button))
        self.manual_radio_button.toggled.connect(lambda: self.radio_btn_state(self.manual_radio_button))
        self.expression_plain_text_edit.setPlainText(self.create_regex_from_pattern())
        self.expression_plain_text_edit.setEnabled(False)
        #self.create_regex_from_pattern()
        #self.finish_button.clicked.connect(self.create_new_rule)
        self.cancel_button.clicked.connect(self.close_dialog)
        menu = QMenu()
        menu.addAction('Write to the dictionary', self.write_to_the_dictionary)
        menu.addAction('Write both to dictionary and plan file', self.write_both_to_dictionary_and_plan_file)
        self.finish_button.setMenu(menu)

    def radio_btn_state(self, radio_btn):
        if radio_btn.text() == "Automatic":
            if radio_btn.isChecked() == True:
                self.expression_plain_text_edit.setEnabled(False)

        if radio_btn.text() == "Manual":
            if radio_btn.isChecked() == True:
                self.expression_plain_text_edit.setEnabled(True)

    def create_regex_from_pattern(self):
        regex_list = list()
        characters = list(self.pattern)
        for c in characters:
            if c == 'L':
                regex_list.append('[a-zA-Z]')
            elif c == 'D':
                regex_list.append('[0-9]')
            elif c == 'W':
                regex_list.append('[a-zA-Z]+')
            elif c == 'N':
                regex_list.append('[0-9]+')
            elif c == ' ':
                regex_list.append('\s')
            elif c == '/':
                regex_list.append('/')
            elif c == '.':
                regex_list.append('\.')
            elif c == '-':
                regex_list.append('-')
            elif c == ':':
                regex_list.append(':')
        regex = "matches(\"^(" + "".join(regex_list) + ")$\", ${value})"
        return regex

    def write_to_the_dictionary(self):
        if self.rule_names_combo_box.currentText() == "" or self.expression_plain_text_edit.toPlainText() == "":
            QMessageBox.critical(self, "Empty Field(s)", "Please enter both rule name and expression.")
            return False
        elif self.check_regex(str(self.expression_plain_text_edit.toPlainText())) is False:
            QMessageBox.critical(self, "Invalid Field", "Please enter a valid regex.")
            return False
        elif self.rule_names_combo_box.currentText() in self.rule_names and self.rule_names_combo_box.isEditable() == True:
            QMessageBox.critical(self, "Duplicate Detected", "The rule name entered is already present into the rule names list. Please select the rule name from the list.")
            return False
        else:
            self.mongo_db_manager.collection.update({"name": self.rule_names_combo_box.currentText()}, {"$set": {
                                                                             "description": self.description_plain_text_edit.toPlainText(),
                                                                             "expression": self.expression_plain_text_edit.toPlainText(),
                                                                             "pattern": self.pattern_plain_text_edit.toPlainText()}}, upsert=True)
            '''for pattern in self.rule_manager.new_detected_patterns:
                if pattern.pattern_value == self.pattern_plain_text_edit.toPlainText():
                    self.rule_manager.new_detected_patterns.remove(pattern)'''
            self.close()
            return True

    def check_regex(self, regex):
        try:
            re.compile(regex)
        except Exception:
            return False
        return True

    def write_both_to_dictionary_and_plan_file(self):
        if self.write_to_the_dictionary():
            rule_expression_template = Template(self.expression_plain_text_edit.toPlainText())
            rule_expression = rule_expression_template.safe_substitute(value=self.name)
            self.rule_manager.write_rule(self.plan_file, self.rule_names_combo_box.currentText(), rule_expression)

    '''def create_new_rule(self):
        if self.rule_names_combo_box.currentText() == "" or self.expression_plain_text_edit.toPlainText() == "":
            QMessageBox.critical(self, "Empty Field(s)", "Please enter both rule name and expression.")
        else:
            self.mongo_db_manager.collection.update({"name": self.rule_names_combo_box.currentText()}, {"$set": {
                                                                             "description": self.description_plain_text_edit.toPlainText(),
                                                                             "expression": self.expression_plain_text_edit.toPlainText(),
                                                                             "pattern": self.pattern_plain_text_edit.toPlainText()}}, upsert=True)
            self.close()'''

    def close_dialog(self):
        self.close()

    def handle_item_pressed(self, index):
        rule_name = self.rule_names_combo_box.model().itemFromIndex(index).text()
        if rule_name == "":
            self.rule_names_combo_box.setEditable(True)
            self.description_plain_text_edit.setReadOnly(False)
            self.description_plain_text_edit.setPlainText("")
            self.pattern_plain_text_edit.setPlainText("^(" + self.pattern + ")$")
            self.expression_plain_text_edit.setPlainText("")
        else:
            self.rule_names_combo_box.setEditable(False)
            self.description_plain_text_edit.setReadOnly(True)
            rule = self.mongo_db_manager.find_doc_by_name(rule_name)
            self.description_plain_text_edit.setPlainText(rule["description"])
            index = rule['pattern'].find('$')
            new_pattern = rule['pattern'][:index] + '|(' + self.pattern + ')' + rule['pattern'][index:]
            self.pattern_plain_text_edit.setPlainText(new_pattern)
            self.expression_plain_text_edit.setPlainText(rule["expression"])

def create_palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(100, 149, 237))
    palette.setColor(QPalette.Base, QColor(15, 15, 15))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
    palette.setColor(QPalette.HighlightedText, Qt.black)
    return palette

if __name__ == '__main__':
    xml_file_manager = XMLFileManager()
    #rules_templates = xml_file_manager.read_rules_expressions_advanced('dictionary.templates')
    app = QApplication(sys.argv)
    #QApplication.setPalette(create_palette())
    window = UI()
    window.setWindowTitle('DQ Analyzer Rules Generator')
    window.show()
    sys.exit(app.exec_())
