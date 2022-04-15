import os
import re
import sys
import traceback
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import (QGuiApplication,
                           QTextCursor)
from PySide2.QtWidgets import (QApplication,
                               QMessageBox)
from PySide2.QtCore import QFile, QIODevice


class MainWindow:

    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.ui_path = os.path.join(self.BASE_DIR, 'ui', 'main_window.ui')
        self.ui = self._load_ui_file(self.ui_path)
        self.document_path = os.path.join(self.BASE_DIR,
                                          'ui', 're_document.ui')
        self.document_ui = self._load_ui_file(self.document_path)
        method = self.ui.comboBox.currentText()
        if method not in ('sub', 'subn'):
            self.ui.frame.hide()
        self.ui.textEditInputText.setFocus()
        self.ui.pushButtonClear.clicked.connect(self.clear)
        self.ui.pushButtonCopy.clicked.connect(self.copy)
        self.ui.pushButtonRun.clicked.connect(self.run)
        self.ui.actionRegex_document.triggered.connect(self.show_document)
        self.ui.comboBox.currentIndexChanged.connect(self.combobox_changed)
        self.copy_message = None

    def clear(self):
        self.copy_message = None
        self.ui.checkBoxA.setChecked(False)
        self.ui.checkBoxI.setChecked(False)
        self.ui.checkBoxL.setChecked(False)
        self.ui.checkBoxM.setChecked(False)
        self.ui.checkBoxS.setChecked(False)
        self.ui.checkBoxX.setChecked(False)
        self.ui.checkBoxU.setChecked(False)
        self.ui.textEditInputText.clear()
        self.ui.lineEditPattern.clear()
        self.ui.textEditResult.clear()
        self.ui.lineEditReplaceText.clear()
        self.ui.statusBar().clearMessage()
        self.ui.textEditInputText.setFocus()

    def combobox_changed(self):
        self.copy_message = None
        self.ui.statusBar().clearMessage()
        method = self.ui.comboBox.currentText()
        if method in ('sub', 'subn'):
            self.ui.frame.show()
        else:
            self.ui.frame.hide()

    def copy(self):
        pattern = self.ui.lineEditPattern.text()
        if self.copy_message is None:
            QMessageBox.about(self.ui, '提示', '该功能需要运行run之后才能使用')
        else:
            QGuiApplication.clipboard().setText(self.copy_message)
            QMessageBox.about(self.ui, '提示', f'{self.copy_message}\n已复制到剪切板')

    def show_document(self):
        message = re.__doc__
        self.document_ui.textEdit.insertPlainText(message)
        self.document_ui.textEdit.moveCursor(QTextCursor.Start)
        self.document_ui.show()

    def run(self):
        self.ui.textEditResult.clear()
        self.ui.statusBar().clearMessage()
        method = self.ui.comboBox.currentText()
        pattern = self.ui.lineEditPattern.text()
        params = self._get_checked_box()
        text = self.ui.textEditInputText.toPlainText()
        if not text:
            QMessageBox.critical(self.ui, '错误', 'Input Text 不能为空。')
            self.ui.textEditInputText.setFocus()
            return
        if not pattern:
            QMessageBox.critical(self.ui, '错误', 'Pattern 不能为空。')
            self.ui.lineEditPattern.setFocus()
            return
        if not params:
            flags = 0
        else:
            flags = '|'.join(params)
        command_pattern = self._get_command(pattern)
        command_text = self._get_command(text)
        if command_pattern is None:
            self._show_wrapper_error('Pattern')
            return
        if command_text is None:
            self._show_wrapper_error('Input Text')
            return
        if method in ('sub', 'subn'):
            replace_text = self.ui.lineEditReplaceText.text()
            command_replace_text = self._get_command(replace_text)
            if command_replace_text is None:
                self._show_wrapper_error('Replace Text')
                return
            command = f"re.{method}({command_pattern}, {command_replace_text}, {command_text}, flags={flags})"
        else:
            command = f"re.{method}({command_pattern}, {command_text}, flags={flags})"
        command = re.sub(r'\, flags\=0\)$', r')', command)
        self.copy_message = command
        try:
            result = eval(command)
            message = str(result)
            if method == 'findall':
                status_message = f'{len(result)} matches'
                self.ui.statusBar().showMessage(status_message)
        except:
            message = traceback.format_exc()
        self.ui.textEditResult.insertPlainText(message)

    def _get_checked_box(self):
        checked = []
        if self.ui.checkBoxA.isChecked():
            checked.append('re.A')
        if self.ui.checkBoxI.isChecked():
            checked.append('re.I')
        if self.ui.checkBoxL.isChecked():
            checked.append('re.L')
        if self.ui.checkBoxM.isChecked():
            checked.append('re.M')
        if self.ui.checkBoxS.isChecked():
            checked.append('re.S')
        if self.ui.checkBoxX.isChecked():
            checked.append('re.X')
        if self.ui.checkBoxU.isChecked():
            checked.append('re.U')
        return checked

    def _get_command(self, text):

        flag = self._get_string_wrapper(text)
        if flag:
            return f"r{flag}{text}{flag}"
        else:
            return None

    def _get_string_wrapper(self, text):
        if '\n' not in text:
            for flag in ("'", '"'):
                if flag not in text:
                    return flag
        if "'''" not in text:
            if not text.endswith("'"):
                return "'''"
        if '"""' not in text:
            if not text.endswith('"'):
                return '"""'
        return None

    def _load_ui_file(self, ui_path):
        """Load ui file return a pyside object.
        """
        ui_file = QFile(ui_path)
        loader = QUiLoader()
        window = loader.load(ui_file)
        ui_file.close()
        return window

    def _show_wrapper_error(self, text):
        flags = ["'", '"', "'''", '"""']
        message = f'{text} 中含有全四种字符串类型\n' + \
            '\'\t\"\t\'\'\'\t\"\"\"\n' + \
            '请用反斜杠转义掉[\'\'\',\"\"\"]中一种再运行程序。'
        QMessageBox.critical(self.ui, '错误', message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.ui.show()
    sys.exit(app.exec_())
