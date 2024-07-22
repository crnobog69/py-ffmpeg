import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QLabel, QLineEdit, QComboBox, QProgressBar, QMessageBox, QTabWidget)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QProcess, Qt
from PyQt5 import QtGui


class FFmpegGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('ikonica.png'))
        self.process = None
        self.duration = 0
        self.input_file = ''
        self.output_file = ''
        self.formats = {
            'Видео': ['mp4', 'avi', 'mkv', 'mov', 'flv', 'webm', 'wmv', 'mpeg', 'm4v', '3gp', 'vob', 'ts', 'mts', 'divx', 'asf'],
            'Аудио': ['mp3', 'wav', 'ogg', 'aac', 'flac', 'm4a', 'wma', 'ac3', 'aiff', 'au', 'amr', 'ape', 'opus'],
            'Изображение': ['jpg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
            'Другое': ['swf', 'raw']
        }
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PyFFmpeg | Русский')
        self.resize(500, 300)

        self.setStyleSheet("""
                    QWidget {
                        background-color: #1E1E2E;
                        color: #F5E0DC;
                    }
                    QPushButton {
                        background-color: #1E1E2E;
                        color: #F38BA8;
                        border: 1px solid #F38BA8;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #F38BA8;
                        color: #1E1E2E;
                    }
                    QLineEdit {
                        background-color: #1E1E2E;
                        color: #F5E0DC;
                        border: 1px solid #F38BA8;
                        padding: 5px;
                    }
                    QLabel {
                        color: #F38BA8;
                    }
                    QComboBox {
                        background-color: #181825;
                        color: #cdd6f4;
                        border: 1px solid #f38ba8;
                    }
                    QProgressBar {
                        background-color: #1E1E2E;
                        color: #F38BA8;
                        border: 1px solid #F38BA8;
                    }
                    QProgressBar::chunk {
                        background-color: #F38BA8;
                    }
                    QMessageBox {
                        background-color: #1E1E2E;
                        color: #F5E0DC;
                    }
                    QTabWidget::pane {
                        border: 1px solid #F38BA8;
                        background-color: #1E1E2E;
                    }
                    QTabWidget::tab-bar {
                        left: 5px;
                    }
                    QTabBar::tab {
                        background-color: #181825;
                        color: #F5E0DC;
                        border: 1px solid #F38BA8;
                        padding: 5px;
                        margin-right: 2px;
                    }
                    QTabBar::tab:selected, QTabBar::tab:hover {
                        background-color: #F38BA8;
                        color: #1E1E2E;
                    }
                """)

        layout = QVBoxLayout()

        # Выбор входного файла
        input_layout = QHBoxLayout()
        self.input_label = QLabel('Выберите файл:', self)
        self.input = QLineEdit(self)
        self.browse_input_button = QPushButton('Обзор', self)
        self.browse_input_button.clicked.connect(self.showInputDialog)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.browse_input_button)
        layout.addLayout(input_layout)

        # Выбор выходного файла
        output_layout = QHBoxLayout()
        self.output_label = QLabel('Сохранить конвертированный файл как:', self)
        self.output = QLineEdit(self)
        self.browse_output_button = QPushButton('Обзор', self)
        self.browse_output_button.clicked.connect(self.showOutputDialog)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output)
        output_layout.addWidget(self.browse_output_button)
        layout.addLayout(output_layout)

        # Выбор формата вывода
        format_layout = QVBoxLayout()
        self.format_label = QLabel('Выберите выходной формат:', self)
        self.format_tab_widget = QTabWidget(self)
        self.populateFormatTabs()
        format_layout.addWidget(self.format_label)
        format_layout.addWidget(self.format_tab_widget)
        layout.addLayout(format_layout)

        # Кнопка конвертации
        self.convert_button = QPushButton('Конвертировать', self)
        self.convert_button.clicked.connect(self.convertVideo)
        layout.addWidget(self.convert_button)

        # Индикатор прогресса
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Метка статуса
        self.status_label = QLabel('Готово', self)
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.show()

    def populateFormatTabs(self):
        for category, formats in self.formats.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            self.format_combobox = QComboBox(tab)
            for fmt in formats:
                self.format_combobox.addItem(fmt)
            tab_layout.addWidget(self.format_combobox)
            tab.setLayout(tab_layout)
            self.format_tab_widget.addTab(tab, category)
        self.format_tab_widget.currentChanged.connect(self.updateOutputExtension)

    def showInputDialog(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Открыть файл', os.path.expanduser('~'))
        if fname:
            self.input_file = fname
            self.input.setText(fname)
            self.updateOutputPath()

    def showOutputDialog(self):
        default_name = self.generateUniqueOutputName()
        default_ext = self.getCurrentFormat()
        default_path = os.path.join(os.path.dirname(self.input_file), f"{default_name}.{default_ext}")
        fname, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл', default_path, f"*.{default_ext}")
        if fname:
            self.output_file = fname
            self.output.setText(fname)

    def getCurrentFormat(self):
        current_tab = self.format_tab_widget.currentWidget()
        combobox = current_tab.findChild(QComboBox)
        current_format = combobox.currentText()
        return current_format

    def updateOutputPath(self):
        if self.input_file:
            default_name = self.generateUniqueOutputName()
            default_ext = self.getCurrentFormat()
            self.output_file = os.path.join(os.path.dirname(self.input_file), f"{default_name}.{default_ext}")
            self.output.setText(self.output_file)

    def generateUniqueOutputName(self):
        input_name = os.path.splitext(os.path.basename(self.input_file))[0]
        output_dir = os.path.dirname(self.input_file)
        base_name = input_name + "_конвертировано"
        counter = 1
        while os.path.exists(os.path.join(output_dir, f"{base_name}.{self.getCurrentFormat()}")):
            base_name = f"{input_name}_конвертировано_{counter}"
            counter += 1
        return base_name

    def updateOutputExtension(self):
        new_format = self.getCurrentFormat()
        if self.output_file:
            old_ext = os.path.splitext(self.output_file)[1]
            if old_ext.lower() != f".{new_format.lower()}":
                base_name = os.path.splitext(self.output_file)[0]
                new_name = self.generateUniqueOutputName()
                self.output_file = os.path.join(os.path.dirname(base_name), f"{new_name}.{new_format}")
                self.output.setText(self.output_file)

    def convertVideo(self):
        if not self.input_file:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, выберите входной файл.')
            return

        if not self.output_file:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, укажите выходной файл.')
            return

        if os.path.normpath(self.input_file).lower() == os.path.normpath(self.output_file).lower():
            QMessageBox.warning(self, 'Ошибка', 'Входной и выходной файлы не могут быть одинаковыми.')
            return

        input_ext = os.path.splitext(self.input_file)[1][1:].lower()
        output_ext = os.path.splitext(self.output_file)[1][1:].lower()

        input_category = next((cat for cat, formats in self.formats.items() if input_ext in formats), None)
        output_category = next((cat for cat, formats in self.formats.items() if output_ext in formats), None)

        if input_category != output_category:
            warning_msg = (f"Предупреждение: Вы конвертируете из формата {input_category} в формат {output_category}. "
                           f"Это может привести к потере данных или неожиданным результатам. Хотите продолжить?")
            reply = QMessageBox.question(self, 'Предупреждение о формате', warning_msg,
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        command = f"ffmpeg -i \"{self.input_file}\" \"{self.output_file}\""

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.updateProgress)
        self.process.readyReadStandardError.connect(self.updateProgress)
        self.process.finished.connect(self.conversionComplete)

        self.status_label.setText('Конвертация...')
        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)

        self.process.start(command)

    def updateProgress(self):
        output = self.process.readAllStandardError().data().decode()

        if "Duration" in output and self.duration == 0:
            duration_str = output.split("Duration: ")[1].split(",")[0].strip()
            duration_parts = duration_str.split(":")
            self.duration = int(duration_parts[0]) * 3600 + int(duration_parts[1]) * 60 + float(duration_parts[2])

        if "time=" in output:
            time_str = output.split("time=")[1].split(" ")[0].strip()
            time_parts = time_str.split(":")
            current_time = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])
            progress = (current_time / self.duration) * 100 if self.duration > 0 else 0
            self.progress_bar.setValue(int(progress))

    def conversionComplete(self):
        exit_code = self.process.exitCode()
        if exit_code == 0:
            self.status_label.setText('Конвертация завершена!')
            self.progress_bar.setValue(100)
            QMessageBox.information(self, 'Успех', 'Конвертация файла успешно завершена!')
        else:
            self.status_label.setText('Ошибка конвертации!')
            QMessageBox.critical(self, 'Ошибка', 'Ошибка конвертации файла. Пожалуйста, проверьте входной файл и попробуйте снова.')

        self.convert_button.setEnabled(True)
        self.duration = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FFmpegGUI()
    sys.exit(app.exec_())
