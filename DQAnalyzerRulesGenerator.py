from RulesManager import RulesManager
from XMLFileManager import XMLFileManager
import sys
from PyQt5 import QtWidgets

xml_file_manager = XMLFileManager()
profiles, profiles_in_json = xml_file_manager.read_profile('1.2 Advanced.profile.xml')
files = ['expressions.common.templates', 'expressions.usc.templates', 'regex.common.templates']
rules_templates = xml_file_manager.read_rules_expressions_advanced(files)
rules_manager = RulesManager()
'''for profile in profiles:
    rules_manager.generate_date_rules(profile)
    rules_manager.generate_ssn_rules(profile)
    rules_manager.generate_fiscal_code_rules(profile)
    rules_manager.generate_len_number_rules(profile)
    rules_manager.generate_email_rules(profile)
    rules_manager.generate_iban_rules(profile)
    rules_manager.generate_ipv4_rules(profile)
    rules_manager.generate_phone_rules(profile)'''

def window():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    b = QtWidgets.QLabel(w)
    b.setText("Hello World!")
    w.setGeometry(100, 100, 200, 50)
    b.move(50, 20)
    w.setWindowTitle("PyQt")
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    window()