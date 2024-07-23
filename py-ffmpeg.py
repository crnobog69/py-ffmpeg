import os
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QLabel, QLineEdit, QComboBox, QProgressBar,
                             QMessageBox, QTabWidget, QInputDialog, QDialog)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QProcess, Qt, QTranslator, QLibraryInfo, QLocale, QUrl
from PyQt5.QtGui import QDesktopServices

class FFmpegGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.translator = QTranslator()
        self.setWindowIcon(QIcon('ikonica.png'))
        self.process = None
        self.duration = 0
        self.input_file = ''
        self.output_file = ''
        self.formats = {
            'Video': ['mp4', 'avi', 'mkv', 'mov', 'flv', 'webm', 'wmv', 'mpeg', 'm4v', '3gp', 'vob', 'ts', 'mts', 'divx', 'asf'],
            'Audio': ['mp3', 'wav', 'ogg', 'aac', 'flac', 'm4a', 'wma', 'ac3', 'aiff', 'au', 'amr', 'ape', 'opus'],
            'Image': ['jpg', 'png', 'gif', 'bmp', 'tiff', 'webp'],
            'Other': ['swf', 'raw']
        }
        self.language_file = 'settings.txt'
        self.initUI()
        self.loadLanguageSetting()

    def initUI(self):
        self.setWindowTitle(self.tr('PyFFmpeg | English'))
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

        # Input file selection
        input_layout = QVBoxLayout()
        self.input_label = QLabel(self.tr('Select a file:'), self)
        input_sub_layout = QHBoxLayout()
        self.input = QLineEdit(self)
        self.browse_input_button = QPushButton(self.tr('Browse'), self)
        self.browse_input_button.clicked.connect(self.showInputDialog)
        input_sub_layout.addWidget(self.input)
        input_sub_layout.addWidget(self.browse_input_button)
        input_layout.addWidget(self.input_label)
        input_layout.addLayout(input_sub_layout)
        layout.addLayout(input_layout)

        # Output file selection
        output_layout = QVBoxLayout()
        self.output_label = QLabel(self.tr('Save converted file as:'), self)
        output_sub_layout = QHBoxLayout()
        self.output = QLineEdit(self)
        self.browse_output_button = QPushButton(self.tr('Browse'), self)
        self.browse_output_button.clicked.connect(self.showOutputDialog)
        output_sub_layout.addWidget(self.output)
        output_sub_layout.addWidget(self.browse_output_button)
        output_layout.addWidget(self.output_label)
        output_layout.addLayout(output_sub_layout)
        layout.addLayout(output_layout)

        # Output format selection
        format_layout = QVBoxLayout()
        self.format_label = QLabel(self.tr('Select output format:'), self)
        self.format_tab_widget = QTabWidget(self)
        self.populateFormatTabs()
        format_layout.addWidget(self.format_label)
        format_layout.addWidget(self.format_tab_widget)
        layout.addLayout(format_layout)

        # Convert button
        self.convert_button = QPushButton(self.tr('Convert'), self)
        self.convert_button.setFixedSize(100, 30)  # Set a fixed size for the Convert button
        self.convert_button.clicked.connect(self.convertVideo)
        layout.addWidget(self.convert_button)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel(self.tr('Ready'), self)
        layout.addWidget(self.status_label)

        # Language and About buttons layout
        button_layout = QHBoxLayout()
        self.about_button = QPushButton(self.tr('About'), self)
        self.about_button.clicked.connect(self.showAboutDialog)
        self.about_button.setFixedHeight(30)  # Set height for the About button
        self.language_button = QPushButton(self.tr('Change Language'), self)
        self.language_button.clicked.connect(self.changeLanguage)
        self.language_button.setFixedHeight(30)  # Set height for the Change Language button
        button_layout.addWidget(self.about_button)
        button_layout.addWidget(self.language_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.show()

    def populateFormatTabs(self):
        tab_labels = {
            'Video': self.tr('Video'),
            'Audio': self.tr('Audio'),
            'Image': self.tr('Image'),
            'Other': self.tr('Other'),
        }
        for category, formats in self.formats.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            combobox = QComboBox(tab)
            for fmt in formats:
                combobox.addItem(fmt)
            combobox.currentIndexChanged.connect(self.updateOutputExtension)
            tab_layout.addWidget(combobox)
            tab.setLayout(tab_layout)
            self.format_tab_widget.addTab(tab, tab_labels[category])
        self.format_tab_widget.currentChanged.connect(self.updateOutputExtension)

    def showInputDialog(self):
        fname, _ = QFileDialog.getOpenFileName(self, self.tr('Open file'), os.path.expanduser('~'))
        if fname:
            self.input_file = fname
            self.input.setText(fname)
            self.updateOutputPath()

    def showOutputDialog(self):
        default_name = self.generateUniqueOutputName()
        default_ext = self.getCurrentFormat()
        default_path = os.path.join(os.path.dirname(self.input_file), f"{default_name}.{default_ext}")
        fname, _ = QFileDialog.getSaveFileName(self, self.tr('Save file'), default_path, f"*.{default_ext}")
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
        base_name = input_name + "_converted"
        counter = 1
        while os.path.exists(os.path.join(output_dir, f"{base_name}.{self.getCurrentFormat()}")):
            base_name = f"{input_name}_converted_{counter}"
            counter += 1
        return base_name

    def updateOutputExtension(self):
        self.updateOutputPath()

    def convertVideo(self):
        if not self.input_file:
            QMessageBox.warning(self, self.tr('Error'), self.tr('Please select an input file.'))
            return

        if not self.output_file:
            QMessageBox.warning(self, self.tr('Error'), self.tr('Please specify an output file.'))
            return

        if os.path.exists(self.output_file):
            reply = QMessageBox.question(self, self.tr('File exists'),
                                         self.tr('The output file already exists. Do you want to overwrite it?'),
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return

        self.status_label.setText(self.tr('Converting...'))
        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)

        self.process = QProcess(self)
        self.process.finished.connect(self.onConversionFinished)
        self.process.readyReadStandardError.connect(self.updateProgress)
        self.process.start("ffmpeg", ["-i", self.input_file, self.output_file])

    def updateProgress(self):
        data = self.process.readAllStandardError().data().decode()
        if "Duration: " in data:
            duration_str = data.split("Duration: ")[1].split(",")[0].strip()
            h, m, s = map(float, duration_str.split(":"))
            self.duration = int(h * 3600 + m * 60 + s)

        if "time=" in data and self.duration > 0:
            time_str = data.split("time=")[1].split(" ")[0].strip()

            # Check if time_str is not 'N/A' before proceeding
            if time_str != 'N/A':
                h, m, s = map(float, time_str.split(":"))
                current_time = int(h * 3600 + m * 60 + s)
                progress = int((current_time / self.duration) * 100)
                self.progress_bar.setValue(progress)

    def parseCurrentTime(self, line):
        import re
        match = re.search(r"time=(\d+):(\d+):(\d+)", line)
        if match:
            hours, minutes, seconds = map(int, match.groups())
            return hours * 3600 + minutes * 60 + seconds
        return 0

    def onConversionFinished(self):
        self.status_label.setText(self.tr('Conversion completed!'))
        self.convert_button.setEnabled(True)
        self.progress_bar.setValue(100)
        self.process = None

    def showAboutDialog(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle(self.tr('About PyFFmpeg'))

        about_layout = QVBoxLayout()
        about_label = QLabel(self.tr(
            '<h1>PyFFmpeg</h1>'
            '<p>Version 0.0.0.4</p>'
            '<p>A simple FFmpeg GUI built with PyQt5.</p>'
            '<p>Made by Црнобог | Crnobog</p>'
        ))
        about_label.setAlignment(Qt.AlignCenter)

        image_label = QLabel(self)
        image_label.setPixmap(QPixmap("ikonica.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        image_label.setAlignment(Qt.AlignCenter)

        github_link = QLabel(self)
        github_link.setText('')
        github_link.setOpenExternalLinks(True)
        github_link.setAlignment(Qt.AlignCenter)

        button_layout = QHBoxLayout()
        github_button = QPushButton(self.tr('GitHub'))
        github_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl('https://github.com/crnobog69/py-ffmpeg/')))
        close_button = QPushButton(self.tr('Close'))
        close_button.clicked.connect(about_dialog.accept)
        button_layout.addWidget(github_button)
        button_layout.addWidget(close_button)

        about_layout.addWidget(image_label)
        about_layout.addWidget(about_label)
        about_layout.addWidget(github_link)
        about_layout.addLayout(button_layout)

        about_dialog.setLayout(about_layout)
        about_dialog.exec_()

    def saveLanguageSetting(self, language):
        with open(self.language_file, 'w') as file:
            file.write(language)

    def loadLanguageSetting(self):
        try:
            with open(self.language_file, 'r') as file:
                language = file.read().strip()
                self.switchTranslator(language)
        except FileNotFoundError:
            self.switchTranslator('en')

    def switchTranslator(self, language):
        if language == 'en':
            self.translator.load(QLibraryInfo.location(QLibraryInfo.TranslationsPath))
        elif language == 'ja':
            self.translator.load('translations/ja.qm')
        elif language == 'sr':
            self.translator.load('translations/sr.qm')
        elif language == 'ru':
            self.translator.load('translations/ru.qm')
        elif language == 'es':
            self.translator.load('translations/es.qm')
        elif language == 'fr':
            self.translator.load('translations/fr.qm')
        elif language == 'de':
            self.translator.load('translations/de.qm')
        elif language == 'it':
            self.translator.load('translations/it.qm')
        elif language == 'kz':
            self.translator.load('translations/kz.qm')
        QApplication.instance().installTranslator(self.translator)
        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(self.tr('PyFFmpeg | English'))
        self.input_label.setText(self.tr('Select a file:'))
        self.browse_input_button.setText(self.tr('Browse'))
        self.output_label.setText(self.tr('Save converted file as:'))
        self.browse_output_button.setText(self.tr('Browse'))
        self.format_label.setText(self.tr('Select output format:'))
        self.convert_button.setText(self.tr('Convert'))
        self.status_label.setText(self.tr('Ready'))
        self.about_button.setText(self.tr('About'))
        self.language_button.setText(self.tr('Change Language'))

        # Update the format tab labels
        tab_labels = {
            'Video': self.tr('Video'),
            'Audio': self.tr('Audio'),
            'Image': self.tr('Image'),
            'Other': self.tr('Other'),
        }
        for index in range(self.format_tab_widget.count()):
            category = list(self.formats.keys())[index]
            self.format_tab_widget.setTabText(index, tab_labels[category])

    def changeLanguage(self):
        languages = ['English (EN)', '日本語 (JP)', 'Српски (SR)', 'Русский (RU)', 'Español (ES)', 'Français (FR)', 'Deutsch (DE)', 'Italiano (IT)', 'Қазақша (KZ)']
        current_language = 'English (EN)'
        language, ok = QInputDialog.getItem(self, self.tr('Select Language'), self.tr('Language:'), languages, languages.index(current_language), False)
        if ok and language:
            if language == 'English (EN)':
                self.saveLanguageSetting('en')
                self.switchTranslator('en')
            elif language == '日本語 (JP)':
                self.saveLanguageSetting('ja')
                self.switchTranslator('ja')
            elif language == 'Српски (SR)':
                self.saveLanguageSetting('sr')
                self.switchTranslator('sr')
            elif language == 'Русский (RU)':
                self.saveLanguageSetting('ru')
                self.switchTranslator('ru')
            elif language == 'Español (ES)':
                self.saveLanguageSetting('es')
                self.switchTranslator('es')
            elif language == 'Français (FR)':
                self.saveLanguageSetting('fr')
                self.switchTranslator('fr')
            elif language == 'Deutsch (DE)':
                self.saveLanguageSetting('de')
                self.switchTranslator('de')
            elif language == 'Italiano (IT)':
                self.saveLanguageSetting('it')
                self.switchTranslator('it')
            elif language == 'Қазақша (KZ)':
                self.saveLanguageSetting('kz')
                self.switchTranslator('kz')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    translator = QTranslator()
    locale = QLocale.system().name()
    qt_translator = QTranslator()
    qt_translator.load("qt_" + locale, QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qt_translator)
    gui = FFmpegGUI()
    gui.show()
    sys.exit(app.exec_())
